import RPi.GPIO as GPIO
import termios, fcntl, sys, os
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
	
	def __init__(self, PIN_MOTOR1=22, PIN_DIRF1=23, PIN_DIRB1=24, PIN_MOTOR2=4, PIN_DIRF2=22, PIN_DIRB2=27, lowSpeed=0, highSpeed=100):
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
		
		self.velocity = 0
		GPIO.setup(PIN_MOTOR1, GPIO.OUT)
		self.pwm1 = GPIO.PWM(PIN_MOTOR1, Platform.__F)
		self.pwm1.start(self.velocity)
		
		GPIO.setup(PIN_MOTOR2, GPIO.OUT)
		self.pwm2 = GPIO.PWM(PIN_MOTOR2, Platform.__F)
		self.pwm2.start(self.velocity)
		
		self.state(Platform.__STOP)
	
	def __del__(self):
		self.pwm1.stop()
		self.pwm2.stop()
		
		GPIO.cleanup()
	
	
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
			GPIO.output(self.pin_dir1f, 1)
			GPIO.output(self.pin_dir1b, 0)
			GPIO.output(self.pin_dir2f, 0)
			GPIO.output(self.pin_dir2b, 1)
		elif(newState == Platform.__RIGHT):
			#set direction outputs to ((0,1),(1,0))
			GPIO.output(self.pin_dir1f, 0)
			GPIO.output(self.pin_dir1b, 1)
			GPIO.output(self.pin_dir2f, 1)
			GPIO.output(self.pin_dir2b, 0)
		else:
			self.state(Platform.__STOP)
	
if __name__=="__main__":
        GPIO.setwarnings(False)
        movement = Platform()

        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        def UP():
            #FORWARD    
            movement.setVelocity(vel)
            movement.state(1)
            time.sleep(0.5)    
            print 'You mov FORDWARD with vel ' + repr(vel) + '\n'
         
        def DOWN():
            # BACKWARD
            movement.setVelocity(vel)
            movement.state(2)
            time.sleep(0.5)
            print 'You mov BACKWARD with vel ' + repr(vel) + '\n'
         
        def LEFT():
            # LEFT
            movement.setVelocity(vel)
            movement.state(4)
            time.sleep(0.5)    
            print 'You mov LEFT with vel ' + repr(vel) + '\n'
         
        def RIGHT():
            # RIGHT
            movement.setVelocity(vel)
            movement.state(3)
            time.sleep(0.5)
            print 'You mov RIGHT with vel ' + repr(vel) + '\n'

        def STOP():
            #STOP    
            global vel
            vel = 0
            movement.state(0)
            print 'You STOP\n'

        def EXIT():
            print 'exit program'
            #STOP    
            global vel
            vel = 0
            movement.state(0)
            sys.exit(0)

        def VEL_UP():
            global vel
            aux = vel
            aux += 10 
            if aux > 100 :
                vel = 100
            else:
                vel += 10

            movement.setVelocity(vel)    
            print 'You UP SET vel to ' + repr(vel) + '\n'

        def VEL_DOWN():
            global vel
            aux = vel
            aux -= 10
            if aux < 0 :
                vel = 0
            else:
                vel -= 10
							
	    movement.setVelocity(vel)	    				
            print 'You DOWN SET vel to ' + repr(vel) + '\n'

        options = {'w' : UP,
                        's' : DOWN,
                        'a' : LEFT,
                        'd' : RIGHT,
                        'x' : STOP,
                        'e' : VEL_UP,
                        'q' : VEL_DOWN,
                        '\x1b' : EXIT       
        }

        try:
            vel = 0
            while 1:
                try:
                    c = sys.stdin.read(1)
                    print "Got character", repr(c)
                    options[str(c)]()
                except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)       

