# External
import os, sys, traceback

global LOG_LEVEL, COMMAND, DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = 0
COMMAND = 4
DEBUG = 3
INFO = 2
WARNING = 1
ERROR = 0

def get_trace(start_func="main", nb_off=2):
	calls = []
	start = False
	for frame in traceback.extract_stack():
		if frame.name == start_func:
			start = True
		elif start:
			calls += [ frame.name ]
	calls = ">".join(calls[:-nb_off])
	return calls

# Print an error and exit
def eprint(*args, exit=True, **kwargs):
    log(ERROR, *args, **kwargs)
    if exit:
    	sys.exit(1)

def log(level, *args, **kwargs):
	if level <= LOG_LEVEL:
		if level == ERROR:
			trace = get_trace(nb_off=3)+":"
			print("[ERROR]", trace, *args, file=sys.stderr, **kwargs)
		elif level == WARNING:
			trace = get_trace()+":"
			print("[WARNING]", trace, *args, **kwargs)
		elif level == INFO:
			print("[INFO]", *args, **kwargs)
		elif level == DEBUG:
			print("[DEBUG]", *args, **kwargs)
		elif level == COMMAND:
			print("[COMMAND]", *args, **kwargs)

def set_log_level(log_level):
	global LOG_LEVEL

	if log_level=="ERROR":
		LOG_LEVEL = ERROR
	elif log_level=="WARNING":
		LOG_LEVEL = WARNING
	elif log_level=="INFO":
		LOG_LEVEL = INFO
	elif log_level=="DEBUG":
		LOG_LEVEL = DEBUG
	elif log_level=="CMD":
		LOG_LEVEL = COMMAND
	else:
		print("utils.logs.set_log_level: invalid log level")
		sys.exit(1)