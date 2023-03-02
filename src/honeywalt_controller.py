import signal

from client.controller import ClientController
from door.global_controller import DoorGlobalController
import glob
from tools.cowrie import CowrieController
from tools.traffic import TrafficController
from tools.tunnels import TunnelsController
from common.utils.files import *
from vm.controller import VMController

def handle(signum, frame):
	glob.SERVER.stop()

class ControllerServer:
	"""ControllerServer"""
	def __init__(self):
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
		self.DOORS_CONTROLLER.start()
		self.VM_CONTROLLER.start()
		self.CLIENT_CONTROLLER.start()

	def stop(self):
		self.CLIENT_CONTROLLER.stop()
		self.VM_CONTROLLER.stop()
		self.DOORS_CONTROLLER.stop()
		self.COWRIE_CONTROLLER.stop()
		self.TUNNELS_CONTROLLER.stop()

if __name__ == '__main__':
	controller_server = ControllerServer()
	controller_server.start()