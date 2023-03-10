# External
import os, sys

# Internal
from common.door.proto import *
from common.utils.controller import Controller
from common.utils.logs import *
from common.utils.misc import get_public_ip
from common.utils.sockets import ClientSocket

class DoorController(Controller):
	def __init__(self, door):
		log(DEBUG, "DoorController.__init__: creating the DoorController for "+str(door["host"]))
		self.door = door
		self.socket = ClientSocket()

	def __del__(self):
		del self.socket
		del self.door

	def connect(self):
		self.socket.connect(self.door["host"], DOOR_PORT)

	# CMD_DOOR_LIVE
	def connected(self):
		if self.socket.connected():
			return self.socket.exchange(commands=[CMD_DOOR_LIVE])
		else:
			return False

	# CMD_DOOR_FIREWALL_UP
	def firewall_up(self):
		return self.socket.exchange(commands=[CMD_DOOR_FIREWALL_UP])

	# CMD_DOOR_FIREWALL_DOWN
	def firewall_down(self):
		return self.socket.exchange(commands=[CMD_DOOR_FIREWALL_DOWN])

	# CMD_DOOR_WG_KEYGEN
	def wg_keygen(self):
		return self.socket.exchange(commands=[CMD_DOOR_WG_KEYGEN])

	# CMD_DOOR_WG_UP
	def wg_up(self):
		return self.socket.exchange(commands=[CMD_DOOR_WG_UP])

	# CMD_DOOR_WG_DOWN
	def wg_down(self):
		return self.socket.exchange(commands=[CMD_DOOR_WG_DOWN])

	# CMD_DOOR_WG_ADD_PEER
	def wg_add_peer(self, pubkey, dev_id):
		return self.socket.exchange(
			commands=[CMD_DOOR_WG_ADD_PEER],
			data={"pubkey":pubkey, "id": dev_id}
		)

	# CMD_DOOR_TRAFFIC_SHAPER_UP
	def traffic_shaper_up(self):
		return self.socket.exchange(commands=[CMD_DOOR_TRAFFIC_SHAPER_UP])

	# CMD_DOOR_TRAFFIC_SHAPER_DOWN
	def traffic_shaper_down(self):
		return self.socket.exchange(commands=[CMD_DOOR_TRAFFIC_SHAPER_DOWN])