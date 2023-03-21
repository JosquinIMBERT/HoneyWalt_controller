# External
import argparse, signal, threading

# Internal
from client.controller import ClientController
from common.utils.files import *
from common.utils.logs import *
from config import get_conf
from door.global_controller import DoorGlobalController
import glob
from tools.cowrie import CowrieController
from tools.traffic import TrafficController
from tools.tunnels import TunnelsController
from vm.controller import VMController

def handle(signum, frame):
	glob.SERVER.stop()

class ControllerServer:
	"""ControllerServer"""
	def __init__(self):
		log(INFO, "ControllerServer.__init__: creating the ControllerServer")
		glob.init(
			self,
			get_conf(),
			to_root_path("var/key/id_olim"),
			to_root_path("var/key/id_olim.pub"),
			to_root_path("var/key/id_door"),
			to_root_path("var/key/id_door.pub")
		)
		self.DOORS_CONTROLLER = DoorGlobalController()
		self.VM_CONTROLLER = VMController()
		self.CLIENT_CONTROLLER = ClientController()
		self.COWRIE_CONTROLLER = CowrieController()
		self.TUNNELS_CONTROLLER = TunnelsController()
		self.TRAFFIC_CONTROLLER = TrafficController()
		signal.signal(signal.SIGINT, handle) # handle ctrl-C

	def start(self):
		self.CLIENT_CONTROLLER.start()
		self.CLIENT_CONTROLLER.run()

	def stop(self):
		self.CLIENT_CONTROLLER.stop()
		self.VM_CONTROLLER.stop()
		self.COWRIE_CONTROLLER.stop()
		self.TUNNELS_CONTROLLER.stop()
		del self.DOORS_CONTROLLER

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