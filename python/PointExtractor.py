import numpy as np
import cv2, math, os ,sys

from numpy.core.numeric import outer
from ImageHelper import ImageHelper
from typing import Tuple

class PointExtractor(object):
    masked_image: np.ndarray = None
    points: np.ndarray = None
    points_per_subdivide: int = 1
    subdivide_area: int = 0
 
    def __init__(self, image: np.ndarray, mask: np.ndarray, subdivides: int = 2, granularity: float = 1e-4):
        """
            :param np.ndarray image: in color image
            :param np.ndarray mask: in b/w image mask that selects area to extract points from
            :param int subdivides: number of divides of the selected object. Can enhance the extraction of points
            :param float granularity: defines how many points per pixels^2 should be extracted
        """
        image_float = ImageHelper.let_it_float(image)
        mask_float = ImageHelper.let_it_float(mask)
        self.masked_image = image_float * mask_float
        #self.masked_image = ImageHelper.make_it_char(self.masked_image)
        gray_mask = cv2.cvtColor(self.masked_image, cv2.COLOR_BGR2GRAY)
        num_masked_pixels = cv2.findNonZero(gray_mask).shape[0]
        self.points = np.zeros((0,1,2), dtype=np.uint64)
        rect = cv2.boundingRect(cv2.findNonZero(gray_mask))
        width = rect[2]
        height = rect[3]
        x_step = int(width / subdivides)
        y_step = int(height / subdivides)
        self.subdivide_area = x_step * y_step
        self.points_per_subdivide = max(1, int(self.subdivide_area * granularity))
        
        if subdivides <= 0:
            raise Exception("subdivides was too low!")
        for p in range(subdivides ** 2):
            col = (p % subdivides)
            row = int(p / subdivides)
            min_x = int(col * x_step + rect[0])
            min_y = int(row * y_step + rect[1])
            max_x = min_x + x_step
            max_y = min_y + y_step
            new_rects = self.__do_extraction(((min_y, min_x), (max_y, max_x)))
            self.points = np.concatenate((self.points, new_rects), axis=0)

    def __do_extraction(self, box: Tuple[Tuple[int, int], Tuple[int, int]]) -> np.ndarray:
        subMask = np.zeros(self.masked_image.shape, dtype=self.masked_image.dtype)
        for y in range(box[0][0], box[1][0] + 1):
            for x in range(box[0][1], box[1][1] + 1):
                subMask[y, x] = self.masked_image[y, x]

        gray_mask = cv2.cvtColor(subMask, cv2.COLOR_BGR2GRAY)
        min_dist = int(math.sqrt(self.subdivide_area / self.points_per_subdivide) / 2.0)
        return np.int0(cv2.goodFeaturesToTrack(gray_mask, self.points_per_subdivide, 0.01, min_dist, useHarrisDetector=True))
        
        
    def renderPoints(self, image: np.ndarray, track_block_size: int = 10):
        outer_color = (0,0,255)
        inner_color = (255,0,0)
        for i in self.points:
            x,y = i.ravel()
            image = cv2.circle(image, (int(x), int(y)), track_block_size, outer_color, 1)
            image = cv2.circle(image, (int(x), int(y)), 3, inner_color, -1)
        return image







if __name__ == "__main__":
    frame = cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Screenshot.png"))
    mask = cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Mask.png"))
    pe1 = PointExtractor(frame, mask)
    pointedImage = pe1.renderPoints(frame)
    cv2.imshow("Points", pointedImage)
    #cv2.imshow("Masked", pe1.masked_image)
    cv2.waitKey(50000)