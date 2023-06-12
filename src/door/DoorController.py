# External
import json, os, rpyc, sys

# Internal
from common.door.proto import *
from common.utils.controller import Controller
from common.utils.files import *
from common.utils.logs import *
from common.utils.misc import get_public_ip
from common.utils.rpc import IPService
from common.utils.sockets import ClientSocket

class DoorController():
	def __init__(self, door, timeout=1):
		log(DEBUG, "Creating the DoorController for "+str(door["host"]))
		self.timeout = timeout
		self.door = door
		self.conn = rpyc.ssl_connect(
			self.door["host"],
			port=DOOR_PORT,
			config={"allow_public_attrs": True, "sync_request_timeout": self.timeout},
			keyfile=to_root_path("var/key/pki/private/controller-client.key"),
			certfile=to_root_path("var/key/pki/controller-client.crt"),
			ca_certs=to_root_path("var/key/pki/ca.crt"),
			service=IPService
		)
		self.conn.root.set_stdout(sys.stdout)
		self.conn.root.set_stderr(sys.stderr)
		self.conn.root.set_log_level(LOG_LEVEL)

	def __del__(self):
		del self.timeout
		del self.door
		del self.conn

	def call(self, func, *args, **kwargs):
		return json.loads(func(*args, **kwargs))

	# CMD_DOOR_FIREWALL_UP
	def firewall_up(self):
		return self.call(self.conn.root.firewall_up)

	# CMD_DOOR_FIREWALL_DOWN
	def firewall_down(self):
		return self.call(self.conn.root.firewall_down)

	# CMD_DOOR_WG_KEYGEN
	def wg_keygen(self):
		res = self.call(self.conn.root.wg_keygen)
		res["host"] = self.door["host"]
		return res

	# CMD_DOOR_WG_UP
	def wg_up(self):
		return self.call(self.conn.root.wg_up)

	# CMD_DOOR_WG_DOWN
	def wg_down(self):
		return self.call(self.conn.root.wg_down)

	# CMD_DOOR_WG_RESET
	def wg_reset(self):
		return self.call(self.conn.root.wg_reset)

	# CMD_DOOR_WG_ADD_PEER
	def wg_add_peer(self, pubkey, dev_id):
		return self.call(self.conn.root.wg_add_peer, pubkey, dev_id)

	# CMD_DOOR_TRAFFIC_SHAPER_UP
	def traffic_shaper_up(self):
		return self.call(self.conn.root.traffic_shaper_up)

	# CMD_DOOR_TRAFFIC_SHAPER_DOWN
	def traffic_shaper_down(self):
		return self.call(self.conn.root.traffic_shaper_down)