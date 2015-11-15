# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import cv2

import Platform
import Claw
from visionClass import Vision

# --- MAIN CLASS ---

class Loop(object):
        """
        Stores pre-programmed rutines for Rover Loader

        Each method defines a single iteration of it's state
        """

        GPIO.setmode(GPIO.BCM);

        __init  = 0;            # No hay movimiento. Solo inicio y fin de desafio :D
        __bC    = 1;            # Buscar cubo rojo
        __aC    = 2;            # Agarrar Cubo
        __bBr   = 3;            # Buscar Barcaza
        __sABr  = 4;            # Subir a barcaza
        __eEBr  = 5;            # Esperar en barcaza
        __bDBr  = 6;            # Bajar de barcaza
        __dC    = 7;            # Dejar cubo
        __ThisIsTheEnd = 8;     # Se recogieron todos los cubos
        
        
        __redCube    = 100;     # at platform
        __yellowCube = 101;     # at port

        aux = 0 #Cuenta veces que ocurre el Loop

        # Metodos
        def __init__(self, platform, claw, reset):
                self.movement = platform; 
                self.claw     = claw;
                self.resetSwt = reset;
                #self.visual   = False;

                self.coord  = 0;
                # Default initial cubes quantity
                self.yellowCubesLeftCount = 10;
                self.redCubesLeftCount    = 4;
                self.turnsCounter = 0;

                # Lists of movements
                self.vectorMovimiento = [];     # (1, t) -> giratT(1,t)
                                                # (-1, t)-> giratT(-1,t)
                                                # (2,0)  -> avanzarPoco()
                                                # (2,1)  -> avanarHarto()
                
                # state "vector"
                self.__InnerState   = self.__init;
                self.__CurrentCube  = self.__redCube;
                self.isSleeping     = False;
                self.__whereIam     = 1;

                # Desition constans
                self.left_th   = 340;   # 305
                self.right_th  = 400;   # 325
                self.top_th    = 310;   # 305
                self.bottom_th = 400;   # 410

                #redTemplate     = ['/home/pi/images_rover/redTest69.jpg', '/home/pi/images_rover/redTest79.jpg']
                redTemplate    = ['/home/pi/images_rover/redTest7.jpg',
                                  '/home/pi/images_rover/redTest8.jpg']
                yellowTemplate = ['/home/pi/images_rover/yellotest1.jpg',
                                  '/home/pi/images_rover/yellotest3.jpg',]
                self.vision = Vision(0,redTemplate,yellowTemplate)

                self.vision.getCalibrationPar('calibration/Distortion.npz','calibration/Intrinsics.npz','calibration/Rotation.npz','calibration/Translation.npz')
                
        def __del__(self):
                self.movement.__del__();
                self.claw.__del__();
                GPIO.cleanup();

        def reset(self):
                self.__InnerState   = self.__init;
                self.__CurrentCube  = self.__redCube;

                self.init()

                # La cuenta de cubos no debe resetearse

        
        def loop(self):
                """ Main loop, aca pasa de to' """

                while True:
                        # Leer pin de reseteo de estado
                        
                        if(self.resetSwt.isOn() == False):
                                if(self.isSleeping == False):
                                        print ":: RESET ::"
                                        self.isSleeping = True;
                                        self.reset();

                                # suficiente para que el CPU no joda :P
                                time.sleep(1);
                                continue;
                        else:
                                self.isSleeping = False;

                        if(self.verificarEstado() == False):
                                # se podria hacer algo que indique problema de estado (movimiento iterativo)
                                continue;
                        
                        # Ahora una horrible sucesion de ifs (switch)

                        if(self.__InnerState == self.__init):
                                self.__InnerState = self.init();
                                continue;

                        elif(self.__InnerState == self.__bC):
                                self.__InnerState = self.buscarCubo();
                                continue;

                        elif(self.__InnerState == self.__aC):
                                self.__InnerState = self.agarrarCubo();
                                continue;

                        elif(self.__InnerState == self.__bBr):
                                self.__InnerState = self.buscarBarcaza();
                                continue;

                        elif(self.__InnerState == self.__sABr):
                                self.__InnerState = self.subirABarcaza();
                                continue;

                        elif(self.__InnerState == self.__eEBr):
                                self.__InnerState = self.esperarEnBarcaza();
                                continue;

                        elif(self.__InnerState == self.__bDBr):
                                self.__InnerState = self.bajarDeBarcaza();
                                continue;

                        elif(self.__InnerState == self.__dC):
                                self.__InnerState = self.dejarCubo();
                                continue;

                        elif(self.__InnerState == self.__ThisIsTheEnd):
                                self.__InnerState = self.thisIsTheEnd();
                                continue;

                        else:
                                #TODO: indicar error y luego resetear
                                self.reset();


        def init(self):
                print "\tESTADO: INICIO\n";

                self.movement.state(0);
                self.claw.up();
                self.claw.open();
                time.sleep(1);

                return self.__bC;

        def buscarCubo(self):
                """
                Buscar cubo rojo/amarillo y quedar enfrente de el, evadiendo obstaculos :S
                """
                
                if self.__CurrentCube == self.__redCube:
                        print "\tESTADO: BUSCAR CUBO ROJO";

                        if(self.redCubesLeftCount <= 0):
                                return self.__bBr;

                        if self.vision.captureFrame() == True :
                                cubes = self.vision.detectCubesV3("RED")
                                name = "cubesDetection_"
                                new_string = name + str(self.aux)
                                cv2.imwrite(new_string+".jpg",cubes[3])

                                name = "segmentationResult"
                                new_string = name + str(self.aux)
                                cv2.imwrite(new_string+".jpg",cubes[4])
                                
                                name = "frame_"
                                new_string = name + str(self.aux)
                                cv2.imwrite(new_string+".jpg",self.vision.getFrame())
                                self.aux += 1

                        else :
                                return self.__bC;

                elif self.__CurrentCube == self.__yellowCube:
                        print "\tESTADO: BUSCAR CUBO AMARILLO";

                        if(self.yellowCubesLeftCount <= 0):
                                return self.__bBr;

                        if self.vision.captureFrame() == True :
                                cubes = self.vision.detectCubesV3("YELLOW")
                                name = "cubesDetection_"
                                new_string = name + str(self.aux)
                                cv2.imwrite(new_string+".jpg",cubes[3])

                                name = "segmentationResult"
                                new_string = name + str(self.aux)
                                cv2.imwrite(new_string+".jpg",cubes[4])

                                name = "frame_"
                                new_string = name + str(self.aux)
                                cv2.imwrite(new_string+".jpg",self.vision.getFrame())
                        
                                
                                self.aux += 1

                        else :
                                return self.__bC;
                else:
                        # Nunca debe pasar lo siguiente, pero para tener algo
                        print "Que mierda esta pasando en BuscarCubo()"

                        return self.__init;


                if len(cubes[0]) == 0 :
                        print "No encontro Cubo"
                        crit = 0.5
                        self.movement.girarT(1, crit);             #TODO: setear tiempo
                        self.vectorMovimiento.append((1, crit));
                        self.movement.stop()

                else :
                        print "Encontro cubos"
                        cuboAlaVista    = True;
                        coordenadasCubo = cubes[0].pop();
                        centroide       = cubes[2].pop();
                        self.coord      = centroide

                        print "Encontre X:" + str(coordenadasCubo[0])
                        print "Encontre Y:" + str(centroide[1])
                        
                        if (coordenadasCubo[0] <= self.right_th and coordenadasCubo[0] >= self.left_th
                        and centroide[1] >= self.top_th and centroide[1] <=  self.bottom_th):
                                return self.__aC;
                        else:
                                if(coordenadasCubo[0] > self.right_th or coordenadasCubo[0] < self.left_th):
                                        # Movimiento angular, giro no simetrico y converge
                                        if coordenadasCubo[0] > self.right_th:
                                                print "Mas a la izquierda"
                                                crit = 0.1 #0.3 + float((coordenadasCubo[0]-self.right_th)/300.0)
                                                self.movement.girarT(-1, crit);
                                                self.movement.stop()
                                                self.vectorMovimiento.append((-1, crit));
                                        if coordenadasCubo[0] < self.left_th:
                                                print "Mas a la derecha"
                                                crit = 0.18 #0.2 + float((self.left_th-coordenadasCubo[0])/400.0)
                                                self.movement.girarT(1, crit);
                                                self.movement.stop()
                                                self.vectorMovimiento.append((1, crit));

                                # Al mimso timepo que centrado
                                if centroide[1] < self.top_th:  #TODO: setiar valor de cercania
                                        crit = 0.21 #0.3 + (self.top_th - centroide[1])/300.0;
                                        self.movement.mover(2, 45, crit);
                                        self.vectorMovimiento.append((2, 45, crit));
                                elif centroide[1] > self.bottom_th:
                                        crit = 0.12 #0.3 + (centroide[1] - self.bottom_th)/200.0;
                                        self.movement.mover(-2, 45, crit);
                                        self.vectorMovimiento.append((-2, 45, crit));
                                
        
                return self.__bC;
                
        def agarrarCubo(self):
                """ Manejar garra para agarrar cubo """
                print "\tESTADO: AGARRAR CUBO";

                #self.vision.captureFrame();
                #time.sleep(2)
                #cv2.imwrite("foto_previa.jpg", self.vision.getFrame());

                """"
                if self.vision.captureFrame():
                        cubes = self.vision.detectCubesV3("RED")
                        if cubes[0]:
                                coordenadasCubo = cubes[0].pop();
                                centroide       = cubes[2].pop();
                                print "Encontre X:" + str(coordenadasCubo[0])
                                print "Encontre Y:" + str(centroide[1])
                else:
                        print "no photo"
                """

                # take photo
                #self.vision.captureFrame();
                #time.sleep(2)
                #cubes = self.vision.detectCubesV3("RED")
                #print "x: =" + str(cubes[0][0])
                #cv2.imwrite("cubo_agarrado.jpg", self.vision.getFrame());

                self.claw.open()
                time.sleep(0.4)
                self.claw.down()
                time.sleep(0.5)
                
                self.movement.avanzarPoco();
                #vel = self.posToVel()
                #self.movement.setVelocity(vel)
                
                self.claw.open()
                time.sleep(0.5)
                self.claw.close()
                time.sleep(0.5)

                self.claw.up()
                time.sleep(0.5)
                self.movement.retrocederPoco();
                
                return self.__bBr; # Busca barcaza
        
        def buscarBarcaza(self):
                """ Buscar barcaza """
                print "ESTADO: BUSCAR BARCAZA";

                if self.vectorMovimiento == []:
                        return self.__sABr;

                lastStep = self.vectorMovimiento.pop();

                if abs(lastStep[0]) == 1:
                        self.movement.girarT(-lastStep[0], lastStep[1])
                else:
                        self.movement.mover(-lastStep[0], lastStep[1], lastStep[2])

                time.sleep(0.5)

                self.movement.girarT(1, 0.7)

                return self.__bBr;

        def subirABarcaza(self):
                """ Seguir linea y subir a barcaza """
                print "ESTADO: SUBIR A BARCAZA";

                # seguir linea            

                if self.vision.captureFrame():
                        coordenadasLinea = self.vision.followLine();
                else:
                        print "no photo"


                #self.movement.girarT(1,1)

                if coordenadasLinea and coordenadasLinea != (-1,-1):
                        # moverse en funcion de coordenadasLinea
                        if coordenadasLinea[0] < 300:
                                print "linea a la derecha"
                                self.movement.girarT(1, 0.1);
                        elif coordenadasLinea[0] > 325:
                                print "linea a la izquierda"
                                self.movement.girarT(-1, 0.18);
                        else:
                                self.movement.mover(1, 40, 2)   #TODO: revizar si sirve o dejarlo en funcion de que sirva aca
                else:
                        self.movement.girarT(1, 0.1);
                        """
                        self.movement.girarT(1, 0.3);
                        self.movement.mover(1, 40, 0.3)
                        self.movement.girarT(-1, 0.6)
                        self.movement.mover(-1, 40, 0.3)
                        self.movement.girarT(1, 0.3)
                        """
                        return self.__sABr;

                return self.__eEBr;

        def esperarEnBarcaza(self):
                # decide cuando es tiempo de bajar
                print "ESTADO: ESPERAR EN BARCAZA";

                isRampDown = False;     #TODO: PDI

                if isRampDown:
                        return self.__bDBr;

                time.sleep(25);

                return self.__eEBr;

        def bajarDeBarcaza(self):
                # Probablemente igual que subirBarcaza()?
                print "ESTADO: BAJAR DE BARCAZA";

                self.movement.mover(1, 40, 3);

                return self.__dC;

        def dejarCubo(self):
                # Decide donde dejar cubo rojo/amarillo
                print "ESTADO: DEJAR CUBO";

                self.claw.down()
                time.sleep(0.5)
                self.movement.girarT(1, 0.3)
                self.movement.avanzarPoco();
                #vel = self.posToVel()
                #self.movement.setVelocity(vel)
                self.claw.open();
                self.movement.retrocederPoco();

                self.claw.up()
                self.claw.close();
                time.sleep(1)

                if(self.__CurrentCube == self.__redCube):
                        self.redCubesLeftCount -= 1;
                        self.__CurrentCube = self.__yellowCube;
                        
                elif(self.__CurrentCube == self.__yellowCube):
                        self.yellowCubesLeftCount -= 1;
                        self.__CurrentCube = self.__redCube;
                        
                return self.__bC;

        def thisIsTheEnd():
                print "ESTADO: THIS IS THE END";

                self.movement.state(Platform.__LEFT);
                self.claw.open();
                time.sleep(3);
                self.claw.close();
                time.sleep(1);
                self.movement.state(Platform.__RIGHT);
                self.claw.open();
                time.sleep(3);
                self.claw.close();
                time.sleep(1);
                
                sleep(1);
                return __ThisIsTheEnd;

        def verificarEstado(self):

                # No debe pasar nunca, pero igual
                if(self.__CurrentCube != self.__redCube and self.__CurrentCube != self.__yellowCube):
                        assert (self.__CurrentCube != self.__redCube and self.__CurrentCube != self.__yellowCube);
                        return False;

                return True;

        def posToVel(self):

                min_vel = 35
                max_vel = 80

                vel = ((max_vel-min_vel)/(self.top_th-self.bottom_th))(self.coord[1]-self.bottom_th)+min_vel
                
                return int(vel)

# --- END OF MAIN CLASS ---


# --- RESET SWITCH ---

class ResetSwitch(object):

        GPIO.setmode(GPIO.BCM);

        def __init__(self, PIN_RESET = 8):
                self.resetPin = PIN_RESET;

                GPIO.setup(self.resetPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN);

        def __del__(self):
                self.resetPin = 0;

        def isOn(self):
                if(GPIO.input(self.resetPin) == GPIO.HIGH):
                        print "Switch ON"
                        return True;
                else:
                        return False;


# --- END OF RESET SWITCH

if __name__=="__main__":
	GPIO.setwarnings(False);

        movement = Platform.Platform();
        claw     = Claw.Claw();
        reset    = ResetSwitch();
	
	roverLoop = Loop(movement, claw, reset);

        print "ROVER COMIENZA SUS LABORES";

        #roverLoop.agarrarCubo()
        #roverLoop.claw.close();
        #time.sleep(1);
        #roverLoop.bajarDeBarcaza();
        #roverLoop.dejarCubo();
        #roverLoop.subirABarcaza();

        roverLoop.loop();

        print "This is the END";
