# External
import errno, os, signal, subprocess, sys
from os.path import exists
from string import Template

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from utils.logs import *

# Kill a process using the file "filename"
# Several methods can be used:
#	filetype=pid	=> read the pid in the file
#	filetype=ssh	=> the file is an ssh control socket
def kill_from_file(filename, filetype="pid"):
	if filetype=="pid":
		with open(filename, "r+") as pidfile:
			pid = pidfile.read()
			pidfile.seek(0)
			pidfile.truncate()
			if pid != "":
				pid = int(pid)
				os.kill(pid, signal.SIGTERM)
	elif filetype=="ssh":
		kill_cmd = "ssh -S "+filename+" -O exit 0.0.0.0"
		res = subprocess.run(kill_cmd, shell=True ,check=True, text=True)
		if res.returncode != 0:
			eprint("failed to kill and ssh tunnel")
	else:
		eprint("unknown file type")

def run(command, error, output=False, timeout=None):
	log(COMMAND, command)
	res = subprocess.run(command, shell=True ,check=True, text=True, capture_output=output, timeout=timeout)
	if res.returncode != 0:
		eprint(error)
	if output:
		return str(res.stdout)
	else:
		return None

# Source: https://github.com/giampaolo/psutil/blob/5ba055a8e514698058589d3b615d408767a6e330/psutil/_psposix.py#L28-L53
# Check whether a PID corresponds to a running process (kill 0 allows to test the PID without killing any process)
def pid_exists(pid):
	if pid == 0:
		return True
	try:
		os.kill(pid, 0)
	except OSError as err:
		if err.errno == errno.ESRCH:
			return False
		elif err.errno == errno.EPERM:
			return True
		else:
			raise err
	else:
		return True

# Read a PID from a file and return it as a string if it exists
def read_pid_file(file):
	if exists(file):
		with open(file, "r") as pidfile:
			pid = pidfile.read().strip()
			if pid != "" and pid_exists(int(pid)):
				return str(int(pid))
	return None