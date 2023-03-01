# External
import os, sys

# Internal
from door.controller import DoorController

class DoorGlobalController:
	def __init__(self, doors):
		self.controllers = {}
		for door in doors:
			self.controllers[str(door["id"])] = DoorController(door)

	def __del__(self):
		for door_id, controller in self.controllers.items():
			del controller

	def start(self):
		for door_id, controller in self.controllers.items():
			controller.connect()

	def firewall_up(self):
		for door_id, controller in self.controllers.items():
			controller.firewall_up()
	
	def firewall_down(self):
		for door_id, controller in self.controllers.items():
			controller.firewall_down()

	def wg_keygen(self, door=None):
		keys = []
		for door_id, controller in self.controllers.items():
			keys += [controller.wg_keygen()]
		return keys

	def wg_up(self):
		for door_id, controller in self.controllers.items():
			controller.wg_up()

	def wg_down(self):
		for door_id, controller in self.controllers.items():
			controller.wg_down()

	def wg_add_peer(self, peers):
		for door_id, controller in self.controllers.items():
			peer = find(peers, int(door_id), "door_id")
			controller.wg_add_peer(peer["pubkey"], peer["dev_id"])

	def traffic_shaper_up(self):
		for door_id, controller in self.controllers.items():
			controller.traffic_shaper_up()

	def traffic_shaper_down(self):
		for door_id, controller in self.controllers.items():
			controller.traffic_shaper_down()