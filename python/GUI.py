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
import time


class GUI:
    
    def __init__(self):
        self.width = get_monitors()[0].width
        self.height = get_monitors()[0].height
        self.root = tk.Tk()
        self.root.geometry(str(self.width) + "x" + str(self.height))
        self.canvas = tk.Canvas(self.root,width=(self.width//4),height=(self.width//4), highlightthickness = 2, highlightbackground = "black")
        self.canvas2 = tk.Canvas(self.root,width=(self.width//4),height=(self.width//4), highlightthickness = 2, highlightbackground = "black")
        self.canvas.place(x = self.width//6, y = self.height//6)
        self.canvas2.place(x = self.width-self.width//4-self.width//6, y = self.height//6)
        self.scaler = 0
        self.playButton = 0
        self.frameCount = 0
        self.frameWidth = 0
        self.frameHeight = 0
        self.videocube = 0
        self.im = 0
        self.im2 = 0
        self.isPlaying = 0
        return
    
    def loadVideo(self):
        cap = cv2.VideoCapture('190301_02_KenyaWildlife_29_Trim.mp4')
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
        
    def showFrame(self):
        frameNumber = self.scaler.get()
        frame = self.videocube[frameNumber]
        edditedFrame = self.switchChannel(frame.copy())
        factor = frame.shape[1] / (self.width//4)
        frame = cv2.resize(frame, (self.width//4,int(frame.shape[0]/factor)))
        edditedFrame = cv2.resize(edditedFrame, (self.width//4,int(edditedFrame.shape[0]/factor)))
        self.im[int(math.ceil(self.width//4-frame.shape[0])/2):-int((self.width//4-frame.shape[0])/2),:,:] = frame[:,:,::-1]
        self.im2[int(math.ceil(self.width//4-edditedFrame.shape[0])/2):-int((self.width//4-edditedFrame.shape[0])/2),:,:] = edditedFrame[:,:,::-1]
        img = ImageTk.PhotoImage(image=Image.fromarray(self.im))
        img2 = ImageTk.PhotoImage(image=Image.fromarray(self.im2))
        self.canvas.create_image(2,2, anchor="nw", image=img)
        self.canvas2.create_image(2,2, anchor="nw", image=img2)
        while True:
            if self.isPlaying:
                self.scaler.set(self.scaler.get() + 1)
            time.sleep(0.05)
            self.root.update_idletasks()
            self.root.update()
            if frameNumber != self.scaler.get():
                break
        self.canvas.delete("all")
        self.canvas2.delete("all")
        self.showFrame()
      
    def play(self):
        self.isPlaying = (self.isPlaying + 1) % 2
        print(self.isPlaying)
    
        
    def switchChannel(self, frame):
        temp = frame[:,:,2]
        frame[:,:,2] = frame[:,:,1]
        frame[:,:,1] = temp
        return frame
        


testGui = GUI()
testGui.loadVideo()
testGui.showFrame()

