#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

if __name__=="__main__":
	pwm = GPIO.PWM(17,50)
	pwm.start(0)
	try:
		while 1:
			for dc in range(300000,-1, -1):
				pwm.ChangeDutyCycle(50)
			for dc in range(300000,-1, -1):
				pwm.ChangeDutyCycle(20)
	except KeyboardInterrupt:
		pass
	
	pwm.stop()

GPIO.cleanup()
