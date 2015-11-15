#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

if __name__=="__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17, GPIO.OUT)
	
	pwm = GPIO.PWM(17, 42)
	pwm.start(0)
	
	try:
		interval = ()
		for dc in range(0, 101, 5):
		# Change duty cycle from 0 to 100
			pwm.ChangeDutyCycle(dc)
			ans = raw_input("")
			if ans == "s":
				interval = interval, dc
		
		min_dc = interval[0]
		for dc in range(interval[1], -1, -1):
		# From minimum DC found 'till user do not hit "s"
			pwm.ChangeDutyCycle(dc)
			ans = raw_input("")
			if ans == "s":
				min_dc = dc
			else:
				break
		
		max_dc = interval[-1]
		for dc in range(interval[-1], 101, 1):
		# From maximum DC found 'till user do not hit "s"
			pwm.ChangeDutyCycle(dc)
			ans = raw_input("")
			if ans == "s":
				max_dc = dc
			else:
				break
		
		print("Min duty cycle: ", min_dc)
		print("Max duty cycle: ", max_dc)
		
	except KeyboardInterrupt, SystemExit:
		pass
	
	pwm.stop()
	GPIO.cleanup()

