# Python program to explain cv2.line() method

from managers.imageManager import imageManager

path = 'resources/img.jpg'


def main(pathInput):
    cvManager = imageManager(path=pathInput)
    cvManager.readInputImage()
    cvManager.setupDimensions()
    cvManager.setupSpawn()
    cvManager.createGraph()
    #cvManager.createRestrictions()
    cvManager.calculatePath()


if __name__ == "__main__":
    main(path)
