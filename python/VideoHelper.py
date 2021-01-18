from ProcessingPipe import PipeStageProcessor, ResultType, InactivePipeStageException
import cv2
import numpy as np
from typing import Tuple, List

class FileVideoInputStage(PipeStageProcessor):
    cap: cv2.VideoCapture = None
    frame: np.ndarray = None

    def __init__(self, file: str = None, startFrameIdx: int = 0) -> None:
        super().__init__()
        if not (file is None):
            self.cap = cv2.VideoCapture(file)
            for i in range(startFrameIdx):
                self.__process__()
        else:
            self.cap = None

    def __process__(self, sources: List[Tuple[str, Tuple[ResultType, object]]]) -> Tuple[ResultType, object]:
        if self.cap is None:
            raise InactivePipeStageException()
        ret, self.frame = self.cap.read()
        return (ResultType.Image, self.frame)

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return self.frame