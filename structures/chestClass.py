import sys

from structures.graphs import graphs

class chest:
    def __init__(self, x, y, z=None, warning=False, realX=None, realZ=None):
        # For image detected
        if z is None:
            self.blocks = []
            self.addBlock(x, y)
            self.avgX = -12345
            self.avgY = -12345
            self.realY = None
        # For waypoints
        else:
            self.avgX = x
            self.avgY = z
            self.realX = realX
            self.realY = y
            self.realZ = realZ
        self.warning = warning
        self.graphs = graphs()

    def addBlock(self, x, y):
        self.blocks.append((x, y))

    def addChests(self, chest):
        for block in chest.blocks:
            self.addBlock(block[0], block[1])

    '''
        Calculate the average position of every part
    '''
    def calculateAverage(self):
        # The algo create a rectangle with min/maxX/Y
        minX = sys.maxsize
        maxX = -sys.maxsize
        minY = sys.maxsize
        maxY = -sys.maxsize
        for block in self.blocks:
            if minX > block[0]:
                minX = block[0]
            if maxX < block[0]:
                maxX = block[0]
            if minY > block[1]:
                minY = block[1]
            if maxY < block[1]:
                maxY = block[1]
        # After we get the middle point
        self.avgX = minX + (maxX - minX) // 2
        self.avgY = minY + (maxY - minY) // 2

    '''
        Fast equality
        We check if either we get:
        :param tuple (x, y)
        :param chest, where we check if our adress is the same
    '''
    def __eq__(self, toCheck):
        if type(toCheck) is tuple:
            if self.realY is None:
                for block in self.blocks:
                    # To see if it's the same, then we need 1 axis that is the same, and on the other axis 1 pixel of distance
                    if (toCheck[0] == block[0] and abs(toCheck[1] - block[1]) == 1) or \
                            (toCheck[1] == block[1] and abs(toCheck[0] - block[0]) == 1):
                        return True
            else:
                if abs(self.avgX - toCheck[0]) + abs(self.avgY - toCheck[1]) <= 40:
                    return True
            return False
        elif type(toCheck) is chest:
            for firstBlock in toCheck.blocks:
                if self == firstBlock:
                    return True
            return False
        return False
