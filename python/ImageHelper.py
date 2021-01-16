import cv2
import numpy as np

class ImageHelper:
    @staticmethod
    def let_it_float(image: np.ndarray) -> np.ndarray:
        new_image = image.astype(np.float32)
        dinfo = np.iinfo(image.dtype)
        new_image /= dinfo.max
        return new_image

    @staticmethod
    def make_it_char(image: np.ndarray) -> np.ndarray:
        image *= 255
        new_image = image.astype(np.uint8)
        return new_image