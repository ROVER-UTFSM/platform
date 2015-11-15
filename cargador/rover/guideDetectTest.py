import cv2
from visionClass import Vision

if __name__ == "__main__":
    redTemplate = '/home/pi/images_rover/cuboTest.png'
    yellowTemplate = '/home/pi/images_rover/testyellow.jpg'
    vision = Vision(0,redTemplate,yellowTemplate)

    vision.getCalibrationPar('calibration/Distortion.npz','calibration/Intrinsics.npz','calibration/Rotation.npz','calibration/Translation.npz')

    if vision.captureFrame() == True :
        print "here"
        guide, roi = vision.guideLineDetect()

        

