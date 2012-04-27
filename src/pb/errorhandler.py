import sys

initializing = 0 # increase when you're executing initialization commands; this will disable printing of error messages and should_exit_python!
should_exit_python = 0

def last_error():
	tmp = last_error.last
	last_error.last = 0
	return tmp
last_error.last = 0

def exit(level = 0, message = None):
	# level:
	# 	0 = ok
	# 	1 = args error
	# 	2 = authentication error
	# 	3 = soap fault
	if (not (message is None)) and (initializing == 0):
		print message
		if should_exit_python > 0:
			sys.exit(level)
	if last_error.last == 0:
		last_error.last = level

class ArgsError:
	
	def __init__(self, message = None):
		exit(1, "Invalid arguments" + ("" if message is None else ": " + message))

