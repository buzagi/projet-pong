import json
import tkinter as tk
from _thread import *
from socket import *
from tkinter import *
import os
import random

import pygame
from pygame.locals import KEYDOWN, K_DOWN, \
    K_UP, KEYUP

from ball import Pong
from chatbox import *
from paddle import PlayerPaddle
import constantes as const
import base64
import binascii
from cryptography.fernet import Fernet

rand = binascii.unhexlify(b"eaf57617c2256f260dee04cd84db18c01d59e75a95da8d9eb12c460192ddc1af")
key = base64.urlsafe_b64encode(rand)
f = Fernet(key)

PLAYER_LIST = []



def start_game(menu, username_input, host_input, port_input):

    #initialisation du jeu
    window = tk.Tk()
    window.geometry('340x620+680+0')
    window.title("Multi pong chat")
    pygame.init()

    # mise en place de l'écran

    screen = pygame.display.set_mode(const.SCREENSIZE)
    chat_box = Chatbox(window)

    player_name = username_input.get()
    host = host_input.get()
    port = int(port_input.get())


    main(chat_box, screen, window, menu, player_name, host, port)

def menu():

    menu = tk.Tk()

    menu.geometry('380x320+0+0')
    menu.title("Multi pong game")

    welcome_text = Label(menu, text="Multi Pong", font=("Verdana", 30, "bold"), fg="#1d228c")
    welcome_text.pack(side=TOP)

    user_frame = Frame(menu)
    user_frame.pack(side=TOP)

    user_label_text = StringVar()
    user_label_text.set("nom deu joueur")
    user_label = Label(user_frame, textvariable=user_label_text)
    user_label.pack(side=LEFT)

    default_username = StringVar()
    username_input = Entry(user_frame, textvariable=default_username)
    username_input.pack(side=LEFT, padx="10", pady="10")
    default_username.set(random.choice(const.USERNAMES))

    host_frame = Frame(menu)
    host_frame.pack(side=TOP)

    host_label_text = StringVar()
    host_label_text.set("Host")
    host_label = Label(host_frame, textvariable=host_label_text)
    host_label.pack(side=LEFT)

    default_host = StringVar()
    host_input = Entry(host_frame, textvariable=default_host)
    host_input.pack(side=LEFT, padx="10", pady="10")
    default_host.set(const.HOST)

    port_frame = Frame(menu)
    port_frame.pack(side=TOP)

    port_label_text = StringVar()
    port_label_text.set("Port")
    port_label = Label(port_frame, textvariable=port_label_text)
    port_label.pack(side=LEFT)

    default_port = StringVar()
    port_input = Entry(port_frame, textvariable=default_port)
    port_input.pack(side=LEFT, padx="10", pady="10")
    default_port.set(const.PORT)

    start_game_button = Button(menu, text="Start Game!",
                               command=lambda: start_game(menu, username_input, host_input, port_input), fg="#0e6519")
    start_game_button.pack(side=BOTTOM, padx="10", pady="10")

    menu.mainloop()

def update_players(p_list):
    global PLAYER_LIST

    pids = [p.id for p in PLAYER_LIST]
    for p in p_list:
        if p["id"] not in pids:
            PLAYER_LIST.append(PlayerPaddle(const.SCREENSIZE, p["id"], p["color"]))

def handle_ball(serveur, pong):

    while True:
        data, addr = serveur.recvfrom(const.RECV_BUFF)
        Resdata = f.decrypt(data)
        msg = Resdata.decode().split(";")
        print("msg", msg)
        if msg[0] == "updateLocation":
            print("located")
        elif msg [0] == "updateBallLocation":
            try:
                detail = json.loads(msg[1])
                pong.update(
                    detail["x"],
                    detail["y"],
                    detail["lscore"],
                    detail["rscore"],
                )
            except:
                print("erreur balle", msg)

def handle_serveur(queue, serveur, pong, player_name):
    global PLAYER_LIST
    data = b'ack;\r\n'

    while True:
        msg = serveur.recv(const.RECV_BUFF)
        liste2 = msg.decode().split(";")
        # liste actuelle
        if liste2[0] == "CurrentList":
            try:
                print("received list: ", liste2[1])
                p_list = json.loads(liste2[1])
                update_players(p_list)
            except:
                print("current list could not be read:", liste2)
        elif len(msg) < 250:
            print(msg)
            Resmsg = f.decrypt(msg)
            msg = Resmsg.decode().split(";")
            # Ajout d'un nouveau joueur
            if msg[0] == "newPlayer":
                try:
                    print(msg[1])
                    detail = json.loads(msg[1])
                    player = PlayerPaddle(const.SCREENSIZE, detail["id"], detail["color"])
                    PLAYER_LIST.append(player)
                    queue.append(["SERVER", "Le nouveau joueur" + player_name + " est arrivé"])
                except:
                    print("le nouveau joueur n'a pu être créé", msg)
            # mise à jour de la position d'un joueur.
            elif msg[0] == "updateLocation":

                try:
                    detail = json.loads(msg[1])
                    player = next((player for player in PLAYER_LIST if player.get_id() == detail["id"]))
                    player.update_local(detail["y"])
                except:
                    print("problème avec le message", msg)
            # mise à jour de la position de la balle
            elif msg[0] == "updateBallLocation":
                try:
                    detail = json.loads(msg[1])
                    pong.update(
                        detail["x"],
                        detail["y"],
                        detail["lscore"],
                        detail["rscore"],
                        detail["lwin"],
                        detail["rwin"],
                        detail["sound"],
                    )
                except Exception as e:
                    print("erreur de balle", e)
            elif msg[0] == "receivedMessage":
                global chat_box
                try:
                    queue.append(msg[1],msg[2])
                except Exception as e:
                    print("erreur chat",e )
    server.close()

def main(chat_box, screen, window, menu, player_name, host, port):
    global PLAYER_LIST
    msg_queue = []

    menu.destroy()

    server = socket(AF_INET, SOCK_STREAM)

    udp_server = socket(AF_INET, SOCK_DGRAM)

    try:
        server.connect((host, port))
    except error as msg:
        print("Erreure de connexion au serveur", msg)
        sys.exit(1)

    '''
    envoie des info joueur par le serveur
    '''
    Cypherres = server.recv(const.RECV_BUFF)
    Recvres = f.decrypt(Cypherres)
    print(Recvres.decode())
    res = json.loads(Recvres.decode())
    player_id = res[0]["id"]
    player_color = res[0]["color"]
    data = b'ack;\r\n'
    #DataNew = f.encrypt(data)
    server.sendall(data)

    print("nouveau jouer chargé depuis le serveur avec l'id:", player_id)

    def command(txt):
        print(txt)
        msg = 'sentMessage;' + player_name + ';' + txt + ';\r\n'
        server.sendall(msg.encode())

    running = True

    clock = pygame.time.Clock()
    pong = Pong(
        const.SCREENSIZE,
        res[1]["id"],
        res[1]["x"],
        res[1]["y"],
        res[1]["lscore"],
        res[1]["rscore"],
    )

    player_paddle1 = PlayerPaddle(const.SCREENSIZE, player_id, player_color)
    PLAYER_LIST.append(player_paddle1)

    print("joueur:", player_id, "créé et ajouté")

    pygame.display.set_caption('Multi Pong')

    win = pygame.mixer.Sound(os.path.join('data/win.wav'))
    lose = pygame.mixer.Sound(os.path.join('data/lose.wav'))

    start_new_thread(handle_serveur, (msg_queue, server, pong, player_name))

    chat_box.set_nick("SERVER")

    chat_box.set_command(command)

    chat_box.send("Bienvenu " + player_name + "!")
    chat_box.send("En attente de connexion...")

    chat_box.set_nick(player_name)

    while running:
        if len(PLAYER_LIST) <= 0:
            continue
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == KEYDOWN:
                    if event.key == K_UP and player_paddle1.centery > 30:
                        player_paddle1.direction = -1

                    elif event.key == K_DOWN and player_paddle1.centery < 570:
                        player_paddle1.direction = 1

                if event.type == KEYUP:
                    if event.key == K_UP and player_paddle1.direction == -1:
                        player_paddle1.direction = 0
                        if player_paddle1.centery < 10:
                            player_paddle1.centery = 0

                    elif event.key == K_DOWN and player_paddle1.direction == 1:
                        player_paddle1.direction = 0
                        if player_paddle1.centery > 620:
                            player_paddle1.centery = 620

            player_paddle1.update(udp_server)

            screen.fill(const.BLACK)
            # pygame.draw.line(screen, const.WHITE, (const.SCREEN_WIDTH / 2, 0), (const.SCREEN_WIDTH / 2, const.SCREEN_LENGTH), 5)

            # Deterimine win
            if pong.lwin == True:
                running = False
            elif pong.rwin == True:
                running = False

            for player in PLAYER_LIST:
                player.render(screen)

            pong.render(screen)

            default_font = pygame.font.get_default_font()
            font = pygame.font.Font(default_font, 30)

            left_score = font.render("West Side " + str(pong.lscore), True, const.WHITE)
            screen.blit(left_score, (20, 0))

            right_score = font.render("East Side " + str(pong.rscore), True, const.WHITE)
            screen.blit(right_score, ((const.SCREEN_WIDTH / 2) + 20, 0))

            user_font = pygame.font.Font(default_font, 20)
            user_msg = user_font.render(player_name, True, player_color)
            screen.blit(user_msg, ((const.SCREEN_WIDTH / 2) + 5, const.SCREEN_LENGTH - 20))

            for msg in msg_queue:
                chat_box.user_message(msg[0], msg[1])
                msg_queue.remove(msg)

            chat_box.interior.pack(expand=True, fill=BOTH)

            window.update()

            clock.tick(const.FPS)
            pygame.display.flip()

    if pong.lwin == True and player_paddle1.side == 1:
        txt = font.render(" Victoire!!!!", True, const.WHITE)
        screen.blit(txt, (100, 200))
        win.play()
    elif pong.rwin == True and player_paddle1.side == 0:
        txt = font.render(" Victoire!!!!", True, const.WHITE)
        screen.blit(txt, (100, 200))
        win.play()
        print("left  won")
    else:
        txt2 = font.render("Défaite!", True, const.WHITE)
        screen.blit(txt2, (100, 200))
        lose.play()

    pygame.display.flip()
    server.close()
    pygame.time.delay(5000)
    pygame.quit()


if __name__ == '__main__':
    menu()
