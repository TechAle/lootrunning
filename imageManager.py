import cv2
import numpy

from chestManager import chestManager


class imageManager:
    def __init__(self, path):
        self.nonCompletedLines = None
        self.path = path

        # The real scaled values of the map
        self.imgScaledValues = {
            "startX": -2222,
            "endX": 860,
            "startY": -655,
            "endY": 1900
        }

        # Needed for restrictions
        self.subGroup = {
            "points": [],
            "start": [],
            "end": []
        }

        # The manager of every location of every chest
        self.chestManager = chestManager()

    '''
        This function is needed for creating restrictions
        This manage the click of the button on the image
    '''
    def click_event(self, event, x, y, flags, params):
        # Creating the area
        if event == cv2.EVENT_LBUTTONDOWN:
            add = True
            isZero = False
            if self.subGroup["points"].__len__() > 0:
                # If the point is near the start
                if self.subGroup["points"][0][0] - 10 < x < self.subGroup["points"][0][0] + 10 \
                        and self.subGroup["points"][0][1] - 10 < y < self.subGroup["points"][0][1] + 10:
                    self.chestManager.addNewSubgroup(self.subGroup)
                    add = False
                    self.createSubgroupLines()
                    self.nonCompletedLines = self.completedLines.copy()
                    self.subGroup.clear()
            else:
                # For the first point we do not want to draw a line
                isZero = True

            # If we have to add it
            if add:
                self.subGroup["points"].append((x, y))
                # If we alr had something before
                if not isZero:
                    self.nonCompletedLines = cv2.line(self.nonCompletedLines, (x, y),
                                                      (self.subGroup["points"][-2][0], self.subGroup["points"][-2][1]), (120, 120, 120), 2)
                    cv2.imshow("Lootrunning", self.nonCompletedLines)
        # Make points from start->end->remove
        elif event == cv2.EVENT_RBUTTONDOWN:
            pass

    '''
        This function create the map 
    '''
    def createSubgroupLines(self):
        # We iterate to -1 because we dont want to go out of the array
        for i in range(len(self.subGroup["points"]) - 1):
            self.completedLines = cv2.line(self.completedLines, (self.subGroup["points"][i][0], self.subGroup["points"][i][1]),
                                           (self.subGroup["points"][i + 1][0], self.subGroup["points"][i + 1][1]), (255, 120, 0), 3)
        # Draw the first line
        self.completedLines = cv2.line(self.completedLines, (self.subGroup["points"][0][0], self.subGroup["points"][0][1]),
                                       (self.subGroup["points"][-1][0], self.subGroup["points"][-1][1]), (255, 120, 0), 2)
        # Draw a circle in every node we start
        for start in self.subGroup["start"]:
            self.completedLines = cv2.circle(self.completedLines, (start[0], start[1]), 5,
                                             (255, 0, 0), 2)
        # Draw a circle in every node we end
        for end in self.subGroup["end"]:
            self.completedLines = cv2.circle(self.completedLines, (end[0], end[1]), 5,
                                             (0, 0, 255), 2)
        cv2.imshow("Lootrunning", self.completedLines)

    '''
        This function just setup the starting picture, and events
    '''
    def readInputImage(self):
        # Reading an image in default mode
        self.originalImage = cv2.imread(self.path)

        cv2.imshow("Lootrunning", self.originalImage)

        # Mouse event setup
        cv2.setMouseCallback('Lootrunning',
                             lambda event, x, y, flags, params: self.click_event(event, x, y, flags, params))

        cv2.waitKey(1)

    '''
        This setup the dimensions of the image, in particular
        Try to understand where the map starts and where it ends
    '''
    def setupDimensions(self):
        height, width, _ = self.originalImage.shape

        # Find the top left part
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

        # Create a rectangle all around the image for debugging purpose
        rectangledImage = cv2.line(self.originalImage.copy(), startTopRight, startTopLeft, (0, 255, 0), 2)
        rectangledImage = cv2.line(rectangledImage, startTopRight, startBottomRight, (0, 255, 0), 2)
        rectangledImage = cv2.line(rectangledImage, startBottomRight, startBottomLeft, (0, 255, 0), 2)
        self.drawnImage = cv2.line(rectangledImage, startBottomLeft, startTopLeft, (0, 255, 0), 2)
        # Make the output avaible for everyone
        self.dimensions = {
            "start": startTopLeft,
            "width": startTopRight[0] - startTopLeft[0],
            "height": startBottomLeft[1] - startTopLeft[1]
        }

        # Display the image
        cv2.imshow("Lootrunning", self.drawnImage)
        cv2.waitKey(1)

    '''
        Find every red parts in the picture, that is the location we need
        And then load every waypoint.
    '''
    def setupSpawn(self):
        # Find every red pixel
        for x in range(self.dimensions["start"][0], self.dimensions["start"][0] + self.dimensions["width"]):
            for y in range(self.dimensions["start"][1], self.dimensions["start"][1] + self.dimensions["height"]):
                bgr = self.originalImage[y, x]
                # Range for the color of red
                if bgr[2] > 240 and bgr[1] < 12 and bgr[0] < 12:
                    # By adding every red pixels, it also merge every red pixels that are close by
                    self.chestManager.addChest(x, y)
                    self.drawnImage[y, x] = (0, 0, 0)
        # Get the center of the area of every red part
        self.chestManager.calculateAverageChests()
        # Display everything
        for chest in self.chestManager.chests:
            self.drawnImage = cv2.rectangle(self.drawnImage, (chest.avgX - 2, chest.avgY - 2),
                                            (chest.avgX + 2, chest.avgY + 2), (255, 0, 0), 2)
        # Now loads every waypoint we have in the file
        self.chestManager.loadWaypoints(self.dimensions.copy(), self.imgScaledValues.copy())
        # And display it
        for waypoint in self.chestManager.waypoints:
            self.drawnImage = cv2.rectangle(self.drawnImage, (waypoint[0] - 2, waypoint[2] - 2),
                                            (waypoint[0] + 2, waypoint[2] + 2), (0, 255, 255), 1)
        cv2.imshow("Lootrunning", self.drawnImage)
        cv2.waitKey(1)

    '''
        Create the graph from every node
    '''
    def createGraph(self):
        # Connect every node, and so create a graph
        self.chestManager.generateGraph()
        # After, show every connection we made
        for waypoint in self.chestManager.chests:
            for connection in waypoint.graphs.preferedConnections:
                self.drawnImage = cv2.line(self.drawnImage, (waypoint.avgX, waypoint.avgY),
                                           (connection.reference.avgX, connection.reference.avgY), (255, 255, 255), 1)
        cv2.imshow("Lootrunning", self.drawnImage)
        cv2.waitKey(1)

    # This start the calculation of the best path
    def calculatePath(self):
        #self.drawnImage = self.chestManager.calculateGreedyBruteforce(self.drawnImage.copy())
        self.drawnImage = self.chestManager.calculateAntAlgorithm(self.drawnImage.copy())
        cv2.imshow("Lootrunning", self.drawnImage)
        cv2.waitKey(0)

    '''
        Main function for creating restrictions
    '''
    def createRestrictions(self):
        # Backup of everything for displaying things
        self.nonCompletedLines = self.drawnImage.copy()
        self.completedLines = self.nonCompletedLines.copy()
        print("Press enter when you have finished\n")
        while True:
            k = cv2.waitKey(10) & 0xff
            # Code for the enter key
            if k == 13:
                break
        # Last part, this creates the last group with everything else
        self.chestManager.finishSubGroup()
