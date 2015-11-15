# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time


class Platform(object):
	"""
	Handles the PWM output for a HBridge and offers movement methods for the platform
	TODO:Implement a model of a 'radial' and angular velocity (super position :P)
	"""

	GPIO.setmode(GPIO.BCM)
	
	# Constants
	__F = 20
	
	__STOP     = 0
	__FORWARD  = 1
	__BACKWARD = 2
	__LEFT     = 3
	__RIGHT    = 4
	
	def __init__(self, PIN_MOTOR1=27, PIN_DIRF1=4, PIN_DIRB1=22, PIN_MOTOR2=24, PIN_DIRF2=23, PIN_DIRB2=25, lowSpeed=0, highSpeed=100):
		"""
		  MOTOR 1 -> LEFT
		  MOTOR 2 -> RIGHT
		"""
		
		# PINs as output for direction handling MOTORL
		self.pin_dir1f = PIN_DIRF1
		self.pin_dir1b = PIN_DIRB1
		GPIO.setup(PIN_DIRF1, GPIO.OUT)
		GPIO.setup(PIN_DIRB1, GPIO.OUT)
		
		self.pin_dir2f = PIN_DIRF2
		self.pin_dir2b = PIN_DIRB2
		GPIO.setup(PIN_DIRF2, GPIO.OUT)
		GPIO.setup(PIN_DIRB2, GPIO.OUT)
		
		# Set PWM
		self.velocity = 0
		GPIO.setup(PIN_MOTOR1, GPIO.OUT)
		self.pwm1 = GPIO.PWM(PIN_MOTOR1, Platform.__F)
		self.pwm1.start(self.velocity)
		
		GPIO.setup(PIN_MOTOR2, GPIO.OUT)
		self.pwm2 = GPIO.PWM(PIN_MOTOR2, Platform.__F)
		self.pwm2.start(self.velocity)

		# State vector {state, time}
		self.stateVector = [{0,0},{0,0},{0,0},{0,0},{0,0}]
		self.lastTime = 0

		# Init state
		self.state(Platform.__STOP)
	
	def __del__(self):
		self.pwm1.stop()
		self.pwm2.stop()

		# Ojo con esto ! Ojo con el scope, no se vaya a destruir el objeto cuando aun vivan otros que usen GPIO !
		GPIO.cleanup()
	
	# --- PARTE ESCENCIAL ---

	def setVelocity(self, vel):
		"""
	  	Change duty cycle an velocity of the Platform
		"""
		self.velocity = vel
		self.pwm1.ChangeDutyCycle(self.velocity)
		self.pwm2.ChangeDutyCycle(self.velocity)
	
	def state(self, newState):
		"""
		  Change the direction pins of the HBridge
	  
		  TODO: relegate this to a HBridge class
		"""
		if(newState == Platform.__STOP):
			self.setVelocity(0)
			#set direction outputs to ((0,0),(0,0))
			GPIO.output(self.pin_dir1f, 0)
			GPIO.output(self.pin_dir1b, 0)
			GPIO.output(self.pin_dir2f, 0)
			GPIO.output(self.pin_dir2b, 0)
		elif(newState == Platform.__FORWARD):
			#set direction outputs to ((1,0),(1,0))
			GPIO.output(self.pin_dir1f, 1)
			GPIO.output(self.pin_dir1b, 0)
			GPIO.output(self.pin_dir2f, 1)
			GPIO.output(self.pin_dir2b, 0)
		elif(newState == Platform.__BACKWARD):
			#set direction outputs to ((0,1),(0,1))
			GPIO.output(self.pin_dir1f, 0)
			GPIO.output(self.pin_dir1b, 1)
			GPIO.output(self.pin_dir2f, 0)
			GPIO.output(self.pin_dir2b, 1)
		elif(newState == Platform.__LEFT):
			#set direction outputs to ((1,0),(0,1))
			GPIO.output(self.pin_dir1f, 0)
			GPIO.output(self.pin_dir1b, 1)
			GPIO.output(self.pin_dir2f, 1)
			GPIO.output(self.pin_dir2b, 0)
		elif(newState == Platform.__RIGHT):
			#set direction outputs to ((0,1),(1,0))
			GPIO.output(self.pin_dir1f, 1)
			GPIO.output(self.pin_dir1b, 0)
			GPIO.output(self.pin_dir2f, 0)
			GPIO.output(self.pin_dir2b, 1)
		else:
			self.state(Platform.__STOP)

	# --- FIN PARTE ESCENCIAL ---

	# FUNCIONES A PARTIR DE LAS DE LAS ESCENCIALES
	# funciones especificas para LARC 2014/2015

	def stop(self):
		self.state(0)
		time.sleep(0.1)

	def girarT(self, sentido, t=0.01):
		if(sentido == 0):
			return False;
		elif(sentido > 0):
			self.state(Platform.__RIGHT)
		elif(sentido < 0):
			self.state(Platform.__LEFT)

		self.setVelocity(70);	#TODO: elegir velocidad adecuada
		time.sleep(t);
		self.stop();

		return True;

	def girar180(self):
		#TODO: set time
		return self.girarT(1, 2);

	def mover(self, sentido, velocidad, tiempo):
		if sentido>0:
			self.state(1)
			self.setVelocity(velocidad)
			time.sleep(float(tiempo))
		else:
			self.state(2)
			self.setVelocity(velocidad)
			time.sleep(float(tiempo))

		self.stop()
		time.sleep(0.1)

	def avanzarLento(self):
		#TODO: setear velocidad correcta
		self.state(1);
		self.setVelocity(40);

	def avanzarRapido(self):
		#TODO: setear velocidad correcta
		self.state(1);
		self.setVelocity(75);

	def avanzarMuyRapido(self):
		#TODO: setear velocidad correcta
		self.state(1);
		self.setVelocity(100);

	def avanzarMuyPoco(self):
		#TODO: setear tiempo
		self.avanzarLento();
		time.sleep(0.3);
		self.state(0);
		time.sleep(0.1);

	def avanzarPoco(self):
		#TODO: setear tiempo
		self.avanzarLento();
		time.sleep(0.95);
		self.state(0);
		time.sleep(0.1);

	def avanzarHarto(self):
		#TODO: setear tiempo
		time.sleep(5);
		self.avanzarMuyRapido();
		time.sleep(3);
		self.state(0);
		time.sleep(0.1);

	def retrocederLento(self):
		#TODO: setear velocidad correcta
		self.state(2);
		self.setVelocity(40);

	def retrocederRapido(self):
		#TODO: setear velocidad correcta
		self.state(2);
		self.setVelocity(75);

	def retrocederPoco(self):
		#TODO: setear tiempo
		self.retrocederLento();
		time.sleep(0.9);
		self.state(0);
		time.sleep(0.1);

	def retrocederMuyPoco(self):
		#TODO: setear tiempo
		self.retrocederLento();
		time.sleep(0.5);
		self.state(0);
		time.sleep(0.1);

	def retrocederHarto(self):
		#TODO: setear tiempo
		self.retrocederMuyRapido();
		time.sleep(25);
		self.state(0);
		time.sleep(0.1);
	
if __name__=="__main__":
	GPIO.setwarnings(False)
	movement = Platform();
	
	# FORWARD
	print "FORWARD"
	movement.setVelocity(10)
	movement.state(1)
	time.sleep(0.5)
	movement.setVelocity(30)
	time.sleep(0.5)
	movement.setVelocity(60)
	time.sleep(0.5)
	movement.setVelocity(85)
	time.sleep(0.5)
	movement.setVelocity(100)
	time.sleep(0.5)
	
	print "RIGHT"
	# RIGHT
	movement.setVelocity(20)
	movement.state(4)
	time.sleep(0.5)
	movement.setVelocity(50)
	time.sleep(0.5)
	movement.setVelocity(75)
	time.sleep(0.5)
	movement.setVelocity(100)
	time.sleep(0.5)
	
	# BACKWARD
	print "BACKWARD"
        movement.setVelocity(20)
        movement.state(2)
        time.sleep(0.5)
        movement.setVelocity(50)
        time.sleep(0.5)
        movement.setVelocity(75)
        time.sleep(0.5)
        movement.setVelocity(100)
        time.sleep(0.5)
	
	# LEFT
	print "LEFT"
        movement.setVelocity(20)
        movement.state(4)
        time.sleep(0.5)
        movement.setVelocity(50)
        time.sleep(0.5)
        movement.setVelocity(75)
        time.sleep(0.5)
        movement.setVelocity(100)
        time.sleep(0.5)
	
	# STOP
	print "STOP"
	movement.state(0)
