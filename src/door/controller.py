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
from tools.shaper import ControllerShaper
import common.utils.settings as settings

class ControllerService(IPService):
	def __init__(self):
		super().__init__()
		self.local_shaper = None

	def on_connect(self, conn):
		self.conn = conn
		self.local_shaper = self.conn._config["local_shaper"]

	def exposed_forward(self, packet):
		self.local_shaper.forward(packet)

class DoorController():
	def __init__(self, server, honeypot, timeout=10):
		# Honeypot information
		self.honeyid = honeypot["id"]
		self.honeypot = honeypot

		log(DEBUG, "Creating the DoorController for "+str(self.honeypot["door"]["host"]))
		
		self.server = server
		self.timeout = timeout
		self.shaper = ControllerShaper(settings.get("WIREGUARD_PORTS")+self.honeyid)
		self.shaper.set_peer(self)
		
		# RPyC connection to the door
		self.conn = rpyc.ssl_connect(
			self.honeypot["door"]["host"],
			port=DOOR_PORT,
			config={"allow_public_attrs": True, "sync_request_timeout": self.timeout, "local_shaper": self.shaper},
			keyfile=to_root_path("var/key/pki/private/controller-client.key"),
			certfile=to_root_path("var/key/pki/controller-client.crt"),
			ca_certs=to_root_path("var/key/pki/ca.crt"),
			service=ControllerService
		)
		self.conn.root.set_stdout(sys.stdout)
		self.conn.root.set_stderr(sys.stderr)
		self.conn.root.set_log_level(LOG_LEVEL)
		self.background_service = rpyc.BgServingThread(self.conn)

		# Sending initial configuration to the door
		self.set_config()

	def __del__(self):
		self.background_service.stop()
		del self.timeout
		del self.conn

	def call(self, func, *args, **kwargs):
		return json.loads(func(*args, **kwargs))

	def firewall_up(self):
		return self.call(self.conn.root.firewall_up)

	def firewall_down(self):
		return self.call(self.conn.root.firewall_down)

	def wg_keygen(self):
		res = self.call(self.conn.root.wg_keygen)
		self.honeypot["door"]["pubkey"] = res["pubkey"]
		self.honeypot["door"]["privkey"] = res["privkey"]
		return res

	def wg_up(self):
		return self.call(self.conn.root.wg_up)

	def wg_down(self):
		return self.call(self.conn.root.wg_down)

	def wg_reset(self):
		return self.call(self.conn.root.wg_reset)

	def wg_set_peer(self):
		pubkey = self.honeypot["device"]["pubkey"]
		return self.call(self.conn.root.wg_set_peer, pubkey)

	def shaper_up(self):
		res = self.call(self.conn.root.shaper_up)
		self.shaper.start()
		return res

	def shaper_down(self):
		self.shaper.stop()
		return self.call(self.conn.root.shaper_down)

	def cowrie_start(self):
		return self.call(self.conn.root.cowrie_start)

	def cowrie_stop(self):
		return self.call(self.conn.root.cowrie_stop)

	def cowrie_configure(self):
		return self.call(self.conn.root.cowrie_configure)

	def cowrie_is_running(self):
		return self.call(self.conn.root.cowrie_is_running)

	def forward(self, packet):
		return self.call(self.conn.root.forward, packet)

	def set_config(self):
		config = {
			"honeypot": {
				"id": self.honeyid,
				"door": {
					"privkey": None,
					"pubkey": None
				},
				"device": {
					"pubkey": None
				},
				"credentials": {
					"user": self.honeypot["credentials"]["user"],
					"pass": self.honeypot["credentials"]["pass"]
				}
			},
			"hpfeeds": {
				"server": self.server.run_config["hpfeeds"]["server"],
				"port": self.server.run_config["hpfeeds"]["port"],
				"identifier": self.server.run_config["hpfeeds"]["identifier"],
				"secret": self.server.run_config["hpfeeds"]["secret"]
			}
		}
		return self.call(self.conn.root.set_config, config)

	def commit(self):
		return self.call(self.conn.root.commit)