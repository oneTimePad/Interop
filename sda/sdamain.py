"""
main program for SDA and interop related to SDA
this should be the first program started for sda
PLEASE refer to libinterop/types.py for information on the auvsi provided
objects
objects that used are:
	MovingObstacle
	StationaryObstacles
NOTE: although this might be confusing, this program is NOT called directly. It
is referenced indirectly by a program (that is in the interop repo, which you
don't need to worry about) that contacts the interoperability server and passes
you the obstacles. Below is a template that you should follow for this program
to work correctly with the rest.


There are two functions you need to fill (i.e. however you can import as many
modules and sources as you need): 

	async_routine:= this function is called at periodic points in time and
	passed the current status of the moving and stationary obstacles (formats
	described in function definition below). This allows you to update any
	global structures you have that keep track of the object states. However,
	this function should be as short as possible.

	sync_routine:= this function is the main program. it will constatly run as a
	normal program [i.e. synchronously]. for simplicity you could just import
	some other function you have in another source and just call it there.

"""


import threading #example only

my_lock = threading.Lock() #example only
myglobalvariable = 0 #example only


#TODO:fill in function definition
def async_routine(moving,stationary,error): #don't change function prototype

	"""
	

	moving:= list of moving obstacles in object format
	stationary:= list of stationary obstacles in object format
	NOTE: see libinterop/types.py for the structure of the object format
	moving = [MovingObstacle(...),MovingObstacle(...),...]
	same for stationary
	error:=an error is returned from the server when not equal to None

	NOTE OF Caution: be careful when editing global variables here,
	execution of this function is asynchronous of everything outside it.
	This means that is can happen at anytime. Thus you need to lock any global
	data using the following:

		import threading
		lock = threading.Lock()

		...
		# area where global variable is edited
		def handle_response(...):
			no lock
			with lock:
				do stuff with global variable
			no lock
		#stuff outside of handle_response where global variable is edited
		no lock
		with lock:
			do stuff with same global variable
		no lock

		BELOW is an actual example of locking
	"""

	global myglobalvariable # this is required wherever global vars are
	#referenced

	if error:
		print("error: %s" %(str(error)))
	"""
		all the work that gets done when receiving obstacle updates goes
		hanle_response
	"""
	#safe inside lock
	with my_lock:
		myglobalvariable+=1
	#outside lock, no longer safe
	#Example
	print("updating obstacle status ...",moving,stationary)





#TODO: add synchronus work here (everything that happens while waiting for
#obstacle position updates (i.e. rest of the SDA code [function, routines, etc]
#EXAMPLE:
#time imported for example only
import time #example only
def sync_routine():#don't change function prototype

	"""
	main sda routine: replace with one function call if you want but the program
	ends once this function returns... (i.e. it should NEVER return)


	"""

	global myglobalvariable #example only
	while True:
		print("Do some SDA stuff") #example only
		with my_lock: #example only ...
			myglobalvariable+=1
		time.sleep(2)


