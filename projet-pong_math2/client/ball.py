import pygame
import os

import constantes as const


class Pong(object):
    def __init__(self, screensize, id, x, y, lscore, rscore):
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, "..", "client/data/wow.wav"))
        self.screensize = screensize
        self.id = id
        self.centerx = x
        self.centery = y
        self.lscore = lscore
        self.rscore = rscore
        self.radius = 8
        self.lwin = False
        self.rwin = False
        self.sound= pygame.mixer.Sound(filepath)        

        # create shape and sizes it
        self.rect = pygame.Rect(self.centerx-self.radius,
                                self.centery-self.radius,
                                self.radius*2, self.radius*2)
        self.color = const.WHITE

    def update(self, x, y, lscore, rscore, lwin, rwin, sound):
        self.centerx = x
        self.centery = y
        self.lscore = lscore
        self.rscore = rscore
        self.rect.center = (self.centerx, self.centery)
        self.lwin = lwin
        self.rwin = rwin


    def render(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 0)
        # creates black outline of the circle
        pygame.draw.circle(screen, const.BLACK, self.rect.center, self.radius, 1)
