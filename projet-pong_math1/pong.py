#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Tkinter import *
from random import randint

class Fenetre(Tk):
    def __init__(self, width=600, height=400):
        Tk.__init__(self)
        self.flag = 0

        self.quit= Button(self,text="Quit Game",command=self.destroy)
        self.quit.grid(column=4,row=0,sticky="NE")

        self.new= Button(self,text="New Game",command=self.new_game)
        self.new.grid(column=0,row=0,sticky="NW")


        self.can = Canvas(self,width=width,height=height,bg="black")
        self.can.grid(column=0,row=1,sticky="SW",columnspan=5)

    def new_game(self):
        if self.flag == 0 :
            self.flag=1
            self.pads = Pad(self.can,self.flag)
            self.ball = Ball(self.can,self.pads,self.flag)

class Pad:
    def __init__(self,canvas,flag):
        self.canvas = canvas
        self.flag = flag
        self.height = canvas.winfo_height()
        self.width = canvas.winfo_width()
        self.x1,self.y1 = 10,self.height/2-30
        self.x2,self.y2 = self.width-25,self.height/2-30

        self.Pad1 = canvas.create_rectangle(self.x1,self.y1,self.x1+15,self.y1+60,fill="white")
        self.Pad2 = canvas.create_rectangle(self.x2,self.y2,self.x2+15,self.y2+60,fill="white")

        canvas.bind_all("<Up>",self.mouv_up)
        canvas.bind_all("<Down>", self.mouv_down)
        self.dy2 = 25
        self.ia()

    def mouv_up(self,event):
        if self.y1>5 :
            self.y1=self.y1-10
            self.canvas.coords(self.Pad1,self.x1,self.y1,self.x1+15,self.y1+60)

    def mouv_down(self,event):
        if self.y1+60<(self.height-5):
            self.y1=self.y1+10
            self.canvas.coords(self.Pad1,self.x1,self.y1,self.x1+15,self.y1+60)

    def ia (self):
        self.y2=self.y2 + self.dy2
        if self.y2+60 > self.height-10 :
            self.dy2=-50

        if self.y2 < 5 :
            self.dy2=50

        self.canvas.coords(self.Pad2,self.x2,self.y2,self.x2+15,self.y2+60)
        if self.flag > 0:
            self.canvas.after(70,self.ia)


class Ball:
    def __init__(self,canvas,pad,flag):
        self.canvas = canvas
        self.pad = pad
        self.height = canvas.winfo_height()
        self.width = canvas.winfo_width()
        self.flag = flag
        self.x1,self.y1 = self.width/2,self.height/2
        self.dx,self.dy = 30,30
        self.Ball = canvas.create_oval(self.x1, self.y1, self.x1+25, self.y1+25, width=2, fill='white')
        self.pointA, self.pointB = 0,0

        self.ready()

    def ready(self):
        self.starter=0
        self.score= Label(app,text="%d : %d" % (self.pointA,self.pointB), bg="black",fg="white")
        self.score.grid(column =2,row=0,sticky="S")
        self.x1,self.y1 = self.height/2,self.width/2
        app.titre = Label(app,text="PRESS ANY KEY TO START", bg="black",fg="white")
        app.titre.grid(column =2,row=2,sticky="S")
        self.canvas.bind_all("<Key>",self.start)


    def start(self,event):
        self.starter=1
        self.move()

    def move(self):
        if self.starter==1:
            self.x1, self.y1 = self.x1 +self.dx, self.y1 + self.dy

            if self.y1 >self.height-26:
                self.dx, self.dy = self.dx, -20

            if self.y1 <2:
                self.dx, self.dy = self.dx, 20

            if self.x1 < self.pad.x1+20:
                if self.pad.y1 < self.y1 < self.pad.y1+60:
                    self.dx, self.dy = 20, self.dy

            if self.x1+30 >  self.pad.x2-1:
                if self.pad.y2<self.y1+12.5<self.pad.y2+60:
                     self.dx, self.dy = -20, self.dy

            if self.x1 < 0:
                self.starter = 0
                self.pointB = self.pointB+1
                self.ready()


            if self.x1+25 > self.width:
                self.starter=0
                self.pointA = self.pointA+1
                self.ready()

            self.canvas.coords(self.Ball,self.x1,self.y1,self.x1+30,self.y1+30)
            if self.flag > 0:
                self.canvas.after(70,self.move)




if __name__ == "__main__":
    app = Fenetre()
    app.mainloop()
