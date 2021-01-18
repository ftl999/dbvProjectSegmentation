from enum import Enum
from typing import Tuple, List, Dict
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
    def __init__(self) -> None:
        super().__init__()

    def __process__(self, sources: List[Tuple[str, Tuple[ResultType, object]]]) -> Tuple[ResultType, object]:
        raise Exception("Unimplemented!")

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return None

    def __get_settings__(self) -> dict:
        raise Exception("Unimplemented!")

    def __set_settings__(self, settings: dict):
        raise Exception("Unimplemented!")


class PipeStage(object):
    name: str = ""
    processors: List[PipeStageProcessor] = []
    in_stages: List[str] = []
    listeners: List[PipeStageListener]

    def __init__(self, name: str, processors: List[PipeStageProcessor], in_stages: List[str]):
        super().__init__()
        self.name = name
        self.listeners = []
        self.in_stages = in_stages
        self.processors = processors


class ProcessingPipe:
    # stage_name, processors, in_stages(sources named)
    __stages: List[PipeStage] = []
    __results: Dict[str, Tuple[ResultType, object]] = { "original": None }

    @staticmethod
    def addStage(name: str, processor: PipeStageProcessor, in_stages: List[str] = ["original"]):
        for stage in ProcessingPipe.__stages:
            if stage.name == name:
                stage.processors.append(processor)
                if len(in_stages) > 1 or in_stages[0] != "original":
                    raise Exception("You can't add new stages on a present pipe stage")
                return
        ProcessingPipe.__stages.append(PipeStage(name, [processor], in_stages))

    @staticmethod
    def process(image: np.ndarray = None, startAt: str = "") -> Tuple[ResultType, np.ndarray]:
        result = (ResultType.Image, image)
        renderSize = (result[1].shape[0], result[1].shape[1])
        if not (result is None):
            ProcessingPipe.__results["original"] = result
        processing = len(startAt) == 0
        for stage in ProcessingPipe.__stages:
            if not processing and stage != startAt:
                continue
            
            result = None
            res_img = None
            for listener in stage.listeners:
                listener.__onStartProcessing__(stage.name)
            for processor in stage.processors:
                try:
                    params = [(r, ProcessingPipe.__results[r]) for r in ProcessingPipe.__results.keys() if r in stage.in_stages]
                    if not (result is None):
                        params.append((stage.name, result))
                    result = processor.__process__(params)
                    ProcessingPipe.__results[stage.name] = result
                except Exception as e:
                    print("Error in processor: " + str(processor.__class__))
                    traceback.print_exc()
                    for listener in stage.listeners:
                        listener.__onProcessingError__(stage.name, str(e))
                    return result

                res_img = processor.__render__(result, renderSize)
            for listener in stage.listeners:
                listener.__onEndProcessing__(stage.name, res_img)

        return result

    @staticmethod
    def getStages() -> List[str]:
        return [stage.name for stage in ProcessingPipe.__stages]

    @staticmethod
    def registerListener(listener: PipeStageListener, stage_name: str = None):
        for stage in ProcessingPipe.__stages:
            if stage_name is None:
                stage.listeners.append(listener)
            else: 
                if stage_name == stage.name:
                    stage.listeners.append(listener)
                    break