#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

if __name__=="__main__":
	pwm = GPIO.PWM(17,100)
	pwm.start(0)
	try:
		while 1:
			for dc in range(0,30,1):
				pwm.ChangeDutyCycle(dc)
			for dc in range(30,-1, -1):
				pwm.ChangeDutyCycle(dc)
	except KeyboardInterrupt:
		pass
	
	pwm.stop()

GPIO.cleanup()
