# Python program to explain cv2.line() method

# importing cv2
from imageManager import imageManager

path = 'img.jpg'


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
