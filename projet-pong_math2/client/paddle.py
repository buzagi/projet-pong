import json
import os
import pygame
import base64
import binascii
from cryptography.fernet import Fernet

rand = binascii.unhexlify(b"eaf57617c2256f260dee04cd84db18c01d59e75a95da8d9eb12c460192ddc1af")
key = base64.urlsafe_b64encode(rand)
f = Fernet(key)
import constantes as const


class PlayerPaddle(object):
        # TODO ajouter différente position de x en fonction du nombre de joueur

    def __init__(self, screensize, player, color=const.WHITE):

        print("initializing with ", player)
        self.screensize = screensize
        self.centery = int(screensize[1]*0.5)

        self.side = player % 2

        if self.side == 0:
            self.centerx = screensize[0] - (5 + (player * 30))
        else:
            self.centerx = (player * 30) + 5 if player > 1 else 5

        self.height = 100
        self.width = 10

        self.id = player

        # Pygame box that paddle is drawn and refreshed on
        self.rect = pygame.Rect(0, self.centery-int(self.height*0.5), self.width, self.height)

        self.color = color

        # Speed and direction
        self.speed = 4
        self.direction = 0

    def update_local(self, y_new):
        self.centery = y_new
        self.rect.center = (self.centerx, self.centery)

        # make sure paddle does not go off screen
        if self.rect.top < 0:
                self.rect.top = 0
        if self.rect.bottom > self.screensize[1]-1:
                self.rect.bottom = self.screensize[1]-1 

    def get_id(self):
        return self.id
                
    def update(self, server):
        self.centery += self.direction*self.speed
        self.rect.center = (self.centerx, self.centery)

        # make sure paddle does not go off screen
        if self.rect.top < 0:
                self.rect.top = 0
        if self.rect.bottom > self.screensize[1]-1:
                self.rect.bottom = self.screensize[1]-1 

        info = {"x": self.centerx, "y": self.centery, "id": self.id}
        data = "updateLocation;" +json.dumps(info) + "\r\n"
        NewData = f.encrypt(data.encode())
        server.sendto(NewData, (const.HOST, const.PORT))

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0)
        pygame.draw.rect(screen, const.BLACK, self.rect, 1)
