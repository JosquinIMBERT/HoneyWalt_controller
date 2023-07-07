# External
import argparse, os, signal, threading

# Internal
from config import get_conf

from tools.traffic import Traffic
from tools.tunnels import Tunnels
from tools.honeypot import HoneypotManager
from tools.state import StateManager
from tools.vm import VMManager

from client.controller import ClientController
from door.global_controller import DoorGlobalController
from vm.controller import VMController

# Common
from common.utils.files import *
from common.utils.logs import *

server = None

def handle(signum, frame):
	global server
	if server is not None:
		server.stop()

class ControllerServer:
	"""ControllerServer"""
	def __init__(self, ip_white_list=[]):
		log(INFO, "ControllerServer: building the door global controller")
		self.doors = DoorGlobalController(self)

		log(INFO, "ControllerServer: building the VM controller")
		self.vm = VMController(self)

		log(INFO, "ControllerServer: building the client controller")
		self.client = ClientController(self)

		log(INFO, "ControllerServer: building the tunnels controller")
		self.tunnels = Tunnels(self)

		log(INFO, "ControllerServer: building the traffic controller")
		self.traffic = Traffic(self, ip_white_list=ip_white_list)

		log(INFO, "ControllerServer: building the honeypots manager")
		self.honeypot_manager = HoneypotManager(self)

		log(INFO, "ControllerServer: building the state manager")
		self.state_manager = StateManager(self)

		log(INFO, "ControllerServer: building the VM manager")
		self.vm_manager = VMManager(self)

		self.edit_config = get_conf()
		self.run_config  = {}
		self.need_commit = False

		signal.signal(signal.SIGINT, handle) # handle ctrl-C

	def start(self):
		self.client.start()

	def stop(self):
		try: self.client.stop()
		except Exception as err:
			log(ERROR, "ControllerServer.stop: failed to stop the client controller")
			log(ERROR, "ControllerServer.stop:", err)
		else:
			log(INFO, "ControllerServer.stop: client controller successfully stopped")

		try: self.vm.stop()
		except Exception as err:
			log(ERROR, "ControllerServer.stop: failed to stop the vm controller")
			log(ERROR, "ControllerServer.stop:", err)
		else:
			log(INFO, "ControllerServer.stop: vm controller successfully stopped")

		try: self.tunnels.stop_tunnels()
		except Exception as err:
			log(ERROR, "ControllerServer.stop: failed to stop the tunnels controller")
			log(ERROR, "ControllerServer.stop:", err)
		else:
			log(INFO, "ControllerServer.stop: tunnels controller successfully stopped")

		try: self.traffic.stop_control()
		except Exception as err:
			log(ERROR, "ControllerServer.stop: failed to stop the traffic controller")
			log(ERROR, "ControllerServer.stop:", err)
		else:
			log(INFO, "ControllerServer.stop: traffic controller successfully stopped")

		try: del self.doors
		except Exception as err:
			log(ERROR, "ControllerServer.stop: failed to stop the doors controller")
			log(ERROR, "ControllerServer.stop:", err)
		else:
			log(INFO, "ControllerServer.stop: doors controller successfully stopped")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='HoneyWalt Controller Daemon')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL)")
	parser.add_argument("-p", "--pid-file", nargs=1, help="Select a PID file")
	parser.add_argument("-w", "--ip-white-list", nargs=1, help="Select IPs to accept SSH connections from")

	options = parser.parse_args()

	# Log Level
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)
	log(INFO, "Using log level: "+str(get_log_level()))

	# PID file
	if options.pid_file is not None:
		pid_file_path = options.pid_file[0]
		from pathlib import Path
		path = Path(pid_file_path)
		if path.parent.exists():
			with open(pid_file_path, "w") as pid_file:
				pid_file.write(str(os.getpid()))
		log(INFO, "Using pid file: "+str(pid_file_path))

	# IP White List (from arguments)
	args_ips = []
	if options.ip_white_list is not None:
		args_ips = options.ip_white_list[0].split(",")

	# IP White List (from file)
	file_ips = []
	white_list_filepath = to_root_path("etc/whitelist.txt")
	if isfile(white_list_filepath):
		with open(white_list_filepath, "r") as white_list_file:
			file_ips = ",".join(white_list_file.read().split()).split(",")

	# IP White List (final)
	ip_white_list = args_ips + file_ips

	log(INFO, "Using whitelist: "+str(ip_white_list))

	threading.current_thread().name = "MainThread"

	server = ControllerServer(ip_white_list=ip_white_list)
	server.start()