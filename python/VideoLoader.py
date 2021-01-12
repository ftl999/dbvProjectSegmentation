import cv2 as cv
import numpy as np
import time
from collections import namedtuple

import ObjectSegmenter
videoObj = namedtuple('videoObj', 'frameRate frameArr')

def loadVideo(filename):
    
    cap = cv.VideoCapture(filename)
    numFrames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    
    frameArr = np.empty((numFrames, frameHeight, frameWidth, 3), np.dtype('uint8'))

    i = 0
    ret = True

    while (i < numFrames  and ret):
        ret, frameArr[i] = cap.read()
        i += 1
        
    videoObj1 = videoObj(frameRate=30,frameArr=frameArr)
    cap.release()
    return videoObj1

def showVideo(videoObj1):
    for frame in videoObj1.frameArr:
        cv.imshow('Video', frame)
        cv.waitKey(1)
        time.sleep(1/videoObj1.frameRate)



def main():
    videoObj1 = loadVideo("190301_02_KenyaWildlife_29_Trim.mp4")
    os = ObjectSegmenter(videoObj1.frameArr[0])
    showVideo(videoObj1)


main()