# External
from sshtunnel import SSHTunnelForwarder

# Common
from common.utils.files import *
from common.utils.logs import *

class Tunnels:

	VM_PRIV_KEY   = to_root_path("var/key/id_olim")
	VM_PUB_KEY    = to_root_path("var/key/id_olim.pub")
	DOOR_PRIV_KEY = to_root_path("var/key/id_door")
	DOOR_PUB_KEY  = to_root_path("var/key/id_door.pub")
	TUNNEL_PORTS  = 2000
	EXPOSE_PORTS  = 7000
	PORTS_LIMIT   = 10
	REAL_SSH      = 1312

	def __init__(self, server):
		self.server = server
		self.internal_ssh_tunnels   = []
		self.external_ssh_tunnels   = []
		self.internal_other_tunnels = []
		self.external_other_tunnels = []

	def __del__(self):
		pass


	#######################
	#	 START TUNNELS	  #
	#######################

	# Start tunnels for cowrie traffic
	def start_ssh(self):
		for honeypot in self.server.run_config["honeypots"]:
			# Tunnel controller -> device
			internal_tunnel = SSHTunnelForwarder(
				ssh_address         = '10.0.0.2',
				ssh_port            = 22,
				ssh_username        = "root",
				ssh_private_key     = Tunnels.VM_PRIV_KEY,
				local_bind_address  = ("127.0.0.1", Tunnels.TUNNEL_PORTS+int(honeypot["id"])),
				remote_bind_address = (honeypot["device"]["ip"], 22)
			)
			# Tunnel door -> controller
			external_tunnel = SSHTunnelForwarder(
				ssh_address         = honeypot["door"]["host"],
				ssh_port            = Tunnels.REAL_SSH,
				ssh_username        = "root",
				ssh_private_key     = Tunnels.DOOR_PRIV_KEY,
				local_bind_address  = ("127.0.0.1", Tunnels.TUNNEL_PORTS+int(honeypot["id"])),
				remote_bind_address = ("127.0.0.1", Tunnels.TUNNEL_PORTS)
			)
			self.internal_ssh_tunnels += [internal_tunnel]
			self.external_ssh_tunnels += [external_tunnel]
			internal_tunnel.start()
			external_tunnel.start()

	# Start tunnels for other exposed ports
	def start_other(self):
		for honeypot in self.server.run_config["honeypots"]:
			if len(honeypot["ports"]) > Tunnels.PORTS_LIMIT:
				log(WARNING, "We only accept "+str(Tunnels.PORTS_LIMIT)
					+" exposed ports per honeypot - honeypot "+str(honeypot["id"])
					+"does not meet this requirement")
				continue
			cpt = 0
			for port in honeypot["ports"]:
				# Controller --> Device
				internal_tunnel = SSHTunnelForwarder(
					ssh_address         = "10.0.0.2",
					ssh_port            = 22,
					ssh_username        = "root",
					ssh_private_key     = Tunnels.VM_PRIV_KEY,
					local_bind_address  = ("127.0.0.1", Tunnels.EXPOSE_PORTS+(int(honeypot["id"])*Tunnels.PORTS_LIMIT)+cpt),
					remote_bind_address = (honeypot["device"]["ip"], port)
				)
				# Door --> Controller
				external_tunnel = SSHTunnelForwarder(
					ssh_address         = honeypot["door"]["host"],
					ssh_port            = Tunnels.REAL_SSH,
					ssh_username        = "root",
					ssh_private_key     = Tunnels.DOOR_PRIV_KEY,
					local_bind_address  = ("127.0.0.1", Tunnels.EXPOSE_PORTS+(int(honeypot["id"])*Tunnels.PORTS_LIMIT)+cpt),
					remote_bind_address = ("0.0.0.0", port)
				)
				self.internal_other_tunnels += [internal_tunnel]
				self.external_other_tunnels += [external_tunnel]
				internal_tunnel.start()
				external_tunnel.start()
				cpt += 1


	#######################
	#     STOP TUNNELS    #
	#######################

	# For additional ports (not ssh)
	def stop_other(self):
		for external_tunnel in self.external_other_tunnels:
			external_tunnel.stop()
		for internal_tunnel in self.internal_other_tunnels:
			internal_tunnel.stop()
		self.external_other_tunnels = []
		self.internal_other_tunnels = []

	def stop_ssh(self):
		for external_tunnel in self.external_ssh_tunnels:
			external_tunnel.stop()
		for internal_tunnel in self.internal_ssh_tunnels:
			internal_tunnel.stop()
		self.external_ssh_tunnels = []
		self.internal_ssh_tunnels = []

	def stop_tunnels(self):
		self.stop_other()
		self.stop_ssh()