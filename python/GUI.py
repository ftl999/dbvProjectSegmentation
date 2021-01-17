# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 14:04:32 2021

@author: Raphael-NB
"""
import math
import tkinter as tk
import cv2
import numpy as np
from PIL import ImageTk, Image
from screeninfo import get_monitors
from tkinter import filedialog
from ImagePipe import ImagePipe, PipeStageListener



class GUI(PipeStageListener):

    def __init__(self):
        ## setting up for image pipe
        ImagePipe.registerListener(self)

        self.width = get_monitors()[0].width
        self.height = get_monitors()[0].height
        self.root = tk.Tk()
        self.root.geometry(str(self.width) + "x" + str(self.height))
        self.canvas = tk.Canvas(self.root,width=(self.width//4),height=(self.width//4), highlightthickness = 2, highlightbackground = "black")
        self.canvas2 = tk.Canvas(self.root,width=(self.width//4),height=(self.width//4), highlightthickness = 2, highlightbackground = "black")
        self.canvas.place(x = self.width//6, y = self.height//6)
        self.canvas2.place(x = self.width-self.width//4-self.width//6, y = self.height//6)
        self.menu = tk.Menu(self.root)
        self.filemenu = tk.Menu(self.menu)
#        self.submenu = tk.Menu(self.filemenu)
#        self.submenu.add_command(label="Tsest")
        self.filemenu.add_command(label='Load', underline=0, command=self.loadVideo)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", underline=0, command=self.root.destroy)
        self.menu.add_cascade(label="File", underline=0, menu=self.filemenu)
        self.root.config(menu=self.menu)
        self.scaler = 0
        self.playButton = 0
        self.frameCount = 0
        self.frameWidth = 0
        self.frameHeight = 0
        self.videocube = 0
        self.im = 0
        self.im2 = 0
        self.isPlaying = 0
        while True:
        	self.root.update_idletasks()
        	self.root.update()
        return

    def __onEndProcessing__(self, stage: str, result: np.ndarray):
        print("Stage finished processing: " + stage)

    def loadVideo(self):
        file_path = filedialog.askopenfilename()
        cap = cv2.VideoCapture(file_path)#('190301_02_KenyaWildlife_29_Trim.mp4')
        self.frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        buffer = np.empty((self.frameCount, self.frameHeight, self.frameWidth, 3), np.dtype('uint8'))  #shape: (161, 1080, 1920, 3)
        fc = 0
        ret = True
        while (fc < self.frameCount  and ret):
            ret, buffer[fc] = cap.read()
            fc += 1
        self.videocube = buffer
        cap.release()
        self.scaler = tk.Scale(self.root, from_=0, to=self.frameCount-1, orient="horizontal")
        self.scaler.place(x = self.width//2-(3*self.width//4)//2 , y = 4*self.height//6, width = 3*self.width//4)
        self.im = np.zeros((self.width//4,self.width//4,3),dtype=np.uint8)
        self.im2 = np.zeros((self.width//4,self.width//4,3),dtype=np.uint8)
        self.playButton = tk.Button(self.root, text="Play", fg="red", command=self.play)
        self.playButton.place(x=self.width//10, y=4*self.height//6)
        self.run() 
       
    def getorigin(self, eventorigin):
        #global x0,y0
        self.x0 = eventorigin.x
        self.y0 = eventorigin.y
        self.x0 = int(max(0,min(self.frameHeight-1,(self.x0 * self.factor))))
        self.y0 = int(min(self.frameWidth-1,max(0,(self.y0*(self.frameWidth/(self.width//4))))))
        print(self.x0,self.y0)
        self.videocube[self.scaler.get()][self.x0][self.y0] = (np.ones(3, dtype=np.uint8) * 255)
        self.showFrame()

    def showFrame(self):
        frameNumber = self.scaler.get()
        frame = self.videocube[frameNumber]
        edditedFrame = self.switchChannel(frame.copy())
        self.factor = frame.shape[1] / (self.width//4)
        frame = cv2.resize(frame, (self.width//4,int(frame.shape[0]/self.factor)))
        edditedFrame = cv2.resize(edditedFrame, (self.width//4,int(edditedFrame.shape[0]/self.factor)))
        self.im[int(math.ceil(self.width//4-frame.shape[0])/2):-int((self.width//4-frame.shape[0])/2),:,:] = frame[:,:,::-1]
        self.im2[int(math.ceil(self.width//4-edditedFrame.shape[0])/2):-int((self.width//4-edditedFrame.shape[0])/2),:,:] = edditedFrame[:,:,::-1]
        img = ImageTk.PhotoImage(image=Image.fromarray(self.im))
        img2 = ImageTk.PhotoImage(image=Image.fromarray(self.im2))
        self.canvas.create_image(2,2, anchor="nw", image=img)
        self.canvas2.create_image(2,2, anchor="nw", image=img2)
        
        ImagePipe.process(frame)

        self.canvas.bind("<B1-Motion>",self.getorigin)
        while True:
            if self.isPlaying:
                self.scaler.set(self.scaler.get() + 1)
            self.root.update_idletasks()
            self.root.update()
            if frameNumber != self.scaler.get():
                break
        self.canvas.delete("all")
        self.canvas2.delete("all")
      
    def play(self):
        self.isPlaying = (self.isPlaying + 1) % 2
        print(self.isPlaying)
    
        
    def switchChannel(self, frame):
        temp = frame[:,:,2]
        frame[:,:,2] = frame[:,:,1]
        frame[:,:,1] = temp
        return frame
        
    def run(self):
        while True:
            self.showFrame()

if __name__ == "__main__":
    testGui = GUI()
    #testGui.loadVideo()

    #while True:
    #	testGui.showFrame()

