import cv2 as cv
import numpy as np


class ObjectSegmenter:
    def __init__(self, frame):
        self.frame = frame
        self.objectmask = np.zeros((frame.dim))
        self.frameHistory = np.array((10,frame.dim))
    def setFrame(frame):
        return False