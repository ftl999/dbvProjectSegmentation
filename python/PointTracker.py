from ProcessingPipe import PipeStageProcessor, ResultType, StageType, InactivePipeStageException
from typing import Dict, Tuple, List
import numpy as np
import cv2
from matplotlib import pyplot as plt

class PointTracker(PipeStageProcessor):
    points: np.ndarray = None
    kalman: cv2.KalmanFilter = None
    regionSize: int = 3
    old_hists: List[np.ndarray] = []
    
    def __init__(self, regionSize = 3):
        super().__init__()
        self.regionSize = regionSize
        self.old_hists = []
        self.kalman = cv2.KalmanFilter(4, 2)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                                [0, 1, 0, 0]], np.float32)

        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                                [0, 1, 0, 1],
                                                [0, 0, 1, 0],
                                                [0, 0, 0, 1]], np.float32)

        self.kalman.processNoiseCov = np.array([[1, 0, 0, 0],
                                                [0, 1, 0, 0],
                                                [0, 0, 1, 0],
                                                [0, 0, 0, 1]], np.float32) * 0.03

        self.measurement = np.array((2, 1), np.float32)
        self.prediction = np.zeros((2, 1), np.float32)
        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        

    def __process__(self, sources: Dict[StageType, Tuple[ResultType, object]]) -> Tuple[ResultType, object]:
        old_points = None
        image = sources[StageType.Video][1]
        if StageType.PointTracking in sources.keys():
            old_points = sources[StageType.PointTracking][1]
        else:
            if StageType.PointExtraction in sources.keys():
                old_points = sources[StageType.PointExtraction][1]
            else:
                raise InactivePipeStageException()
        
        self.old_hists = []
        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        #cv2.imshow("img_hsv", img_hsv)
        #cv2.waitKey(5000)
        predictedPoints = []
        for p in old_points:
            x,y = p.ravel()
            p = (x, y)
            try:
                region = self.getRegion(image, p)
                hist = self.getHist(region)
                self.old_hists.append(hist)
            
                img_bproject = cv2.calcBackProject(
                    [img_hsv], [
                        0, 1], hist, [
                        0, 180, 0, 255], 1)
                track_window = (
                    int(p[0]) - int(self.regionSize / 2),
                    int(p[1]) - int(self.regionSize / 2),
                    self.regionSize,
                    self.regionSize
                )
                ret, track_window = cv2.meanShift(img_bproject, track_window, self.term_crit)
                x, y, w, h = track_window
                #image_track_window = cv2.rectangle(image, track_window,(0,255,0),3)
                #cv2.imshow("Track Window", image_track_window)
                #cv2.waitKey(1)

                #pts = cv2.boxPoints(ret)
                pts = [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
                pts = np.int0(pts)
                self.kalman.correct(self.getCenter(pts))
            except Exception as e:
                print("Tracker Exception in point: " + str(p) + " -> " + str(e))
            finally:
                prediction = self.kalman.predict()
                if prediction[0] < 0 or prediction[0] > image.shape[1]:
                    prediction[0] = p[0]
                if prediction[1] < 0 or prediction[1] > image.shape[0]:
                    prediction[1] = p[1]
                predictedPoints.append([int(prediction[0]), int(prediction[1])])

        return (ResultType.PointsArray, np.int0(predictedPoints))

    def getCenter(self, pts: np.ndarray) -> np.ndarray:
        x = 0.0
        y = 0.0
        for p in pts:
            x = x + p[0]
            y = y + p[1]
        
        x = x / pts.shape[0]
        y = y / pts.shape[0]
        return np.array([np.float32(x), np.float32(y)], np.float32)

    def __render__(self, result: Tuple[ResultType, object], size: Tuple[int, int]) -> np.ndarray:
        image = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        for p in result[1]:
            x,y = p.ravel()
            image = cv2.circle(image, (int(x), int(y)), self.regionSize,(0,255,0),2)
        return image      

    def getRegion(self, frame: np.ndarray, point: np.ndarray) -> np.ndarray:
        crop = frame[int(point[1]) - int(self.regionSize / 2):int(point[1]) + int(self.regionSize / 2) + 1,
                       int(point[0]) - int(self.regionSize / 2):int(point[0]) + int(self.regionSize / 2) + 1].copy()
        hsv_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        return hsv_crop

    def getHist(self, region: np.ndarray) -> np.ndarray:
        # construct a histogram of hue and saturation values and
        # normalize it

        mask = cv2.inRange(
            region, np.array(
                (0., float(20), float(20))), np.array(
                (180., float(200), float(200))))

        crop_hist = cv2.calcHist(
            [region], [0, 1], mask, [
                180, 255], [0, 180, 0, 255])
        cv2.normalize(crop_hist, crop_hist, 0, 255, cv2.NORM_MINMAX)

        #plt.hist(crop_hist)
        #plt.show()
        return crop_hist
        
