from pygame.locals import Rect
import constantes as const
import time


class Pong(object):
    def __init__(self, screensize, id):
        self.screensize = screensize
        self.id = id

        # place ball in the center
        self.centerx = int(screensize[0]*0.5) 
        self.centery = int(screensize[1]*0.5)

        self.radius = 8

        # create shape and sizes it
        self.rect = Rect(self.centerx-self.radius, 
                         self.centery-self.radius,
                         self.radius*2, self.radius*2)
        self.color = const.WHITE
        self.direction = [1, 1] # current direction to the right and up
        # list so we can access each individual part because it will change

        self.speedx = 4
        self.speedy = 2

        self.hit_left_edge = False
        self.hit_right_edge = False

        self.ai_score = 0
        self.player_score = 0

        self.player_paddle_win = False
        self.ai_paddle_win = False              
        self.play_sound = False

    def update(self, player_list):
        self.play_sound = False
        self.centerx += self.direction[0]*self.speedx
        self.centery += self.direction[1]*self.speedy
        self.rect.center = (self.centerx, self.centery)
        # makes sure if ball hits top it comes back down
        if self.rect.top <= 0: 
                self.direction[1] = 1
        elif self.rect.bottom >= self.screensize[1]-1:
                self.direction[1] = -1 # bounce up and down
        elif self.rect.right >= self.screensize[0]-1: 
                self.direction[0] = -1
        elif self.rect.left <= 0:
                self.direction[0] = 1

        # checks if the code above is true
        if self.rect.right >= self.screensize[0]-1: # if it's greater than width -1
                self.hit_right_edge = True
        elif self.rect.left <= 0:
                self.hit_left_edge = True
        if self.rect.top <= 0: 
                self.hit_right_edge = True
        elif self.rect.bottom >= self.screensize[1]-1:
                self.hit_left_edge = True


        #Resets score after all player leave and restart game
        if  len(player_list) < 1:
            self.reset_score()

        # check for a collision between the rectangles
        for player in player_list:
            if player.side == 0:
                if self.rect.colliderect(player.rect):
                    self.direction[0] = -1
                    self.play_sound=True;
                    self.player_score += 1
                    if self.player_score == 15:  # win if you score 15 points
                        time.sleep(.4)
                        self.player_paddle_win = True   
            else:
                if self.rect.colliderect(player.rect):
                    self.direction[0] = 1
                    self.play_sound=True;
                    self.ai_score += 1
                    if self.ai_score == 15:  # lose if the computer scores 15 points
                        time.sleep(.4)
                        self.ai_paddle_win = True

    def get_info(self):
        info = {
            "id": self.id,
            "x": self.centerx,
            "y": self.centery,
            "lscore": self.ai_score,
            "rscore": self.player_score,
            "rwin": self.player_paddle_win,
            "lwin": self.ai_paddle_win,
            "sound": self.play_sound
        }
        return info

    def reset_score(self):
        self.player_score = 0
        self.ai_score = 0
        self.ai_paddle_win = False
        self.player_paddle_win = False   

