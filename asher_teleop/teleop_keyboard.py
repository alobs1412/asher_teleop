import sys
import tty
import termios
import rclpy
from geometry_msgs.msg import Twist
MSG = """
Asher Holonomic Teleop
----------------------
w/s   : forward / back
a/d   : strafe left / right
q/e   : rotate left / right
space : stop
CTRL-C: quit
"""

# key = (forward/backward, strafe left/right, rotation)
keys = {
    'w': ( 1.0,  0.0,  0.0),
    's': (-1.0,  0.0,  0.0),
    'a': ( 0.0,  1.0,  0.0),
    'd': ( 0.0, -1.0,  0.0),
    'q': ( 0.0,  0.0,  1.0),
    'e': ( 0.0,  0.0, -1.0),
}

linear_speed = 0.3 #m/s
angular_speed = 0.5 #rad/s

# Reading the Keyboard
# gets key instant it is pressed
def get_key():
	settings = termios.tcgetattr(sys.stdin) # save current terminal settings
	tty.setraw(sys.stdin.fileno()) # switch to raw mode so every keypress is sent immediately
	key = sys.stdin.read(1) # read exactly 1 character
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings) # restore terminal back to normal right after
	return key

# main operation
def main():
	rclpy.init() #starts ROS2
	node = rclpy.create_node('asher_teleop') # registers program on ROS network
	pub  = node.create_publisher(Twist, '/cmd_vel', 10) 

	print(MSG)
	
	try:
		while True:
			key = get_key()
			
			if key == '\x03': # '...' = CTRL C
				break

			msg = Twist()
			
			if key in keys:
				x,y,z = keys[key]
				msg.linear.x = x*linear_speed
				msg.linear.y = y*linear_speed
				msg.angular.z = z*angular_speed
			pub.publish(msg)
	finally:
		pub.publish(Twist())
		rclpy.shutdown()

if __name__ == '__main__':
	main()


# Complete Flow For Notes
''' 
User presses 'w'
- get_key() captures it instantly
- keys['w'] = (1,0,0) = (forward, no strafe, no rotation)
- msg.linear.x = forward by linear speed = 1.0 * 0.3 = 0.3
- pub.publish(msg) = display movement
- /cmd_vel topic receives the message
- base driver reads it and wheels spin forward
'''
'''
Other Notes
1. create_publisher is same as making a python list with .append()
This line of code tells ROS you are going to be sending 
'''
