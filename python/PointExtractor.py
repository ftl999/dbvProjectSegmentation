import numpy as np

class PointExtractor(object):
    masked_image: np.ndarray = None

    def __init__(self, image: np.ndarray, mask: np.ndarray):
        self.masked_image = image * mask