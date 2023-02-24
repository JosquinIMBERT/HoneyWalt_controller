# External
import os, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from door.controller import DoorController

class DoorGlobalController:
	def __init__(self, doors):
		self.controllers = []
		for door in doors:
			self.controllers += [DoorController(door)]

	def __del__(self):
		for controller in self.controllers:
			del controller

	def start(self):
		for controller in self.controllers:
			controller.connect()

	def firewall_up(self):
		for controller in self.controllers:
			controller.firewall_up()
	
	def firewall_down(self):
		for controller in self.controllers:
			controller.firewall_down()

	def wg_keygen(self, door=None):
		keys = []
		for controller in self.controllers:
			keys += [controller.wg_keygen()]
		return keys

	def wg_up(self):
		for controller in self.controllers:
			controller.wg_up()

	def wg_down(self):
		for controller in self.controllers:
			controller.wg_down()

	def wg_gen_conf(self, door=None):
		for controller in self.controllers:
			controller.wg_gen_conf()

	def traffic_shaper_up(self):
		for controller in self.controllers:
			controller.traffic_shaper_up()

	def traffic_shaper_down(self):
		for controller in self.controllers:
			controller.traffic_shaper_down()