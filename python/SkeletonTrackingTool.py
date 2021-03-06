from PointTracker import PointTracker
from VideoHelper import VideoCubeStage
from SegmentationStage import SegmentationStage, ClosingOperation
from GUI import GUI
from ProcessingPipe import ProcessingPipe, StageType
from ImageHelper import StaticImageInputStage
import cv2, os, sys
from PointExtractor import PointExtractor

if __name__ == "__main__":
    ProcessingPipe.addStage(StageType.Video, VideoCubeStage())
    ProcessingPipe.addStage(StageType.Segmentation, SegmentationStage(), [StageType.Video])
    ProcessingPipe.addStage(StageType.Segmentation, ClosingOperation())
#StaticImageInputStage(cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Mask.png"))))
    ProcessingPipe.addStage(StageType.PointExtraction, PointExtractor(), [StageType.Video, StageType.Segmentation])
    ProcessingPipe.addStage(StageType.PointTracking, PointTracker(60), [StageType.PointExtraction, StageType.Video, StageType.PointTracking])
    
    gui = GUI()
