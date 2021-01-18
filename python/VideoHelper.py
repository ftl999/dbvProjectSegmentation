from ProcessingPipe import PipeStageProcessor, ResultType
import cv2
import numpy as np
from typing import Tuple, List

class FileVideoInputStage(PipeStageProcessor):
    cap: cv2.VideoCapture = None
    frame: np.ndarray = None

    def __init__(self, file: str) -> None:
        super().__init__()
        self.cap = cv2.VideoCapture(file)

    def __process__(self, sources: List[Tuple[str, Tuple[ResultType, object]]]) -> Tuple[ResultType, object]:
        ret, self.frame = self.cap.read()
        return (ResultType.Image, self.frame)

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return self.frame