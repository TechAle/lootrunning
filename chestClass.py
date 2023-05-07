from graphs import graphs

class chest:
    def __init__(self, x, y, z=None):
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
            self.realY = y

        self.graphs = graphs()

    def addBlock(self, x, y):
        self.blocks.append((x, y))

    def addChests(self, chest):
        for block in chest.blocks:
            self.addBlock(block[0], block[1])

    def calculateAverage(self):
        minX = 9999
        maxX = -9999
        minY = 9999
        maxY = -9999
        for block in self.blocks:
            if minX > block[0]:
                minX = block[0]
            if maxX < block[0]:
                maxX = block[0]
            if minY > block[1]:
                minY = block[1]
            if maxY < block[1]:
                maxY = block[1]
        self.avgX = minX + (maxX - minX) // 2
        self.avgY = minY + (maxY - minY) // 2

    def __eq__(self, toCheck):
        if type(toCheck) is tuple:
            if self.realY is None:
                for block in self.blocks:
                    if (toCheck[0] == block[0] and abs(toCheck[1] - block[1]) == 1) or \
                            (toCheck[1] == block[1] and abs(toCheck[0] - block[0]) == 1):
                        return True
            else:
                if (self.avgX - toCheck[0])**2 + (self.avgY - toCheck[1])**2 <= 36:
                    return True
            return False
        elif type(toCheck) is chest:
            for firstBlock in toCheck.blocks:
                if self == firstBlock:
                    return True
            return False
        return False
