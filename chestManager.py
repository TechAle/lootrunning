import sys

import cv2

from chestClass import chest
from sortedcontainers import SortedDict

from graphs import connection


class chestManager:
    def __init__(self):
        self.chests = []
        self.waypoints = []

    def addChest(self, x, y):
        if (chestFound := self.chestExists(x, y)) is None:
            self.chests.append(chest(x, y))
        else:
            if type(chestFound) is list:
                for i in range(1, len(chestFound)):
                    chestFound[0].addChests(chestFound[1])
                    self.chests.remove(chestFound[1])
            else:
                chestFound.addBlock(x, y)

    '''
        This function loads the waypoints from file into chests
    '''
    def loadWaypoints(self, dimensions: dict, scaledValues: dict):
        # Start normalizing values for after
        scaledValues["endX"] -= scaledValues["startX"]
        scaledValues["endY"] -= scaledValues["startY"]
        with open("waypoints.txt", 'r') as file:
            # The first 3 lines are useless
            for i in range(3):
                file.readline()
            # Read every waypoint
            while line := file.readline():
                array = line.rstrip().split(":")
                # Get x-y-z
                x, y, z = int(array[3]), int(array[4]), int(array[5])
                ## Normalizing the values as coordinates
                x = (x - scaledValues["startX"]) / scaledValues["endX"]
                x = 1 if x > 1 else 0 if x < 0 else x
                z = (z - scaledValues["startY"]) / scaledValues["endY"]
                z = 1 if z > 1 else 0 if z < 0 else z
                x = int(dimensions["start"][0] + dimensions["width"] * x)
                z = int(dimensions["start"][1] + dimensions["height"] * z)

                # If the waypoint we found is in an area we discovered before, remove that area
                if (chestFound := self.chestExists(x, z)) is not None:
                    self.chests.remove(chestFound)
                # Add it
                self.waypoints.append((x, y, z))
        # Normalize it again as a waypoint
        for wayp in self.waypoints:
            self.chests.append(chest(wayp[0], wayp[1], wayp[2]))
        # Add mistport as a node, this is our starting point
        x, y, z = -760, 85, 1346
        x = (x - scaledValues["startX"]) / scaledValues["endX"]
        x = 1 if x > 1 else 0 if x < 0 else x
        z = (z - scaledValues["startY"]) / scaledValues["endY"]
        z = 1 if z > 1 else 0 if z < 0 else z
        x = int(dimensions["start"][0] + dimensions["width"] * x)
        z = int(dimensions["start"][1] + dimensions["height"] * z)
        self.chests.insert(0, chest(x, y, z))

    def calculateAverageChests(self):
        for chest in self.chests:
            chest.calculateAverage()

    def chestExists(self, x, y):
        found = []
        for chest in self.chests:
            if chest == (x, y):
                found.append(chest)
        if len(found) == 0:
            return None
        elif len(found) == 1:
            return found[0]
        return found

    def generateGraph(self):
        N_DEEP = 2
        for wayp in self.chests:
            tempCosts = {}
            for toCheck in self.chests:
                if wayp is toCheck:
                    continue
                cost = abs(wayp.avgX - toCheck.avgX) + abs(wayp.avgY - toCheck.avgY)
                tempCosts[cost] = toCheck
            s = SortedDict(tempCosts)
            wayp.graphs.addEveryConnections(N_DEEP, s)

    def addBlackList(self, notes):
        blackList = [
            ((610, 278), (477, 311)),
            ((623, 283), (477, 311)),
            ((651, 310), (477, 311)),
            ((649, 325), (477, 311)),
            ((625, 355), (477, 311)),
            ((379, 206), (610, 187))
        ]
        result = [

        ]
        for bl in blackList:
            toAdd = []
            for element in notes:
                if element == bl[0]:
                    toAdd.append(element)
                elif element == bl[1]:
                    toAdd.append(element)
            result.append(toAdd)
        for bl in result:
            bl[0].graphs.blackList.append(bl[1].graphs.id)
            bl[1].graphs.blackList.append(bl[0].graphs.id)

    def calculatePath(self, toDisplay):
        minCost = sys.maxsize
        minPath = []
        # 327, 278 | 610, 311
        nonVisitedNode = [x for x in self.chests]
        visitedNode = []
        currentNode = connection(0, nonVisitedNode.pop(0))
        currentCosts = 0
        # Needed for the first extension
        comingBack = False
        self.addBlackList(nonVisitedNode)

        while True:
            goBack = False
            if nonVisitedNode.__len__() != 0:
                # We must first get the next point
                toVisit = None
                for conn in currentNode.reference.graphs.preferedConnections:
                    if not conn.reference.graphs.visited and not currentNode.reference.graphs.containsIgnore(
                            conn.reference.graphs.id) and not currentNode.reference.graphs.blackList.__contains__(conn.reference.graphs.id):
                        toVisit = conn
                        break
                if toVisit is None:
                    if comingBack:
                        goBack = True
                    else:
                        for conn in currentNode.reference.graphs.everyConnections:
                            if not conn.reference.graphs.visited and not currentNode.reference.graphs.containsIgnore(
                                    conn.reference.graphs.id) and not currentNode.reference.graphs.blackList.__contains__(conn.reference.graphs.id):
                                toVisit = conn
                                break
                if toVisit is None:
                    goBack = True
                if not goBack:
                    comingBack = False
                    currentCosts += toVisit.costs
                    currentNode.reference.graphs.visited = True
                    visitedNode.append(currentNode)
                    currentNode = toVisit
                    if (idx := self.findSamePosition(nonVisitedNode, currentNode)) != -1:
                        nonVisitedNode.pop(idx)
                    else:
                        raise Exception("Node is fun")
            else:
                goBack = True
                if currentCosts < minCost:
                    minCost = currentCosts
                    minPath = visitedNode.copy()
                self.updateMap(minPath, toDisplay.copy(), minCost, visitedNode, currentCosts)

            if goBack:
                comingBack = True
                currentCosts -= currentNode.costs
                befNode = currentNode
                nonVisitedNode.append(currentNode)
                currentNode.reference.graphs.visited = False
                currentNode = visitedNode.pop(visitedNode.__len__() - 1)
                currentNode.reference.graphs.toIgnore.append(befNode)
                befNode.reference.graphs.toIgnore.clear()

    def findSamePosition(self, nonVisited, currentNode):
        for idx, value in enumerate(nonVisited):
            if type(value) is connection:
                if value.reference.graphs.id == currentNode.reference.graphs.id:
                    return idx
                continue
            if value.graphs.id == currentNode.reference.graphs.id:
                return idx
        return -1

    def updateMap(self, nodes, display, costs, unoptimized, curCosts):
        for i in range(len(nodes) - 1):
            display = cv2.line(display, (nodes[i].reference.avgX, nodes[i].reference.avgY),
                               (nodes[i + 1].reference.avgX, nodes[i + 1].reference.avgY), (255, 255, 0), 2)
        for i in range(len(unoptimized) - 1):
            display = cv2.line(display, (unoptimized[i].reference.avgX, unoptimized[i].reference.avgY),
                               (unoptimized[i + 1].reference.avgX, unoptimized[i + 1].reference.avgY), (0, 255, 255), 1)

        display = cv2.putText(display, "Best costs: " + str(costs), (120, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
        display = cv2.putText(display, "Current costs: " + str(curCosts), (460, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow("Lootrunning", display)
        cv2.waitKey(1)
