from ProcessingPipe import PipeStageProcessor, ResultType, InactivePipeStageException, StageType
import cv2
import numpy as np
from typing import Tuple, Dict

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

    def __process__(self, sources: Dict[StageType, Tuple[ResultType, object]]) -> Tuple[ResultType, object]:
        if self.cap is None:
            raise InactivePipeStageException()
        ret, self.frame = self.cap.read()
        return (ResultType.Image, self.frame)

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return self.frame

class VideoCubeStage(PipeStageProcessor):
    def __init__(self):
        super().__init__()
        self.framenumber = 0

    def __process__(self, sources: Dict[StageType, Tuple[ResultType, object]]) -> Tuple[ResultType, object]:

        newFrame = self.videocube[self.framenumber]
        if self.framenumber >= self.frameCount-1:
            raise InactivePipeStageException()
        self.framenumber = self.framenumber+1
        return (ResultType.Image, newFrame)#, self.frameMasks[self.framenumber])

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return self.videocube[self.framenumber]

    def loadVideo(self, file_path:str):
        cap = cv2.VideoCapture(file_path)#('190301_02_KenyaWildlife_29_Trim.mp4')
        self.frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        buffer = np.empty((self.frameCount, self.frameHeight, self.frameWidth, 3), np.dtype('uint8'))  #shape: (161, 1080, 1920, 3)
        fc = 0
        ret = True
        while (fc < self.frameCount  and ret):
            ret, buffer[fc] = cap.read()
            fc += 1
        self.videocube = buffer
        cap.release()

