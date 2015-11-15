# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import picamera
import io
from numpy import *
from operator import itemgetter

max_area = 200

class Vision:
    """Abstraccion del Sistema de Vision de ROVER chico"""
    def __init__(self,cam, redTemplate, yellowTemplate):
        self.cam = cam
        #self.frame = frame
        self.redTemplate = redTemplate
        self.yellowTemplate = yellowTemplate

        self.width  = 640
        self.height = 480
        
    def captureFrame(self):
        #Metodo para capturar self.frame
        
        with picamera.PiCamera() as camera:
            #camera.start_preview()
            stream = io.BytesIO()
            time.sleep(1)
            camera.capture(stream, format='jpeg')
            #camera.stop_preview()
        #Construct a numpy array from the stream
        data = np.fromstring(stream.getvalue(),dtype=np.uint8)    
        #"Decode" the image from the array, preserving colour
        self.frame = cv2.imdecode(data,1)
        self.height, self.width, self.depth = self.frame.shape
        
        print self.frame.shape
        
        return True

    def getFrame(self):
        #Metodo que retorna el frame actual
        return self.frame

    def getCalibrationPar(self, distortionFileName,intrFileName, rotMatFileName, transFileName):

        rt = np.load(rotMatFileName)
        it = np.load(intrFileName)
        trans = np.load(transFileName)
        dist = np.load(distortionFileName)
        
        rt_loaded = rt['rot']
        it_loaded = it['intrinsic_matrix']
        trans_loaded = trans['tcv']
        dist_loaded = dist['distortion_coefficient']

        self.intrinsic = it_loaded
        self.distortion = dist_loaded
        self.RotTrasMatrix = cv2.hconcat([rt_loaded, trans_loaded[0]])

    def imgtoWorld(self, imgPoint):

        imgHomPoint = [imgPoint[0], imgPoint[1], 1] #Homogenous Point
        imgWorldPoint = np.dot(linalg.inv(self.intrinsic),imgHomPoint)

        worldPoint = np.dot(linalg.inv(np.delete(self.RotTrasMatrix,2,1)),imgWorldPoint) 
        
        worldPoint = (np.delete(worldPoint,2,0)/worldPoint[2])*0.16

        print "worldPoint "
        print worldPoint

        
    def detectCubes(self, cube):
        #roi is the object or region of object we need to find
        # '/home/cristobal/Escritorio/ROVER/images_rover/testred.jpg'
        if cube == "YELLOW" : template = self.yellowTemplate
        elif cube == "RED"  : template = self.redTemplate
        else: return -1

        roi = cv2.imread(template,1)
        roi = cv2.GaussianBlur(roi,(3,3),0) #Filtro
        hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)

        target = self.frame
        target = cv2.GaussianBlur(target,(5,5),0) #Filtro
        hsvt   = cv2.cvtColor(target,cv2.COLOR_BGR2HSV)

        # calculating object histogram
        roihist = cv2.calcHist([hsv],[0, 1], None, [180, 256], [0, 180, 0, 256] )

        # normalize histogram and apply backprojection
        cv2.normalize(roihist,roihist,0,255,cv2.NORM_MINMAX)
        dst  = cv2.calcBackProject([hsvt],[0,1],roihist,[0,180,0,256],1)

        # Now convolute with circular disc
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        cv2.filter2D(dst,-1,disc,dst)

        # threshold and binary AND
        ret,thresh = cv2.threshold(dst,50,255,0)
                
        bottoms, area , centroids , threshRGB = self.countours(thresh)

        return (bottoms, area , centroids , threshRGB, thresh)

    def detectCubesV3(self, cube):

        #roi is the object or region of object we need to find
        # '/home/cristobal/Escritorio/ROVER/images_rover/testred.jpg'
        if cube == "YELLOW" : template = self.yellowTemplate
        elif cube == "RED"  : template = self.redTemplate
        else: return -1
        
        idx = 0;

        seg_res = np.zeros((self.height, self.width, 1), dtype=np.uint8)
        
        for fnameTmp in template :

            roi = cv2.imread(fnameTmp,1)
            roi = cv2.bilateralFilter(roi,9,75,75)
            hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)

            #target is the image we search in
            #'/home/cristobal/Escritorio/ROVER/images_rover/cubered0.jpg'
            target = self.frame.copy()
            target = cv2.bilateralFilter(target,9,75,75)
            hsvt= cv2.cvtColor(target,cv2.COLOR_BGR2HSV)

            # calculating object histogram
            roihist = cv2.calcHist([hsv],[0, 1], None, [180, 256], [0, 180, 0, 256] )

            # normalize histogram and apply backprojection
            cv2.normalize(roihist,roihist,0,255,cv2.NORM_MINMAX)
            dst = cv2.calcBackProject([hsvt],[0,1],roihist,[0,180,0,256],1)

            # Now convolute with circular disc
            disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
            cv2.filter2D(dst,-1,disc,dst)

            # threshold and binary OR
            ret,thresh = cv2.threshold(dst,50,255,0)
            #thresh = cv2.merge((thresh,thresh,thresh))
            #res = cv2.bitwise_and(target,thresh)
            #res = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)

            seg_res = cv2.bitwise_or(seg_res,thresh)
            
            idx += 1
        
        bottoms, area , centroids , threshRGB = self.countours(seg_res)

        return (bottoms, area , centroids , threshRGB, seg_res)

    def detectCubesV2(self, cube):
     
        target = self.frame
        #blur = cv2.blur(target,(10,10))
        #gray= cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)
        b,g,r = cv2.split(target)
        
        ret,thresh_red = cv2.threshold(r,127,255,cv2.THRESH_BINARY) 

        height, width, depth = target.shape

        res = target[:,:,0]

        for i in range( 0, height ):
            for j in range( 0, width ):
                
                r = target.item(i,j,2)
                g = target.item(i,j,1)
                b = target.item(i,j,0)

                if cube == "RED" :
                    first_th = r >= 50 and g <= 30 and b <= 30 and abs(b-g) < 20
                    second_th = r >= 100 and g <= 80 and b <= 80 and abs(b-g) < 30
                    third_th = r  >= 200 and g <= 150 and b <= 150 and  abs(b-g) < 40
                else :
                    first_th = r >= 50 and g >= 50 and b <= 30 and abs(r-g) < 20
                    second_th = r >= 100 and g >= 100 and b <= 80 and abs(r-g) < 30
                    third_th = r  >= 200 and g >= 200 and b <= 150 and abs(r-g) < 40
                    
                if  first_th or second_th or third_th :           
                    res.itemset((i,j),255)
                else :
                    res.itemset((i,j),0)
  
        bottoms, area , centroids , threshRGB = self.countours(res)

        return (bottoms, area , centroids , threshRGB, res)

    def countours(self, res) :

        #Morphological Operations
        kernel = np.ones((3,3),np.uint8)
        thresh = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel)
        kernel = np.ones((6,6),np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        #Find Contours
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        threshRGB = cv2.cvtColor(thresh,cv2.COLOR_GRAY2RGB)

        #Contours Filter 
        idx = 0
        real_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            print area
            if area > max_area :
                real_contours.append(contours[idx])
            idx += 1     

        #Draw Bounding Boxe
        idx =0 #index initialization
        centroids = []
        bottoms = []
        area = []
        
        for cnt in real_contours:

            rect = cv2.minAreaRect(cnt)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(threshRGB,[box],0,(0,0,255),2)
            M = cv2.moments(cnt)
            centroids.append((int(M['m10']/M['m00']),int(M['m01']/M['m00'])))

            area.append(cv2.contourArea(cnt))

            #GROUND CENTER POINT TEST
            p_y_test = array([box[0][1],box[1][1],box[2][1],box[3][1]])
            bottommost0_idx = p_y_test.argmax()
            p_y_temp = p_y_test
            p_y_temp[bottommost0_idx] = 0
            bottommost1_idx = p_y_temp.argmax()
            bottommost0 = box[bottommost0_idx]
            bottommost1 = box[bottommost1_idx]

            if bottommost0[0] > bottommost1[0] : 
                x_center = bottommost1[0]+(abs(bottommost0[0]-bottommost1[0])/2)
            else : x_center = bottommost0[0]+(abs(bottommost0[0]-bottommost1[0]))/2

            if bottommost0[1] > bottommost1[1] : 
                y_center = bottommost1[1]+(abs(bottommost0[1]-bottommost1[1])/2)
            else : y_center = bottommost0[1]+(abs(bottommost0[1]-bottommost1[1])/2)
            
            #GROUND CENTER POINT TEST

            bottoms.append((x_center,y_center))           
            p1 = (box[0][0],box[0][1])
            p2 = (box[1][0],box[1][1])
            p3 = (box[2][0],box[2][1])
            p4 = (box[3][0],box[3][1])
            
            cv2.circle(threshRGB,p1,10,(0,255,255))
            cv2.circle(threshRGB,p2,10,(0,255,255))
            cv2.circle(threshRGB,p3,10,(0,255,255))
            cv2.circle(threshRGB,p4,10,(0,255,255))
            
            cv2.circle(threshRGB,centroids[idx],10,(0,255,0))
            cv2.circle(threshRGB,bottoms[idx],10,(0,255,0))
            cv2.line(threshRGB,centroids[idx],bottoms[idx],(255,0,0),5)

            idx += 1
  
        return (bottoms, area , centroids , threshRGB)



    '''ROVER Cargador: Metodo para seguir Linea Negra
    Return : Punto que debe seguir el Robot
    Parametros ::: 
    kernel: tamaño del area blanca y negra a analizar luego de detectar las lineas en la imagen-> formato: tupla
    limites: Limites de la region de interes a usar para detectar linea
    vertical_limits   = (top_limit, bottom_limit)
    horizontal_limits = (left_limit, rigth_limit)
    maxDistBlack: Maxima distancia en pixeles de la franja negra a seguir
    diffBlackWhiteThreshold: Umbral de diferencias de intensidad blanco y negro
    '''

    def followLine(self, kernel = (100,50), vertical_limits = (None,None), horizontal_limits = (None,None), maxDistBlack = 300, diffBlackWhiteThreshold = 10):

        frame = self.frame.copy()
        height, width, depth = frame.shape
        roi = frame[vertical_limits[0]:horizontal_limits[1],horizontal_limits[0]:horizontal_limits[1]].copy()
        roi_filter = cv2.bilateralFilter(roi,9,75,75)
        temp = roi_filter.copy()
        center = (-1,-1)
        #temp = cv2.GaussianBlur(temp,(5,5),0) #Filtro a imagen temporal
        
        new_height, new_width, new_depth = roi.shape

        # Otsu's thresholding after Gaussian filtering
        blur = cv2.GaussianBlur(roi_filter,(5,5),0) #Filtro a Region de interes
        roi_gray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY) #BGR to Gray
        ret,thresh = cv2.threshold(roi_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Threshold
        edges = cv2.Canny(thresh,50,150,apertureSize = 3) #Detector de Bordes
        lines = cv2.HoughLines(edges,1,np.pi/180,100) #Detector de Lineas

        detectedLines = []
        centersLines = []

        if lines != None :
            for rho,theta in lines[0]:
                    
                if theta > (np.pi/180)*170 or theta < (np.pi/180)*10 :
                        
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))

                    if a != 0.0 and b != 0.0 :
                        
                        aux = rho/b
                        line =  [(x1,y1),(x2,y2)]
                        inter = (int)(-((new_height/2)-aux)*(b/a))
                        cnt = (inter,new_height/2)
                        print "Lineas : "
                        print line
                        
                        detectedLines.append(line)
                        centersLines.append(cnt)

                        cv2.line(roi,line[0],line[1],(0,0,255),1)
                        #cv2.circle(roi,(center[0],center[1]),5,(255,0,0),4)

            #Filtrado de Lineas
            idx = 0
            centersLines = sorted(centersLines, key = itemgetter(0))

            for cnt in centersLines :
                if idx != 0:
                    if cnt[0] < prevCenter[0]+20:
                        centersLines.pop(idx)
                prevCenter = cnt                
                idx += 1

            imgs = []
            
            if len(centersLines) != 0 :
                for cnt in centersLines :
                    cv2.circle(roi,(cnt[0],cnt[1]),5,(255,0,0),2)
                    roi_izq = temp[cnt[1]-kernel[0]:cnt[1]+kernel[0],cnt[0]-kernel[1]:cnt[0]]
                    roi_der = temp[cnt[1]-kernel[0]:cnt[1]+kernel[0],cnt[0]:cnt[0]+kernel[1]]
                    imgs.append((roi_izq, roi_der))
                    print "centers"
                    print cnt
                    
            idx = 0
            grayLevelCenters = []
            for data in imgs :

                idx_lado = 0
                grayLevels =[]
                
                for im in data :

                    #name = "roi_"
                    #name += str(idx)+str(idx_lado)
                    
                    #cv2.imshow(name,im)
                    #cv2.waitKey(33)
                    
                    height, width, depth = im.shape
                    res = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
                    acum = 0
                    samples = 0

                    for i in range( 0, height ):
                        for j in range( 0, width ):

                            val = res.item(i,j)
                            acum += val
                            samples += 1

                    if samples != 0 :
                        indiceNivelGris = acum/samples
                    else :
                        indiceNivelGris = 0

                    grayLevels.append(indiceNivelGris)
                    
                    idx_lado += 1

                val = (grayLevels[0], grayLevels[1])
                grayLevelCenters.append(val)
                idx += 1

            centerType = []
            idx = 0
            for levels in grayLevelCenters :

                if levels[0] > levels[1] :
                    
                    centerType.append(("IZQ", levels))
                else :
                    centerType.append(("DER", levels))

                idx += 1

            idx = 0
            for dataCenter in centerType :
                if idx > 0 :
                    if dataCenter[0] == "DER" and prev[0] == "IZQ" and abs(centersLines[idx][0]-centersLines[idx-1][0]) < maxDistBlack :
                        center = (abs(centersLines[idx][0]-centersLines[idx-1][0])/2 + centersLines[idx-1][0],centersLines[idx-1][1])
                        cv2.circle(roi,(center[0],center[1]),10,(255,255,0),2)
                    '''
                    elif dataCenter[0] == "IZQ" and prev[0] == "DER" :
                        if idx+1 < len(centerType): 
                            if dataCenter[2] > prev[1] and centerType[idx+1][0] != "DER":
                                center = (centersLines[idx][0],centersLines[idx][1])
                                cv2.circle(roi,(center[0],center[1]),10,(255,255,0),2)
                            

                    elif dataCenter[0] == "DER" and prev[0] == "DER" :
                        if dataCenter[1] < prev[1] :
                            center = (centersLines[idx][0],centersLines[idx][1])
                            cv2.circle(roi,(center[0],center[1]),10,(255,255,0),2)
                            
                    elif dataCenter[0] == "IZQ" and prev[0] == "IZQ" :
                        if dataCenter[2] > prev[2] :
                            center = (centersLines[idx-1][0],centersLines[idx-1][1])
                            cv2.circle(roi,(center[0],center[1]),10,(255,255,0),2)
                    '''    
                if len(centerType) == 1 and abs(dataCenter[1][0]-dataCenter[1][1]) > diffBlackWhiteThreshold :
                    print "Una linea detectada : "
                    print abs(dataCenter[1][0]-dataCenter[1][1])
                    center = (centersLines[idx][0],centersLines[idx][1])
                    cv2.circle(roi,(center[0],center[1]),10,(255,255,0),2)
                            
                idx += 1
                prev = dataCenter
            
            print centerType
        else :
            print "no hay lineas detectadas"
    
        return center
