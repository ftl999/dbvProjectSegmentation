from enum import Enum
from typing import Tuple, List, Dict
import numpy as np
import traceback
import threading
import queue

class StageType(Enum):
    Video = 0
    Segmentation = 1
    PointExtraction = 2
    PointTracking = 3
    Skeletonize = 4

class PipeStageListener:
    def __onStartProcessing__(self, stage: StageType):
        pass

    def __onEndProcessing__(self, stage: StageType, result: np.ndarray):
        pass

    def __onProcessingError__(self, stage: StageType, error: str):
        pass


class ResultType(Enum):
    Image = 0
    PointsArray = 1


class InactivePipeStageException(Exception):
    def __str__(self):
        return "InactivePipeStageException: " + super().__str__()

class PipeStageProcessor(object):
    def __init__(self) -> None:
        super().__init__()

    def __process__(self, sources: List[Tuple[StageType, Tuple[ResultType, object]]]) -> Tuple[ResultType, object]:
        raise Exception("Unimplemented!")

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        return None

    def __get_settings__(self) -> dict:
        raise Exception("Unimplemented!")

    def __set_settings__(self, settings: dict):
        raise Exception("Unimplemented!")


class PipeStage(object):
    name: StageType = None
    processors: List[PipeStageProcessor] = []
    in_stages: List[StageType] = []
    listeners: List[PipeStageListener]

    def __init__(self, name: StageType, processors: List[PipeStageProcessor], in_stages: List[StageType]):
        super().__init__()
        self.name = name
        self.listeners = []
        self.in_stages = in_stages
        self.processors = processors


class ProcessingPipe:
    # stage_name, processors, in_stages(sources named)
    __stages: List[PipeStage] = []
    __results: Dict[StageType, Tuple[ResultType, object]] = { }
    __isRunning: bool = False
    __lock = threading.Lock()
    __queue = queue.Queue()

    @staticmethod
    def reset():
        while not ProcessingPipe.__queue.empty():
            try:
                ProcessingPipe.__queue.get(False)
            except queue.Empty:
                continue

    @staticmethod
    def addStage(name: StageType, processor: PipeStageProcessor, in_stages: List[StageType] = []):
        for stage in ProcessingPipe.__stages:
            if stage.name == name:
                stage.processors.append(processor)
                if len(in_stages) > 1:
                    raise Exception("You can't add new stages on a present pipe stage")
                return
        ProcessingPipe.__stages.append(PipeStage(name, [processor], in_stages))

    @staticmethod
    def process(partialProcess: List[StageType] = None):
        ProcessingPipe.__lock.acquire()
        if ProcessingPipe.__isRunning == False:
            ProcessingPipe.__isRunning = True
            ProcessingPipe.__queue.put(lambda: ProcessingPipe.__process(partialProcess))
            callback = ProcessingPipe.__queue.get(False)
            threading.Thread(target=lambda: callback()).start()
        else:
            ProcessingPipe.__queue.put(lambda: ProcessingPipe.__process(partialProcess))
        ProcessingPipe.__lock.release()

    @staticmethod
    def __process(partialProcess: List[StageType] = None) -> Tuple[ResultType, np.ndarray]:
        result = (ResultType.Image, None)
        try:
            renderSize = None
            if not (result is None):
                ProcessingPipe.__results[StageType(0)] = result
            processing = (partialProcess is None)
            lastStage = StageType(0)
            for stage in ProcessingPipe.__stages:
                if not processing and not (stage.name in partialProcess):
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
                        if renderSize is None and result[0] == ResultType.Image:
                            renderSize = (result[1].shape[0], result[1].shape[1])
                        ProcessingPipe.__results[stage.name] = result
                    except InactivePipeStageException as e:
                        # end processing if inactive
                        result = ProcessingPipe.__results[lastStage]
                        raise Exception()
                    except Exception as e:
                        print("Error in processor: " + str(processor.__class__))
                        traceback.print_exc()
                        for listener in stage.listeners:
                            listener.__onProcessingError__(stage.name, str(e))
                        raise Exception()

                    res_img = processor.__render__(result, renderSize)
                    for listener in stage.listeners:
                        listener.__onEndProcessing__(stage.name, res_img)
                lastStage = stage.name
        except Exception as e:
            pass
        finally:
            try:
                callback = ProcessingPipe.__queue.get(False)
                callback()
            except queue.Empty:
                ProcessingPipe.__lock.acquire()
                ProcessingPipe.__isRunning = False
                ProcessingPipe.__lock.release()
        return result

    @staticmethod
    def getStages() -> List[str]:
        return [stage.name for stage in ProcessingPipe.__stages]

    @staticmethod
    def getStageByName(name: StageType) -> PipeStage:
        for stage in ProcessingPipe.__stages:
            if stage.name == name:
                return stage
        return None

    @staticmethod
    def registerListener(listener: PipeStageListener, stage_name: str = None):
        for stage in ProcessingPipe.__stages:
            if stage_name is None:
                stage.listeners.append(listener)
            else: 
                if stage_name == stage.name:
                    stage.listeners.append(listener)
                    break