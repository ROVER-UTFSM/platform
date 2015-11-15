#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

if __name__=="__main__":
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17, GPIO.OUT)
	
	pwm = GPIO.PWM(17, 42)
	pwm.start(70)
	
	try:
		interval = ()
		for f in range(100, 10, -10):
		# Change period from 10 to 100[ms]
			pwm.ChangeFrequency(f)
			print "Period ", 1000/f
			
			ans = raw_input("")
			if ans == "s":
				interval = interval, 1000/f
				
	except KeyboardInterrupt, SystemExit:
		pass
	
	print("Valid periods: ")
	for p in interval:
		print p
		
	pwm.stop()
	GPIO.cleanup()

