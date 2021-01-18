from enum import Enum
from typing import Tuple, List
import numpy as np
import traceback

class PipeStageListener:
    def __onStartProcessing__(self, stage: str):
        pass

    def __onEndProcessing__(self, stage: str, result: np.ndarray):
        pass

    def __onProcessingError__(self, stage: str, error: str):
        pass

class ResultType(Enum):
    Image = 0
    PointsArray = 1

class PipeStageProcessor(object):
    listeners: List[PipeStageListener]

    def __init__(self) -> None:
        super().__init__()
        self.listeners = []

    def __process__(self, sources: List[Tuple[str, Tuple[ResultType, object]]]) -> Tuple[ResultType, object]:
        raise Exception("Unimplemented!")

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return None

    def __get_settings__(self) -> dict:
        raise Exception("Unimplemented!")

    def __set_settings__(self, settings: dict):
        raise Exception("Unimplemented!")


class ImagePipe:
    # stage_name, processor, in_stages(sources named)
    __stages: List[Tuple[str, PipeStageProcessor, List[str]]] = []
    __results = { "original": None }

    @staticmethod
    def addStage(name: str, processor: PipeStageProcessor, in_stages: List[str] = ["original"]):
        ImagePipe.__stages.append((name, processor, in_stages))

    @staticmethod
    def process(image: np.ndarray = None, startAt: str = "") -> Tuple[ResultType, np.ndarray]:
        result = (ResultType.Image, image)
        renderSize = (result[1].shape[0], result[1].shape[1])
        if not (result is None):
            ImagePipe.__results["original"] = result
        processing = len(startAt) == 0
        for stage in ImagePipe.__stages:
            if not processing and stage != startAt:
                continue

            for listener in stage[1].listeners:
                listener.__onStartProcessing__(stage[0])
            try:
                result = stage[1].__process__([(r, ImagePipe.__results[r]) for r in ImagePipe.__results.keys() if r in stage[2]])
                ImagePipe.__results[stage[0]] = result
            except Exception as e:
                traceback.print_exc()
                for listener in stage[1].listeners:
                    listener.__onProcessingError__(stage[0], str(e))
                break
            res_img = stage[1].__render__(result, renderSize)
            for listener in stage[1].listeners:
                listener.__onEndProcessing__(stage[0], res_img)
        return result

    @staticmethod
    def getStages() -> List[str]:
        return [stage[0] for stage in ImagePipe.__stages]

    @staticmethod
    def registerListener(listener: PipeStageListener):
        for stage in ImagePipe.__stages:
            stage[1].listeners.append(listener)
            break