# External
import os, sys

# Internal
from common.utils.logs import *
from common.utils.misc import *
import common.utils.settings as settings

from door.controller import DoorController

class DoorGlobalController:
	def __init__(self, server):
		self.server = server
		self.controllers = {}

	def __del__(self):
		for honeyid, controller in self.controllers.items():
			del controller

	def reload(self, config, set_config=False):
		log(INFO, "DoorGlobalController.reload: reloading the DoorGlobalController")
		for honeyid, controller in self.controllers.items():
			del controller
		self.controllers = {}
		for honeypot in config["honeypots"]:
			self.controllers[str(honeypot["id"])] = DoorController(self.server, honeypot)
			if set_config:
				self.controllers[str(honeypot["id"])].set_config()

	def firewall_up(self):
		for honeyid, controller in self.controllers.items():
			controller.firewall_up()
	
	def firewall_down(self):
		for honeyid, controller in self.controllers.items():
			controller.firewall_down()

	def wg_keygen(self, door=None):
		for honeyid, controller in self.controllers.items():
			controller.wg_keygen()

	def wg_up(self):
		for honeyid, controller in self.controllers.items():
			controller.wg_up()

	def wg_down(self):
		for honeyid, controller in self.controllers.items():
			controller.wg_down()

	def wg_reset(self):
		for honeyid, controller in self.controllers.items():
			controller.wg_reset()

	def wg_set_peer(self):
		for honeyid, controller in self.controllers.items():
			controller.wg_set_peer()

	def shaper_up(self):
		for honeyid, controller in self.controllers.items():
			controller.shaper_up()

	def shaper_down(self):
		for honeyid, controller in self.controllers.items():
			controller.shaper_down()

	def cowrie_start(self):
		for honeyid, controller in self.controllers.items():
			controller.cowrie_start()

	def cowrie_stop(self):
		for honeyid, controller in self.controllers.items():
			controller.cowrie_stop()

	def cowrie_configure(self):
		for honeyid, controller in self.controllers.items():
			controller.cowrie_configure()

	def cowrie_running(self):
		cpt = 0
		for honeyid, controller in self.controllers.items():
			if controller.cowrie_is_running(): cpt += 1
		return cpt

	def commit(self):
		for honeyid, controller in self.controllers.items():
			controller.commit()
