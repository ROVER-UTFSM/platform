import RPi.GPIO as GPIO
import termios, fcntl, sys, os
import time
import Platform

	
if __name__=="__main__":
        GPIO.setwarnings(False)
        movement = Platform.Platform()

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

