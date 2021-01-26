from tkinter import Image
from ProcessingPipe import PipeStageProcessor, ResultType, InactivePipeStageException, StageType
import cv2
import numpy as np
from typing import Tuple, Dict
from ImageHelper import ImageHelper


class SegmentationStage(PipeStageProcessor):
    def __init__(self):
        super().__init__()
        self.framenumber = 0
        self.firstPoint = 0
        self.lastPoint = 0
        self.frameMasks = np.zeros(1)#(self.frameCount, self.frameHeight, self.frameWidth,3),dtype=np.uint8)

    def __process__(self, sources: Dict[StageType, Tuple[ResultType, object]]) -> Tuple[ResultType, object]:
        print("seg process")
        return (ResultType.Image, self.frameMasks[self.framenumber])#, self.frameMasks[self.framenumber])

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        print("seg render")
        return self.frameMasks[self.framenumber]

    def draw_mask(self, x, y, factor, width, frameHeight, frameWidth, framenumber, frameCount):
        self.frameCount = frameCount
        self.framenumber = framenumber
        self.width = width
        self.frameHeight = frameHeight
        self.frameWidth = frameWidth
        self.factor = factor
        if len(self.frameMasks) == 1:
            self.frameMasks = np.zeros((self.frameCount, self.frameHeight, self.frameWidth,3),dtype=np.uint8)
        self.x0 = x
        self.y0 = y
        self.x0 = max(5, min(self.frameWidth-5-1, self.x0 * self.factor))
        self.y0 = max(5,min(self.frameHeight-5-1,((self.y0-(((self.width//4)-(self.frameHeight//self.factor)))/2)*self.factor)))

        if self.lastPoint != 0:
            self.frameMasks[self.framenumber,int(self.y0)-5:int(self.lastPoint[0])+5,int(self.x0)-5:int(self.lastPoint[1])+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.framenumber,int(self.lastPoint[0])-5:int(self.y0)+5,int(self.lastPoint[1])-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.framenumber,int(self.lastPoint[0])-5:int(self.y0)+5,int(self.x0)-5:int(self.lastPoint[1])+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.framenumber,int(self.y0)-5:int(self.lastPoint[0])+5,int(self.lastPoint[1])-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
        else:
            self.frameMasks[self.framenumber,int(self.y0)-5:int(self.y0)+5,int(self.x0)-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
        self.lastPoint = [int(self.y0),int(self.x0)]
        if self.firstPoint == 0:
            self.firstPoint = self.lastPoint

    def resetLastPoint(self):
        self.lastPoint = 0
        if self.firstPoint != 0:
            self.frameMasks[self.framenumber,int(self.y0)-5:int(self.firstPoint[0])+5,int(self.x0)-5:int(self.firstPoint[1])+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.framenumber,int(self.firstPoint[0])-5:int(self.y0)+5,int(self.firstPoint[1])-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.framenumber,int(self.firstPoint[0])-5:int(self.y0)+5,int(self.x0)-5:int(self.firstPoint[1])+5] = (np.ones(3, dtype=np.uint8) * 255)
            self.frameMasks[self.framenumber,int(self.y0)-5:int(self.firstPoint[0])+5,int(self.firstPoint[1])-5:int(self.x0)+5] = (np.ones(3, dtype=np.uint8) * 255)
        self.firstPoint = 0

        #grayMask = ImageHelper.make_it_gray(self.frameMasks[self.framenumber])
        #im2, contours = cv2.findContours(grayMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        self.frameMasks[self.framenumber] = cv2.morphologyEx(self.frameMasks[self.framenumber], cv2.MORPH_CLOSE, np.ones((5,5),np.uint8), iterations=100)
        #cv2.fillPoly(grayMask, )
        #con = cv2.floodFill(self.frameMasks[self.framenumber], mask=None)
        print("YUHUU")
        


    def update_framenumber(self,fn):
        self.framenumber = fn
