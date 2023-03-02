# External
import os, sys

# Internal
from common.door.proto import *
from door.sock import DoorSocket
from common.utils.controller import Controller
from common.utils.misc import get_public_ip

class DoorController(Controller):
	def __init__(self, door):
		self.door = door
		self.socket = DoorSocket()

	def __del__(self):
		del self.socket
		del self.door

	def connect(self):
		self.socket.connect(self.door["ip"], self.door["port"])

	# CMD_DOOR_LIVE
	def connected(self):
		if self.socket.connected():
			self.socket.send_cmd(CMD_DOOR_LIVE)
			return self.socket.get_answer()
		else:
			return False

	# CMD_DOOR_FIREWALL_UP
	def firewall_up(self):
		self.socket.send_cmd(CMD_DOOR_FIREWALL_UP)
		res = self.socket.get_answer()
		return res

	# CMD_DOOR_FIREWALL_DOWN
	def firewall_down(self):
		self.socket.send_cmd(CMD_DOOR_FIREWALL_DOWN)
		return self.socket.get_answer()

	# CMD_DOOR_WG_KEYGEN
	def wg_keygen(self):
		self.socket.send_cmd(CMD_DOOR_WG_KEYGEN)
		return self.socket.get_answer()

	# CMD_DOOR_WG_UP
	def wg_up(self):
		self.socket.send_cmd(CMD_DOOR_WG_UP)
		return self.socket.get_answer()

	# CMD_DOOR_WG_DOWN
	def wg_down(self):
		self.socket.send_cmd(CMD_DOOR_WG_DOWN)
		return self.socket.get_answer()

	# CMD_DOOR_WG_ADD_PEER
	def wg_add_peer(self, pubkey, dev_id):
		self.socket.send_cmd(CMD_DOOR_WG_ADD_PEER)
		self.socket.send_obj({"pubkey":pubkey, "id": dev_id})
		return self.socket.get_answer()

	# CMD_DOOR_TRAFFIC_SHAPER_UP
	def traffic_shaper_up(self):
		self.socket.send_cmd(CMD_DOOR_TRAFFIC_SHAPER_UP)
		return self.socket.get_answer()

	# CMD_DOOR_TRAFFIC_SHAPER_DOWN
	def traffic_shaper_down(self):
		self.socket.send_cmd(CMD_DOOR_TRAFFIC_SHAPER_DOWN)
		return self.socket.get_answer()