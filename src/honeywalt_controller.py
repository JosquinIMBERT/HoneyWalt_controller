# External
import argparse, signal, threading

# Internal
from client.controller import ClientController
from common.utils.files import *
from common.utils.logs import *
from config import get_conf
from door.global_controller import DoorGlobalController
from tools.traffic import TrafficController
from tools.tunnels import TunnelsController

from tools.honeypot import HoneypotManager
from tools.state import StateManager
from tools.vm import VMManager

from vm.controller import VMController

server = None

def handle(signum, frame):
	global server
	if server is not None:
		server.stop()

class ControllerServer:
	"""ControllerServer"""
	def __init__(self):
		log(INFO, "ControllerServer.__init__: creating the ControllerServer")
		
		self.doors    = DoorGlobalController(self)
		self.vm       = VMController(self)
		self.client   = ClientController(self)
		self.tunnels  = TunnelsController(self)
		self.traffic  = TrafficController(self)
		
		self.honeypot_manager = HoneypotManager(self)
		self.state_manager    = StateManager(self)
		self.vm_manager       = VMManager(self)

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

		try: self.tunnels.stop()
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

	options = parser.parse_args()
	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)

	threading.current_thread().name = "MainThread"

	controller_server = ControllerServer()
	controller_server.start()