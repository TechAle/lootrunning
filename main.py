# Python program to explain cv2.line() method

# importing cv2
import cv2
import time
from imageManager import imageManager
import numpy

path = 'img.jpg'

def main(pathInput):
    cvManager = imageManager(path=pathInput)
    cvManager.readInputImage()
    cvManager.setupDimensions()
    cvManager.setupSpawn()
    cvManager.createGraph()
    cvManager.calculatePath()

if __name__ == "__main__":
    main(path)
