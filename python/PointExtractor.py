import numpy as np
import cv2, math, os ,sys
from ImageHelper import ImageHelper
from typing import Tuple

class PointExtractor(object):
    masked_image: np.ndarray = None
    points: np.ndarray = None

    def __init__(self, image: np.ndarray, mask: np.ndarray, num_parts: int = 4):
        image_float = ImageHelper.let_it_float(image)
        mask_float = ImageHelper.let_it_float(mask)
        self.masked_image = image_float * mask_float
        #self.masked_image = ImageHelper.make_it_char(self.masked_image)
        gray_mask = cv2.cvtColor(self.masked_image, cv2.COLOR_BGR2GRAY)
        num_masked_pixels = cv2.findNonZero(gray_mask).shape[0]
        self.points = np.zeros((0,1,2), dtype=np.uint64)
        rect = cv2.boundingRect(cv2.findNonZero(gray_mask))
        i = self.masked_image.copy()
        width = rect[2]
        height = rect[3]
        sqr = int(math.sqrt(num_parts))
        x_step = int(width / sqr)
        y_step = int(height / sqr)
        for p in range(num_parts):
            if sqr <= 0:
                raise Exception("num_parts was too low!")
            col = (p % sqr)
            row = int(p / sqr)
            min_x = int(col * x_step + rect[0])
            min_y = int(row * y_step + rect[1])
            max_x = min_x + x_step
            max_y = min_y + y_step
            new_rects = self.__do_extraction(((min_y, min_x), (max_y, max_x)))
            self.points = np.concatenate((self.points, new_rects), axis=0)

        cv2.imshow("bb", i)
        cv2.waitKey(5000)

    def __do_extraction(self, box: Tuple[Tuple[int, int], Tuple[int, int]]) -> np.ndarray:
        subMask = np.zeros(self.masked_image.shape, dtype=self.masked_image.dtype)
        for y in range(box[0][0], box[1][0] + 1):
            for x in range(box[0][1], box[1][1] + 1):
                subMask[y, x] = self.masked_image[y, x]

        gray_mask = cv2.cvtColor(subMask, cv2.COLOR_BGR2GRAY)
        return np.int0(cv2.goodFeaturesToTrack(gray_mask, 25, 0.01, 10, useHarrisDetector=True))
        
        
    def renderPoints(self, image: np.ndarray):
        for i in self.points:
            x,y = i.ravel()
            cv2.circle(image,(int(x),int(y)),3,255,-1)
        return image







if __name__ == "__main__":
    frame = cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Screenshot.png"))
    mask = cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Mask.png"))
    pe1 = PointExtractor(frame, mask)
    pointedImage = pe1.renderPoints(frame)
    cv2.imshow("Points", pointedImage)
    cv2.imshow("Masked", pe1.masked_image)
    cv2.waitKey(50000)