import cv2
import numpy

from chestClass import chest
from chestManager import chestManager


class imageManager:
    def __init__(self, path):
        self.path = path

        self.imgScaledValues = {
            "startX": -2222,
            "endX": 860,
            "startY": -655,
            "endY": 1900
        }

        self.chestManager = chestManager()

    def readInputImage(self):
        # Reading an image in default mode
        self.originalImage = cv2.imread(self.path)

        cv2.imshow("Lootrunning", self.originalImage)

        cv2.waitKey(1)

    def setupDimensions(self):
        height, width, _ = self.originalImage.shape

        # Find the top left
        startTopLeft = None
        for y in range(height // 4):
            for x in range(width // 4):
                # The difference starts when the color is really dark
                if numpy.sum(self.originalImage[y, x]) < 200:
                    startTopLeft = (x, y)
                    break
            if startTopLeft is not None:
                break
        # Now top right
        startTopRight = None
        for x in range(width - 1, 0, -1):
            if numpy.sum(self.originalImage[startTopLeft[1], x]) < 200:
                startTopRight = (x, startTopLeft[1])
                break
            if startTopRight is not None:
                break

        # Now the bottom
        startBottomLeft = None
        for y in range(height - 1, 0, -1):
            if numpy.sum(self.originalImage[y, startTopLeft[0]]) < 200:
                startBottomLeft = (startTopLeft[0], y)
                break
            if startBottomLeft is not None:
                break

        # Last one
        startBottomRight = (startTopRight[0], startBottomLeft[1])

        rectangledImage = cv2.line(self.originalImage.copy(), startTopRight, startTopLeft, (0, 255, 0), 2)
        rectangledImage = cv2.line(rectangledImage, startTopRight, startBottomRight, (0, 255, 0), 2)
        rectangledImage = cv2.line(rectangledImage, startBottomRight, startBottomLeft, (0, 255, 0), 2)
        self.drawnImage = cv2.line(rectangledImage, startBottomLeft, startTopLeft, (0, 255, 0), 2)
        self.dimensions = {
            "start": startTopLeft,
            "width": startTopRight[0] - startTopLeft[0],
            "height": startBottomLeft[1] - startTopLeft[1]
        }

        cv2.imshow("Lootrunning", self.drawnImage)
        cv2.waitKey(1)

    def setupSpawn(self):
        for x in range(self.dimensions["start"][0], self.dimensions["start"][0] + self.dimensions["width"]):
            for y in range(self.dimensions["start"][1], self.dimensions["start"][1] + self.dimensions["height"]):
                bgr = self.originalImage[y, x]
                if bgr[2] > 240 and bgr[1] < 12 and bgr[0] < 12:
                    self.chestManager.addChest(x, y)
                    self.drawnImage[y, x] = (0, 0, 0)
        self.chestManager.calculateAverageChests()
        for chest in self.chestManager.chests:
            self.drawnImage = cv2.rectangle(self.drawnImage, (chest.avgX - 2, chest.avgY - 2),
                                            (chest.avgX + 2, chest.avgY + 2), (255, 0, 0), 2)
        self.chestManager.loadWaypoints(self.dimensions.copy(), self.imgScaledValues.copy())
        for waypoint in self.chestManager.waypoints:
            self.drawnImage = cv2.rectangle(self.drawnImage, (waypoint[0] - 2, waypoint[2] - 2),
                                            (waypoint[0] + 2, waypoint[2] + 2), (0, 255, 255), 1)
        cv2.imshow("Lootrunning", self.drawnImage)
        cv2.waitKey(1)

    def createGraph(self):
        # Start!
        self.chestManager.generateGraph()
        for waypoint in self.chestManager.chests:
            for connection in waypoint.graphs.preferedConnections:
                self.drawnImage = cv2.line(self.drawnImage, (waypoint.avgX, waypoint.avgY),
                                           (connection.reference.avgX, connection.reference.avgY), (255, 255, 255), 1)
        cv2.imshow("Lootrunning", self.drawnImage)
        cv2.waitKey(1)

    def calculatePath(self):
        self.drawnImage = self.chestManager.calculatePath(self.drawnImage.copy())
        cv2.imshow("Pathing done", self.drawnImage)
        cv2.waitKey(0)

