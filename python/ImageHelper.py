import cv2
import numpy as np
from ProcessingPipe import PipeStageProcessor, ResultType, StageType
from typing import Tuple, Dict

class ImageHelper:
    @staticmethod
    def let_it_float(image: np.ndarray) -> np.ndarray:
        if isinstance(image.dtype, np.float32):
            return image

        new_image = image.astype(np.float32)
        dinfo = np.iinfo(image.dtype)
        new_image /= dinfo.max
        return new_image

    @staticmethod
    def make_it_char(image: np.ndarray) -> np.ndarray:
        image *= 255
        new_image = image.astype(np.uint8)
        return new_image

    @staticmethod
    def make_it_gray(image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

class ImageFloaterStage(PipeStageProcessor):
    def __init__(self) -> None:
        super().__init__()

    def __process__(self, sources: Dict[StageType, Tuple[ResultType, object]]) -> Tuple[ResultType, object]:
        img = sources[sources.keys()[0]][1]
        return (ResultType.Image, ImageHelper.let_it_float(img))


class StaticImageInputStage(PipeStageProcessor):
    image: np.ndarray = None

    def __init__(self, image: np.ndarray) -> None:
        super().__init__()
        self.image = image

    def __process__(self, sources: Dict[StageType, Tuple[ResultType, object]]) -> Tuple[ResultType, object]:
        return (ResultType.Image, self.image)

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return self.image