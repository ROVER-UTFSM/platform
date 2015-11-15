# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time 

class Claw(object):
	"""
	Fixs the maxiumim and minimum duty cycles (angles) for the servos of the claw
	and allows to open and close it with those values.
	"""

	GPIO.setmode(GPIO.BCM)
	
	__F = 42		# 42
	
	__forceps_max = 9.4	# 9.4
	__forceps_min = 4.0	# 4.0
	
	__lifter_max = 10.0	# 10.0
	__lifter_min = 4.5	# 4.5
	
	__smooth_factor = 5
	
	
	def __init__(self, PIN_lifter=17, PIN_forceps=18):
		GPIO.setup(PIN_lifter, GPIO.OUT)
		GPIO.setup(PIN_forceps, GPIO.OUT)
		
		self.lifter_pwm = GPIO.PWM(PIN_lifter, self.__F)
		self.lifter_pwm.start(self.__lifter_min)
		
		self.forceps_pwm = GPIO.PWM(PIN_forceps, self.__F)
		self.forceps_pwm.start(self.__forceps_max)
		
	
	def __del__(self):
		self.lifter_pwm.stop()
		self.forceps_pwm.stop()
		
		GPIO.cleanup()
	
	def start(self):
		#TODO: pwm.start() here or in __init__()???
		pass
	
	# --- PARTE ESCENCIAL ---

	### lifter methods
	def up(self):
		self.lifter_pwm.ChangeDutyCycle(self.__lifter_min)

	def down(self):
		self.lifter_pwm.ChangeDutyCycle(self.__lifter_max)
	
	def upSmooth(self):
		for dc in range(self.__lifter_max, self.__lifter_min-0.1, -(self.__lifter_max-self.__lifter_min)/self.__smooth_factor):
			self.lifter_pwm.ChangeDutyCycle(dc)
			time.sleep(0.1)
	
	def downSmooth(self):
		for dc in range(self.__lifter_min, self.__lifter_max+0.1, (self.__lifter_max-self.__lifter_min)/self.__smooth_factor):
			self.lifter_pwm.ChangeDutyCycle(dc)
			time.sleep(0.1)
	
	### forceps methods
	def open(self):
		self.forceps_pwm.ChangeDutyCycle(self.__forceps_min)
	
	def close(self):
		self.forceps_pwm.ChangeDutyCycle(self.__forceps_max)
	
	def openSmooth(self):
		for dc in range(self.__forceps_max*self.__smooth_factor, self.__forceps_min*self.__smooth_factor-0.1, -self.__smooth_factor):
			self.forceps_pwm.ChangeDutyCycle(dc)
			time.sleep(0.1)
	
	def closeSmooth(self):
		for dc in range(self.__forceps_min*self.__smooth_factor, self.__forceps_max*self.__smooth_factor-0.1, -(self.__forceps_max-self.__forceps_min)/self.__smooth_factor):
			self.forceps_pwm.ChangeDutyCycle(dc)
			time.sleep(0.1)

	#  --- FIN PARTE ESCENCIAL --

	def agarrar(self):
		self.open()
		time.sleep(0.5)
		self.close()
		time.sleep(1)
		self.up()
		time.sleep(1)

	def dejar(self):
		self.open()
		time.sleep(1)
		self.up()
		time.sleep(1.5)
		self.close()
		time.sleep(0.5)

if __name__=="__main__":
	garra = Claw()
	
	time.sleep(2)
	print "Open"
	garra.open()
	garra.up()
	time.sleep(2)
	print "Close"
	garra.close()
	garra.down()
	time.sleep(2)
	print "Open"
	garra.open()
	time.sleep(1)
