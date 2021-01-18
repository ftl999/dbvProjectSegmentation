from GUI import GUI
from ImagePipe import ImagePipe
from ImageHelper import StaticImageInputStage
import cv2, os, sys
from PointExtractor import PointExtractor

if __name__ == "__main__":
    ImagePipe.addStage("Segmentation", StaticImageInputStage(cv2.imread(os.path.join(os.path.dirname(sys.argv[0]), "Mask.png"))))
    ImagePipe.addStage("PointsExtraction", PointExtractor(), ["original", "Segmentation"])
    gui = GUI()