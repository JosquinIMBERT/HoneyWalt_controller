# External
import os, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from door.proto import *
from door.sock import DoorSocket
from utils.misc import get_public_ip

class DoorController:
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
			return self.socket.wait_confirm()
		else:
			return False

	# CMD_DOOR_FIREWALL_UP
	def firewall_up(self):
		self.socket.send_cmd(CMD_DOOR_FIREWALL_UP)
		self.socket.send_obj(get_public_ip())
		return self.socket.wait_confirm()

	# CMD_DOOR_FIREWALL_DOWN
	def firewall_down(self):
		self.socket.send_cmd(CMD_DOOR_FIREWALL_DOWN)
		return self.socket.wait_confirm()

	# CMD_DOOR_WG_KEYGEN
	def wg_keygen(self):
		self.socket.send_cmd(CMD_DOOR_WG_KEYGEN)
		keys = self.socket.recv_obj()
		if str(keys) == "0": # Failed
			return False
		else:
			return keys

	# CMD_DOOR_WG_UP
	def wg_up(self):
		self.socket.send_cmd(CMD_DOOR_WG_UP)
		return self.socket.wait_confirm()

	# CMD_DOOR_WG_DOWN
	def wg_down(self):
		self.socket.send_cmd(CMD_DOOR_WG_DOWN)
		return self.socket.wait_confirm()

	# CMD_DOOR_WG_GEN_CONF
	def wg_gen_conf(self, vm_wg_pubkey):
		self.socket.send_cmd(CMD_DOOR_WG_GEN_CONF)
		self.socket.send_obj(vm_wg_pubkey)
		return self.socket.wait_confirm()

	# CMD_DOOR_TRAFFIC_SHAPER_UP
	def traffic_shaper_up(self):
		self.socket.send_cmd(CMD_DOOR_TRAFFIC_SHAPER_UP)
		return self.socket.wait_confirm()

	# CMD_DOOR_TRAFFIC_SHAPER_DOWN
	def traffic_shaper_down(self):
		self.socket.send_cmd(CMD_DOOR_TRAFFIC_SHAPER_DOWN)
		return self.socket.wait_confirm()