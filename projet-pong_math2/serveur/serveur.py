

import sys
import argparse

from _thread import *
from pygame import time as gametime
import time
import json
import random
import select
import socket
from pygame.locals import Rect
from ball import Pong
import constantes as const
import base64
import binascii
from cryptography.fernet import Fernet

rand = binascii.unhexlify(b"eaf57617c2256f260dee04cd84db18c01d59e75a95da8d9eb12c460192ddc1af")
key = base64.urlsafe_b64encode(rand)
f = Fernet(key)

REMOTE_CLIENT = []
REMOTE_PLAYER = []

class Player:

    def __init__(self, player):
        self.id = player
        self.y = int(const.SCREENSIZE[1] * 0.5)
        self.side = player % 2

        self.height = 100
        self.width = 10

        if self.side == 0:
            self.x = const.SCREENSIZE[0] - (5 + (player * 30))
        else:
            self.x = (player * 30) + 5 if player > 1 else 5

        self.rect = Rect(0, self.y-int(self.height*0.5), self.width, self.height)
        self.color = random_color()

    def update(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.rect.center = (self.x, self.y)

    def get_info(self):
        return{
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "side": self.side,
            "color": self.color
        }

def random_color():
    rgb = []
    r = random.randint(0, 255)
    b = random.randint(0, 255)
    g = random.randint(0, 255)
    rgb.append(r)
    rgb.append(b)
    rgb.append(g)
    return tuple(rgb)

def broadcast_all(sock, info):
    global REMOTE_CLIENT

    for socket in REMOTE_CLIENT[1:]:
        if socket != sock:
            try:
                socket.sendall(info)
            except:
                socket.close()
                i = REMOTE_CLIENT(socket)
                p = REMOTE_PLAYER[i-1]
                print("supression de", p.id, "de la liste")
                REMOTE_CLIENT.remove(socket)
                REMOTE_PLAYER.remove(p)

def broadcast_global(info):
    global REMOTE_CLIENT

    for socket in REMOTE_CLIENT[1:]:
        try:
            socket.sendall(info)
        except:
            print("error broadcast_global")
            socket.close()
            i = REMOTE_CLIENT.index(socket)
            p = REMOTE_PLAYER[i-1]
            print("supression de", p.id, "de la liste")
            REMOTE_CLIENT.remove(socket)
            REMOTE_PLAYER.remove(p)

def udp_to_tcp_update(location, type):
    global REMOTE_PLAYER
    if "updateLocation" in type:
        player = next((player for player in REMOTE_PLAYER if player.get_info()["id"]==location["id"]))
        player.update(location["x"], location["y"])
        info = type + json.dumps(player.get_info()) +";\r\n"
        NewInfo =  f.encrypt(info.encode())
        broadcast_global(NewInfo)
    else:
        LocBall = type + json.dumps(location) + ";\r\n"
        NewLocBall = f.encrypt(LocBall)
        broadcast_global(NewLocBall)

def handle_udp(sock):

    while True:
        data, addr = sock.recvfrom(const.RECV_BUFF) # taille du buffer est de 1024 octets
        ResData = f.decrypt(data)
        msg = ResData.decode().split(";")
        if msg[0] == "updateLocation":
            udp_to_tcp_update(json.loads(msg[1]), msg[0] + ";\r\n")
        elif msg [0] == "updateBallLocation":
            udp_to_tcp_update(json.loads(msg[1]), msg[0]+";\r\n")

def handle_ball(ball):
    serveur = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clock = gametime.Clock()

    while True:
        global REMOTE_PLAYER
        ball.update(REMOTE_PLAYER)
        info = "updateBallLocation;" + json.dumps(ball.get_info()) +";\r\n"
        NewInfo = f.encrypt(info.encode())
        broadcast_global(NewInfo)
        clock.tick(const.FPS)

def main():

    global REMOTE_CLIENT
    global REMOTE_PLAYER

    #parse des paramètres
    parser = argparse.ArgumentParser(description='Multi Pong', prog='serveur')
    parser.add_argument('--host', '--i',
                        action="store",
                        dest='arg_host',
                        help='Hostname for client to connect')
    parser.add_argument('--port', '--p',
                        action='store',
                        dest='arg_port',
                        help='Port for clients to connect')

    args = parser.parse_args()

    # utilise contantes.py si aucun paramètre n'est fournit
    host = args.arg_host if args.arg_host is not None else const.HOST
    port = args.arg_port if args.arg_port is not None else const.PORT

    print("host", host, "port", port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    REMOTE_CLIENT.append(s)

    # lie le socket au local host
    try:
        udp_server.bind((host, port))
        s.bind((host, port))
    except socket.error as msg:
        print('bind fail. erreure :' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    ball = Pong(const.SCREENSIZE, 1)

    start_new_thread(handle_udp, (udp_server,))
    start_new_thread(handle_ball, (ball,))
    # écoute sur le socket
    s.listen(5)

    print("serveur en écoute")

    while True:
        try:
            ready_read, ready_write, in_error = select.select(REMOTE_CLIENT, [], [], 0)

            for sock in ready_read:
                # nouvelle connection reçu
                if sock == s:
                    conn, addr = s.accept()
                    print("Client", addr[0], "connecté sur", addr[1])

                    player = Player(len(REMOTE_CLIENT)-1) # ne compte pas le socket du serveur

                    print("joueur créé et ajouté à la liste")
                    package = json.dumps([player.get_info(), ball.get_info()])
                    TokenPackage = f.encrypt(package.encode())
                    conn.sendall(TokenPackage)

                    REMOTE_PLAYER.append(player)
                    REMOTE_CLIENT.append(conn)



                    cur_list = [player.get_info() for player in REMOTE_PLAYER]

                    CurrentList = ("CL;" + json.dumps(cur_list) + ";\r\n")
                    #TokenList = f.encrypt(CurrentList.encode())
                    broadcast_global(CurrentList.encode())

                    print("joueur inital envoyé")
                    NewPlayer = ("newPlayer;" + json.dumps(player.get_info()) + ";\r\n")
                    TokenPlayer = f.encrypt(NewPlayer.encode())
                    broadcast_all(conn, TokenPlayer)
                #sinon c'est un update du client
                else:
                    try:
                        data = sock.recv(const.RECV_BUFF)
                        print(data.decode())
                        if data:
                            res = data.decode().split(";")
                            print(res[0])
                            if res[0] == "combo":
                                print("received: ", res[1])
                            elif res[0] == "sentMessage":
                                msg = "receivedMessage;"+ res[1] + ';' + res[2]+';\r\n'
                                broadcast_all(sock, msg.encode())
                        else:
                            # perte de connection du client
                            sock.close()

                            i = REMOTE_CLIENT.index(sokc)
                            p = REMOTE_PLAYER[i-1]

                            print("Suppression du joueur", p.id, " de la liste")
                            broadcast_global(("suppresion du joueur"+ json.dumps(p.get_info())+ ";\r\n").encode())

                            REMOTE_PLAYER.remove(p)
                            REMOTE_CLIENT.remove(sock)
                    except:
                        print("aucune data reçue")
                        continue

        except KeyboardInterrupt:

            print("Fermeture du serveur")
            for sock in REMOTE_CLIENT:
                sock.close()
            sys.exit()

if __name__ == '__main__':
        main()
