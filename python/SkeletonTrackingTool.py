from PointTracker import PointTracker
from VideoHelper import FileVideoInputStage
from GUI import GUI
from ProcessingPipe import ProcessingPipe
from ImageHelper import StaticImageInputStage
import cv2, os, sys
from PointExtractor import PointExtractor

if __name__ == "__main__":
    ProcessingPipe.addStage("Segmentation", StaticImageInputStage(cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Mask.png"))))
    ProcessingPipe.addStage("PointsExtraction", PointExtractor(), ["original", "Segmentation"])
    ProcessingPipe.addStage("VideoIn", FileVideoInputStage())
    ProcessingPipe.addStage("PointsTracking", PointTracker(), ["PointsExtraction", "VideoIn"])
    gui = GUI()