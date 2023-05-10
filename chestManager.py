import sys

import cv2

from chestClass import chest
from sortedcontainers import SortedDict

from graphs import connection


class chestManager:
    def __init__(self):
        self.chests = []
        self.waypoints = []

    '''
        Given x, y, it add the pixel coordinates as a chest
        Also this makes the merge about multiple chests
    '''
    def addChest(self, x, y):
        # If this pixel is alone
        if (chestFound := self.chestExists(x, y)) is None:
            self.chests.append(chest(x, y))
        else:
            # If there are multiple pixels near
            if type(chestFound) is list:
                for i in range(1, len(chestFound)):
                    chestFound[0].addChests(chestFound[1])
                    self.chests.remove(chestFound[1])
            # If it's just 1 section of them
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

    '''
        # This just call "calculateAverage" of every chest
    '''
    def calculateAverageChests(self):
        for chest in self.chests:
            chest.calculateAverage()

    '''
        It checks if, given x, y, there is alr a chest there
    '''
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

    '''
        This generate the connections of every node
        N_DEEP is used for the prefered connections
    '''
    def generateGraph(self, N_DEEP=2):
        # For every chest
        for wayp in self.chests:
            # Temp variable for after
            tempCosts = {}
            # For every chest calculate the costs
            for toCheck in self.chests:
                if wayp is toCheck:
                    continue
                cost = abs(wayp.avgX - toCheck.avgX) + abs(wayp.avgY - toCheck.avgY)
                # Lazy fix, but it works
                while tempCosts.__contains__(cost):
                    cost+=1
                tempCosts[cost] = toCheck
            # Sort it by key and after add every connection
            s = SortedDict(tempCosts)
            wayp.graphs.addEveryConnections(N_DEEP, s)

    '''
        Add blacklist connections, aka connections we dont want to happen
    '''
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
        # Get every node
        for bl in blackList:
            toAdd = []
            for element in notes:
                if element == bl[0]:
                    toAdd.append(element)
                elif element == bl[1]:
                    toAdd.append(element)
            result.append(toAdd)
        # Then add the blacklist
        for bl in result:
            bl[0].graphs.blackList.append(bl[1].graphs.id)
            bl[1].graphs.blackList.append(bl[0].graphs.id)

    '''
        Same as the function above, but for connections we want to force
    '''
    def forceConnection(self, notes):
        toForce = [
            ((369, 250), (380, 205)),
            ((380, 205), (408, 250)),
            ((293, 89), (340, 76))
        ]
        result = [

        ]
        for bl in toForce:
            toAdd = []
            for element in notes:
                if element == bl[0]:
                    toAdd.append(element)
                elif element == bl[1]:
                    toAdd.append(element)
            result.append(toAdd)
        for bl in result:
            bl[0].graphs.forceConnection = bl[1].graphs.id

    '''
        Here we have to check for every point if they are inside a polygon
        https://stackoverflow.com/questions/217578/how-can-i-determine-whether-a-2d-point-is-within-a-polygon
    '''
    def addNewSubgroup(self, subgroup):
        pass

    def finishSubGroup(self):
        pass

    '''
        This function calculate tha shortest path
        The algo is still work in progress.
        This algo is a modified version of the greedy algo with a bruteforce part into
        @:param todDisplay the csv starting display
        @:return end path
    '''
    def calculateGreedyBruteforce(self, toDisplay):
        # Setup every variables
        minCost = sys.maxsize
        minPath = []
        nonVisitedNode = [x for x in self.chests]
        visitedNode = []
        # Create the first useless connection, why? So that the algo is easier to read
        currentNode = connection(0, nonVisitedNode.pop(0))
        currentCosts = 0
        comingBack = False
        # Setup blacklist/forceConnection
        self.addBlackList(nonVisitedNode)
        self.forceConnection(nonVisitedNode)

        '''
            Temporary algo:
            So, the idea of this algo is to bruteforce every connection, bruteforce while removing some possibilities
            Since the complexity is n!, and yeha we have 180 nodes, 180! is never gonna finish.
            Every node has 2 types of connections:
                - Prefered connections
                - Every connections
            Prefered connections contains the fastest connections of every connections.
            Every connection has a value, that is called "costs", that is how much does it take to reach that node.
            Now that the structure is explained, lets explain how in practice the algo works:
            From node X, we go the the nearest node.
            We continue going to the nearest node by using the field "every connections"
            Then, once we dont have any more free connections left, we save the costs and the path.
            After this, we do step back and step forwards.
            Everytime we do step backs, we only check for prefered connections for the next nearest node
            When before we did a step forward, we check for the nearest node not caring if it's prefered.
        '''
        while True:
            # Everytime reset goBack
            goBack = False
            # If we have anything to visit (So we are not at the end)
            if nonVisitedNode.__len__() != 0:

                # The next node we are gonna visit
                toVisit = None

                # First we have to check if there is any forceConnection
                if currentNode.reference.graphs.forceConnection is not None:
                    toVisit = self.getGraphById(currentNode.reference.graphs.forceConnection, nonVisitedNode)
                    if toVisit is not None:
                        for conn in currentNode.reference.graphs.everyConnections:
                            if conn.reference.graphs.id == currentNode.reference.graphs.forceConnection:
                                toVisit = conn
                                break

                # After prefered connections
                if toVisit is None:
                    for conn in currentNode.reference.graphs.preferedConnections:
                        if not conn.reference.graphs.visited and not currentNode.reference.graphs.containsIgnore(
                                conn.reference.graphs.id) and not currentNode.reference.graphs.blackList.__contains__(conn.reference.graphs.id):
                            toVisit = conn
                            break

                # After everything else
                if toVisit is None:
                    # If we are going backwards, then we go back again. When we go back we just want preferedConnections
                    if comingBack:
                        goBack = True
                    else:
                        for conn in currentNode.reference.graphs.everyConnections:
                            if not conn.reference.graphs.visited and not currentNode.reference.graphs.containsIgnore(
                                    conn.reference.graphs.id) and not currentNode.reference.graphs.blackList.__contains__(conn.reference.graphs.id):
                                toVisit = conn
                                break
                # If we found nothing, goBack
                if toVisit is None:
                    goBack = True
                # If we found anything
                if not goBack:
                    # We can now go forward
                    comingBack = False
                    # Add the new costs
                    currentCosts += toVisit.costs
                    # For not going in a loop
                    currentNode.reference.graphs.visited = True
                    # Now say that we have visited the current node, and change the currentNode with what we are going
                    visitedNode.append(currentNode)
                    currentNode = toVisit
                    # Remove it from nonVisited
                    if (idx := self.findSamePosition(nonVisitedNode, currentNode)) != -1:
                        nonVisitedNode.pop(idx)
                    else:
                        # Kill me.
                        raise Exception("Node is fun")
            # If we are at the end
            else:
                # Go backwards and check if it's highest
                goBack = True
                if currentCosts < minCost:
                    minCost = currentCosts
                    minPath = visitedNode.copy()
                # Update the map
                self.updateMap(minPath, toDisplay.copy(), minCost, visitedNode, currentCosts)

            # If we are going back
            if goBack:
                # Say we are going back, decrease costs
                comingBack = True
                currentCosts -= currentNode.costs
                # Put currentNode in nonVisited, and the last node in visited in currentNode
                befNode = currentNode
                nonVisitedNode.append(currentNode)
                currentNode.reference.graphs.visited = False
                currentNode = visitedNode.pop(visitedNode.__len__() - 1)
                # No loops
                currentNode.reference.graphs.toIgnore.append(befNode)
                befNode.reference.graphs.toIgnore.clear()

    '''
        @:param id the id of the node we want
        @:param nonVisited the graph 
    '''
    def getGraphById(self, id, nonVisited):
        for value in nonVisited:
            # We get either a connection type or a reference type
            if type(value) is connection:
                # Make it a reference
                value = value.reference
            if value.graphs.id == id and not value.graphs.visited:
                return value
        return None

    '''
        @:param nonVisited the graph where we have to search
        @:param currentNode what we wanna find the index
    '''
    def findSamePosition(self, nonVisited, currentNode):
        for idx, value in enumerate(nonVisited):
            # We get either a connection type or a reference type
            if type(value) is connection:
                # Make it a reference
                value = value.reference
            if value.graphs.id == currentNode.reference.graphs.id:
                return idx
        return -1

    '''
        Update the map with the new paths
    '''
    def updateMap(self, nodes, display, costs, unoptimized, curCosts):
        # Display best path
        for i in range(len(nodes) - 1):
            display = cv2.line(display, (nodes[i].reference.avgX, nodes[i].reference.avgY),
                               (nodes[i + 1].reference.avgX, nodes[i + 1].reference.avgY), (255, 255, 0), 2)
        # Display current test
        for i in range(len(unoptimized) - 1):
            display = cv2.line(display, (unoptimized[i].reference.avgX, unoptimized[i].reference.avgY),
                               (unoptimized[i + 1].reference.avgX, unoptimized[i + 1].reference.avgY), (0, 255, 255), 1)
        # Display text
        display = cv2.putText(display, "Best costs: " + str(costs), (120, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
        display = cv2.putText(display, "Current costs: " + str(curCosts), (460, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow("Lootrunning", display)
        cv2.waitKey(1)

    '''
        Given x, y, it returns the chest that is near that coordinate
        @:return None/chest
    '''
    def hasSameLocation(self, x, y):
        for ches in self.chests:
            if ches.avgX - 8 < x < ches.avgX + 8 and ches.avgY - 8 < y < ches.avgY + 8:
                return ches
        return None
