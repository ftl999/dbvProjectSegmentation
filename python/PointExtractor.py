from operator import sub
import numpy as np
import cv2, math, os ,sys
from ImageHelper import ImageHelper
from typing import Tuple, List
from ProcessingPipe import PipeStageProcessor, ResultType

class PointExtractor(PipeStageProcessor):
    masked_image: np.ndarray = None
    points: np.ndarray = None
    points_per_subdivide: int = 1
    subdivide_area: int = 0
    __subdivides: int = 2
    __granularity: float = 1e-4
 
    def __init__(self, subdivides: int = 2, granularity: float = 1e-4):
        """
            :param int subdivides: number of divides of the selected object. Can enhance the extraction of points
            :param float granularity: defines how many points per pixels^2 should be extracted
        """
        super().__init__()
        self.__granularity = granularity
        self.__subdivides = subdivides
        if self.__subdivides <= 0:
            raise Exception("subdivides was too low!")

    def __process__(self, sources: List[Tuple[str, Tuple[ResultType, object]]]) -> Tuple[ResultType, object]:
        """
            :param sources: in color image and mask in some order
            :return: a list of good to track points
        """
        image = sources[0][1][1]
        mask = sources[1][1][1]
        image_float = ImageHelper.let_it_float(image)
        mask_float = ImageHelper.let_it_float(mask)
        self.masked_image = image_float * mask_float
        gray_mask = cv2.cvtColor(self.masked_image, cv2.COLOR_BGR2GRAY)
        num_masked_pixels = cv2.findNonZero(gray_mask).shape[0]
        self.points = np.zeros((0,1,2), dtype=np.uint64)
        rect = cv2.boundingRect(cv2.findNonZero(gray_mask))
        width = rect[2]
        height = rect[3]
        x_step = int(width / self.__subdivides)
        y_step = int(height / self.__subdivides)
        self.subdivide_area = x_step * y_step
        self.points_per_subdivide = max(1, int(self.subdivide_area * self.__granularity))
        
        for p in range(self.__subdivides ** 2):
            col = (p % self.__subdivides)
            row = int(p / self.__subdivides)
            min_x = int(col * x_step + rect[0])
            min_y = int(row * y_step + rect[1])
            max_x = min_x + x_step
            max_y = min_y + y_step
            new_rects = self.__do_extraction(((min_y, min_x), (max_y, max_x)))
            self.points = np.concatenate((self.points, new_rects), axis=0)
        
        self.finalize()
        return (ResultType.PointsArray, self.points)

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        image = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        image = self.renderPoints(image, result[1])
        cv2.imshow("Points", image)
        cv2.waitKey(50000)
        return image

    def __do_extraction(self, box: Tuple[Tuple[int, int], Tuple[int, int]]) -> np.ndarray:
        subMask = np.zeros(self.masked_image.shape, dtype=self.masked_image.dtype)
        for y in range(box[0][0], box[1][0] + 1):
            for x in range(box[0][1], box[1][1] + 1):
                subMask[y, x] = self.masked_image[y, x]

        gray_mask = cv2.cvtColor(subMask, cv2.COLOR_BGR2GRAY)
        min_dist = int(math.sqrt(self.subdivide_area / self.points_per_subdivide) / 2.0)
        return np.int0(cv2.goodFeaturesToTrack(gray_mask, self.points_per_subdivide, 0.01, min_dist, useHarrisDetector=True))

    def finalize(self):
        min_dist = int(math.sqrt(self.subdivide_area / self.points_per_subdivide) / 2.0) * 0.9
        idx_for_deletion = []
        for i in range(self.points.shape[0]):
            for j in range(i + 1, self.points.shape[0]):
                pi = self.points[i][0]
                pj = self.points[j][0]
                dist = math.sqrt((pi[0] - pj[0]) ** 2 + (pi[1] - pj[1]) ** 2)
                if dist < min_dist:
                    idx_for_deletion.append(j)

        idx_for_deletion = list(set(idx_for_deletion)) # make all indexes unique
        idx_for_deletion.sort(reverse=True)
        for i in idx_for_deletion:
            self.points = np.delete(self.points, i, axis=0)
        
        
    def renderPoints(self, image: np.ndarray, points: np.ndarray, track_block_size: int = 10):
        outer_color = (0,0,255)
        inner_color = (255,0,0)
        for i in points:
            x,y = i.ravel()
            image = cv2.circle(image, (int(x), int(y)), track_block_size, outer_color, 1)
            image = cv2.circle(image, (int(x), int(y)), 3, inner_color, -1)
        return image

    def __get_settings__(self) -> dict:
        return {
            "subdivides": self.__subdivides,
            "granularity": self.__granularity
        }

    def __set_settings__(self, settings: dict):
        self.__subdivides = settings["subdivides"]
        self.__granularity = settings["granularity"]


if __name__ == "__main__":
    frame = cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Screenshot.png"))
    mask = cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Mask.png"))
    pe1 = PointExtractor(frame, mask)
    pointedImage = pe1.renderPoints(frame)
    cv2.imshow("Points", pointedImage)
    #cv2.imshow("Masked", pe1.masked_image)
    cv2.waitKey(50000)