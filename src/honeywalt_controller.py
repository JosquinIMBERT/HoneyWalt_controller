import signal

import glob
from client.controller import ClientController
from door.global_controller import DoorGlobalController
from utils.files import *
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
		signal.signal(signal.SIGINT, handle) # handle ctrl-C

	def start(self):
		self.DOORS_CONTROLLER.start()
		self.VM_CONTROLLER.start()
		self.CLIENT_CONTROLLER.start()

	def stop(self):
		self.CLIENT_CONTROLLER.stop()
		self.VM_CONTROLLER.stop()
		self.DOORS_CONTROLLER.stop()

if __name__ == '__main__':
	controller_server = ControllerServer()
	controller_server.start()