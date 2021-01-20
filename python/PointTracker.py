from ProcessingPipe import PipeStageProcessor, ResultType, StageType
from typing import Dict, Tuple
import numpy as np


class PointTracker(PipeStageProcessor):
    points: np.ndarray = None

    def __process__(self, sources: Dict[StageType, Tuple[ResultType, object]]) -> Tuple[ResultType, object]:
        old_points