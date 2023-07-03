# External
from sshtunnel import SSHTunnelForwarder
from string import Template

# Common
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

# We use sshtunnel for local port forwarding (i.e. tunnels like the one we open with -L ssh option)
# We use autossh for remote port forwarding (i.e. tunnels like the one we open with -R ssh option)

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
			local_port = Tunnels.TUNNEL_PORTS+int(honeypot["id"])

			# Tunnel controller -> device
			internal_tunnel = SSHTunnelForwarder(
				ssh_address         = '10.0.0.2',
				ssh_port            = 22,
				ssh_username        = "root",
				ssh_private_key     = Tunnels.VM_PRIV_KEY,
				local_bind_address  = ("127.0.0.1", local_port),
				remote_bind_address = (honeypot["device"]["ip"], 22)
			)
			self.internal_ssh_tunnels += [internal_tunnel]
			internal_tunnel.start()

			# Tunnel door -> controller
			external_tunnel = self._start_external_tunnel(
				pid_file = "external-tunnel-"+str(local_port),
				src_addr = "127.0.0.1",
				srd_port = Tunnels.TUNNEL_PORTS,
				dst_addr = "127.0.0.1",
				dst_port = local_port,
				host     = honeypot["door"]["host"],
				port     = Tunnels.REAL_SSH,
				user     = "root",
				privkey  = Tunnels.DOOR_PRIV_KEY
			)
			if external_tunnel:
				self.external_ssh_tunnels += [external_tunnel]
			else:
				log(ERROR, "failed to start external tunnel for ssh in honeypot "+ str(honeypot["id"]))

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
				local_port = Tunnels.EXPOSE_PORTS+(int(honeypot["id"])*Tunnels.PORTS_LIMIT)+cpt

				# Controller --> Device
				internal_tunnel = SSHTunnelForwarder(
					ssh_address         = "10.0.0.2",
					ssh_port            = 22,
					ssh_username        = "root",
					ssh_private_key     = Tunnels.VM_PRIV_KEY,
					local_bind_address  = ("127.0.0.1", local_port),
					remote_bind_address = (honeypot["device"]["ip"], port)
				)
				self.internal_other_tunnels += [internal_tunnel]
				internal_tunnel.start()

				# Door --> Controller
				external_tunnel = self._start_external_tunnel(
					pid_file = "external-tunnel-"+str(local_port),
					src_addr = "0.0.0.0",
					srd_port = port,
					dst_addr = "127.0.0.1",
					dst_port = local_port,
					host     = honeypot["door"]["host"],
					port     = Tunnels.REAL_SSH,
					user     = "root",
					privkey  = Tunnels.DOOR_PRIV_KEY
				)
				if external_tunnel:
					self.external_other_tunnels += [external_tunnel]
				else:
					log(ERROR, "failed to start external tunnel for port " + str(port) + " in honeypot "+ str(honeypot["id"]))

				cpt += 1

	def _start_external_tunnel(self, pid_file, src_addr, src_port, dst_addr, dst_port, user, host, port, privkey):
		template = Template("export AUTOSSH_PIDFILE='${pid_file}'; \
			autossh -M 0 -f -N \
			-R ${src_addr}:${src_port}:${dst_addr}:${dst_port} \
			${user}@${host} -p ${port} -i ${privkey}; \
			cat ${pid_file}")

		command = template.substitute({
			"pid_file" : pid_file,
			"src_addr" : src_addr,
			"src_port" : src_port,
			"dst_addr" : dst_addr,
			"dst_port" : dst_port,
			"user"     : user,
			"host"     : host,
			"port"     : port,
			"privkey"  : privkey,
		})

		pid = run(command, output=True)

		try: pid = int(pid)
		except: return None
		else: return pid

	def _stop_external_tunnel(self, pid):
		try: run("kill "+str(pid))
		except: pass


	#######################
	#     STOP TUNNELS    #
	#######################

	# For additional ports (not ssh)
	def stop_other(self):
		for external_tunnel in self.external_other_tunnels:
			self._stop_external_tunnel(external_tunnel)
		for internal_tunnel in self.internal_other_tunnels:
			internal_tunnel.stop()
		self.external_other_tunnels = []
		self.internal_other_tunnels = []

	def stop_ssh(self):
		for external_tunnel in self.external_ssh_tunnels:
			self._stop_external_tunnel(external_tunnel)
		for internal_tunnel in self.internal_ssh_tunnels:
			internal_tunnel.stop()
		self.external_ssh_tunnels = []
		self.internal_ssh_tunnels = []

	def stop_tunnels(self):
		self.stop_other()
		self.stop_ssh()