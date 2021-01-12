import cv2, os
import numpy as np
import glob
 
img_array = []
path = input("Path: ")
size = (0,0)
for filename in glob.glob(path):
    img = cv2.imread(filename)
    height, width, layers = img.shape
    size = (width,height)
    img_array.append(img)

out = cv2.VideoWriter(os.path.join(path, 'project.mp4'),cv2.VideoWriter_fourcc(*'MPV'), 15, size)
 
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()