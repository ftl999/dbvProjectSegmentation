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
from ProcessingPipe import ProcessingPipe, PipeStageListener, StageType
import time


class GUI(PipeStageListener):
    def __init__(self):
        ## setting up for image pipe
        ProcessingPipe.registerListener(self)

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
        self.im = np.zeros((self.width//4, self.width//4,3), dtype=np.uint8)
        self.im2 = np.zeros((self.width//4, self.width//4,3), dtype=np.uint8)
        self.isPlaying = False
        self.lastPoint = 0
        self.img = ImageTk.PhotoImage(image=Image.fromarray(self.im))
        self.img2 = ImageTk.PhotoImage(image=Image.fromarray(self.im2))
        self.canvasImg = self.canvas.create_image(2,2, anchor="nw", image=self.img)
        self.canvasImg2 = self.canvas2.create_image(2,2, anchor="nw", image=self.img2)

        self.pipeStages = [StageType.Video, StageType.Segmentation, StageType.PointExtraction]
        self.lastFrameTime = time.time()
        
        self.root.bind('<Left>',self.leftKey)
        self.root.bind('<Right>',self.rightKey)

        self.root.mainloop()

    def leftKey(self, event):
        if self.scaler.get() > 0:
            self.scaler.set(self.scaler.get() - 1)
        self.showFrame()

    def rightKey(self, event):
        if self.scaler.get() < self.frameCount:
            self.scaler.set(self.scaler.get() + 1)
        self.showFrame()

    def __onEndProcessing__(self, stage: StageType, result: np.ndarray):
        print("Stage finished processing: " + str(stage))
        if not (result is None):
            print("   with result!")
            non_zero = self.frameMasks[self.scaler.get()] > 0
            edditedFrame = np.where(non_zero, self.frameMasks[self.scaler.get()],result.copy())
            edditedFrame = cv2.resize(edditedFrame, (self.width//4,int(result.shape[0]/self.factor)))
            if stage == StageType.Video:
                self.im[int(math.ceil(self.width//4-edditedFrame.shape[0])/2):-int((self.width//4-edditedFrame.shape[0])/2),:,:] = edditedFrame[:,:,::-1]
                self.img = ImageTk.PhotoImage(image=Image.fromarray(self.im))
                self.canvas.itemconfig(self.canvasImg2, image=self.img)
                if self.isPlaying == True:
                    if self.scaler.get() < self.frameCount:
                        self.scaler.set(self.scaler.get() + 1)
                        self.showFrame()
                    else:
                        self.isPlaying = False
            else:
                self.im2[int(math.ceil(self.width//4-edditedFrame.shape[0])/2):-int((self.width//4-edditedFrame.shape[0])/2),:,:] = edditedFrame[:,:,::-1]
                self.img2 = ImageTk.PhotoImage(image=Image.fromarray(self.im2))
                self.canvas2.itemconfig(self.canvasImg2, image=self.img2)
            self.root.update_idletasks()
            self.root.update()

    def onScalerMouseDown(self):
        self.pipeStages = [StageType.Video]
        print("Mouse Down")

    def onScalerMouseUp(self):
        print("Mouse Up")
        self.pipeStages = [StageType.Video, StageType.Segmentation, StageType.PointExtraction]
        self.showFrame()
    
    def loadVideo(self):
        file_path = filedialog.askopenfilename()
        print("Load Video")

        vidProc = ProcessingPipe.getStageByName(StageType.Video).processors[0]
        vidProc.loadVideo(file_path)
        self.frameCount = vidProc.frameCount
        self.frameWidth = vidProc.frameWidth
        self.frameHeight = vidProc.frameHeight
	
        self.frameMasks = np.zeros((self.frameCount, self.frameHeight, self.frameWidth,3),dtype=np.uint8)

        self.scaler = tk.Scale(self.root, from_=0, to=self.frameCount-1, orient="horizontal", command=self.scalerChange)
        self.scaler.place(x = self.width//2-(3*self.width//4)//2 , y = 4*self.height//6, width = 3*self.width//4)
        self.scaler.bind("<Button-1>", lambda x: self.onScalerMouseDown())
        self.scaler.bind("<ButtonRelease-1>", lambda x: self.onScalerMouseUp())
        self.playButton = tk.Button(self.root, text="Play", fg="red", command=self.play)
        self.playButton.place(x=self.width//10, y=4*self.height//6)
        self.showFrame()
       
    def getorigin(self, eventorigin):
        #global x0,y0
        self.x0 = eventorigin.x
        self.y0 = eventorigin.y
        self.x0 = max(5, min(self.frameWidth-5-1, self.x0 * self.factor))#int(max(0,min(self.frameHeight-1,(self.x0 * self.factor))))
        self.y0 = max(5,min(self.frameHeight-5-1,(self.y0-(self.width//(4*self.factor)))*self.factor))#(self.y0-(self.width//4 - self.frameHeight//2)//2)*self.factor))#int(min(self.frameWidth-1,max(0,(self.y0*(self.frameWidth/(self.width//4))))))
        print(self.x0,self.y0)
        if self.lastPoint != 0:
            self.frameMasks[self.scaler.get(),int(self.y0)-5:int(self.lastPoint[0])+5,int(self.x0)-5:int(self.lastPoint[1])+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.scaler.get(),int(self.lastPoint[0])-5:int(self.y0)+5,int(self.lastPoint[1])-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.scaler.get(),int(self.lastPoint[0])-5:int(self.y0)+5,int(self.x0)-5:int(self.lastPoint[1])+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.scaler.get(),int(self.y0)-5:int(self.lastPoint[0])+5,int(self.lastPoint[1])-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
        else:
            self.frameMasks[self.scaler.get(),int(self.y0)-5:int(self.y0)+5,int(self.x0)-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
        print(self.frameMasks[self.scaler.get(), int(self.y0), int(self.x0)])
        self.lastPoint = [int(self.y0),int(self.x0)]
        self.showFrame()
    
    def resetLastPoint(self, eventRelease):
        self.lastPoint = 0

    def showFrame(self):
        if not self.isPlaying and (time.time() - self.lastFrameTime) < 0.1:
            return

        self.lastFrameTime = time.time()
        frameNumber = self.scaler.get()
        ProcessingPipe.getStageByName(StageType.Video).processors[0].framenumber = frameNumber
        #fullFrame = self.videocube[frameNumber]
 #       edditedFrame = self.frameMasks[frameNumber]#self.switchChannel(fullFrame.copy())
        self.factor = self.frameWidth / (self.width//4)
        #frame = cv2.resize(fullFrame.copy(), (self.width//4,int(fullFrame.shape[0]/self.factor)))
        #edditedFrame = cv2.resize(edditedFrame, (self.width//4,int(edditedFrame.shape[0]/self.factor)))
        #self.im[int(math.ceil(self.width//4-frame.shape[0])/2):-int((self.width//4-frame.shape[0])/2),:,:] = frame[:,:,::-1]
#        self.im2[int(math.ceil(self.width//4-edditedFrame.shape[0])/2):-int((self.width//4-edditedFrame.shape[0])/2),:,:] = edditedFrame[:,:,::-1]
        #self.img = ImageTk.PhotoImage(image=Image.fromarray(self.im))
#        self.img2 = ImageTk.PhotoImage(image=Image.fromarray(self.im2))
        #self.canvas.itemconfig(self.canvasImg, image=self.img)
  #      self.canvas2.itemconfig(self.canvasImg2, image=self.img2)
        self.canvas.bind("<B1-Motion>",self.getorigin)
        self.canvas.bind("<ButtonRelease-1>",self.resetLastPoint)

        ProcessingPipe.process(self.pipeStages)
      
    def play(self):
        ProcessingPipe.reset()
        self.isPlaying = not self.isPlaying
        if self.isPlaying:
            print("PLAY!")
            self.onScalerMouseDown()
            self.pipeStages.append(StageType.PointTracking)
        else:
            self.onScalerMouseUp()
        self.showFrame()
    
        
    def switchChannel(self, frame):
        temp = frame[:,:,2]
        frame[:,:,2] = frame[:,:,1]
        frame[:,:,1] = temp
        return frame
        
    def scalerChange(self, evt):
        self.showFrame()

if __name__ == "__main__":
    testGui = GUI()
    #testGui.loadVideo()

    #while True:
    #	testGui.showFrame()

