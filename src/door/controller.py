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
		Controller.__init__(self)
		log(DEBUG, self.get_name()+".__init__: creating the DoorController for "+str(door["host"]))
		self.door = door
		self.socket = ClientSocket()
		self.socket.set_name("Socket(Controller-Door["+str(door["host"])+"])")

	def __del__(self):
		del self.socket
		del self.door

	def connect(self):
		return self.socket.connect(ip=self.door["host"], port=DOOR_PORT)

	# CMD_DOOR_LIVE
	def connected(self):
		return self.socket.exchange(commands=[CMD_DOOR_LIVE])

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