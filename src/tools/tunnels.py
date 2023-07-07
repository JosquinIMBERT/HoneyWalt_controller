# External
from sshtunnel import SSHTunnelForwarder
from string import Template

# Common
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

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
			internal_tunnel = self._start_tunnel(
				pid_file = "internal-tunnel-"+str(local_port),
				src_addr = "127.0.0.1",
				src_port = local_port,
				dst_addr = honeypot["device"]["ip"],
				dst_port = 22,
				host     = "10.0.0.2",
				port     = 22,
				user     = "root",
				privkey  = Tunnels.VM_PRIV_KEY,
				external = False,
				ignore_unknown_host = True
			)
			if internal_tunnel:
				self.internal_ssh_tunnels += [internal_tunnel]
			else:
				log(ERROR, "failed to start internal tunnel for ssh in honeypot " + str(honeypot["id"]))

			# Tunnel door -> controller
			external_tunnel = self._start_tunnel(
				pid_file = "external-tunnel-"+str(local_port),
				src_addr = "127.0.0.1",
				src_port = Tunnels.TUNNEL_PORTS,
				dst_addr = "127.0.0.1",
				dst_port = local_port,
				host     = honeypot["door"]["host"],
				port     = Tunnels.REAL_SSH,
				user     = "root",
				privkey  = Tunnels.DOOR_PRIV_KEY,
				external = True
			)
			if external_tunnel:
				self.external_ssh_tunnels += [external_tunnel]
			else:
				log(ERROR, "failed to start external tunnel for ssh in honeypot " + str(honeypot["id"]))

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
				internal_tunnel = self._start_tunnel(
					pid_file = "internal-tunnel-"+str(local_port),
					src_addr = "127.0.0.1",
					src_port = local_port,
					dst_addr = honeypot["device"]["ip"],
					dst_port = port,
					host     = "10.0.0.2",
					port     = 22,
					user     = "root",
					privkey  = Tunnels.VM_PRIV_KEY,
					external = False,
					ignore_unknown_host = True
				)
				if internal_tunnel:
					self.internal_other_tunnels += [internal_tunnel]
				else:
					log(ERROR, "failed to start internal tunnel for port " + str(port) + " in honeypot " + str(honeypot["id"]))

				# Door --> Controller
				external_tunnel = self._start_tunnel(
					pid_file = "external-tunnel-"+str(local_port),
					src_addr = "0.0.0.0",
					src_port = port,
					dst_addr = "127.0.0.1",
					dst_port = local_port,
					host     = honeypot["door"]["host"],
					port     = Tunnels.REAL_SSH,
					user     = "root",
					privkey  = Tunnels.DOOR_PRIV_KEY,
					external = True
				)
				if external_tunnel:
					self.external_other_tunnels += [external_tunnel]
				else:
					log(ERROR, "failed to start external tunnel for port " + str(port) + " in honeypot " + str(honeypot["id"]))

				cpt += 1

	def _start_tunnel(self, pid_file, src_addr, src_port, dst_addr, dst_port, user, host, port, privkey, external, ignore_unknown_host=False):
		pid_file = to_root_path("run/tunnel/"+str(pid_file))

		if external:
			origin = "-R"
		else:
			origin = "-L"

		if ignore_unknown_host:
			option = "-o StrictHostKeyChecking=no"
		else:
			option = ""

		template = Template("export AUTOSSH_PIDFILE='${pid_file}'; \
			autossh -M 0 -f -N ${option} \
			${origin} ${src_addr}:${src_port}:${dst_addr}:${dst_port} \
			${user}@${host} -p ${port} -i ${privkey}; \
			cat ${pid_file}")

		command = template.substitute({
			"pid_file" : pid_file,
			"option"   : option,
			"origin"   : origin,
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
		else: return pid_file

	def _stop_tunnel(self, pid_file):
		try: kill_from_file(pid_file)
		except: pass


	#######################
	#     STOP TUNNELS    #
	#######################

	# For additional ports (not ssh)
	def stop_other(self):
		for external_tunnel in self.external_other_tunnels:
			self._stop_tunnel(external_tunnel)
		for internal_tunnel in self.internal_other_tunnels:
			self._stop_tunnel(internal_tunnel)
		self.external_other_tunnels = []
		self.internal_other_tunnels = []

	def stop_ssh(self):
		for external_tunnel in self.external_ssh_tunnels:
			self._stop_tunnel(external_tunnel)
		for internal_tunnel in self.internal_ssh_tunnels:
			self._stop_tunnel(internal_tunnel)
		self.external_ssh_tunnels = []
		self.internal_ssh_tunnels = []

	def stop_tunnels(self):
		self.stop_other()
		self.stop_ssh()


	#######################
	# VERIFY KNOWN HOSTS  #
	#######################

	def verify_known_host(self, host, port=None):
		port = Tunnels.REAL_SSH if port is None else port
		# Use: ssh-keygen -H -F '[host]:port' to check if we already know host:port
		res = run("ssh-keygen -H -F '["+host+"]:"+str(port)+"'", output=True)
		if res == "": return False
		return True