import cv2
from visionClass import Vision

if __name__ == "__main__":
    redTemplate = '/home/pi/images_rover/testred.jpg'
    yellowTemplate = '/home/pi/images_rover/testyellow.jpg'
    vision = Vision(0,redTemplate,yellowTemplate)

    vision.getCalibrationPar('calibration/Distortion.npz','calibration/Intrinsics.npz','calibration/Rotation.npz','calibration/Translation.npz')

    if vision.captureFrame() == True :
        print "here"
        cubes = vision.detectCubes("RED")
        
        idx = 0
        for pts in cubes[0]: 
            print cubes[0][idx]
            vision.imgtoWorld(cubes[0][idx])
            idx += 1

       
     
        
