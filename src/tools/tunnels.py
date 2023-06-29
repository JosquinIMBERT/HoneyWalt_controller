# External
from sshtunnel import SSHTunnelForwarder
from string import Template
import tempfile

# Common
from common.utils.files import *
from common.utils.logs import *
from common.utils.misc import *
from common.utils.system import *

class TunnelsController:

	VM_PRIV_KEY   = to_root_path("var/key/id_olim")
	VM_PUB_KEY    = to_root_path("var/key/id_olim.pub")
	DOOR_PRIV_KEY = to_root_path("var/key/id_door")
	DOOR_PUB_KEY  = to_root_path("var/key/id_door.pub")
	TUNNEL_PORTS  = 2000
	EXPOSE_PORTS  = 7000
	PORTS_LIMIT   = 10

	def __init__(self, server):
		log(INFO, "TunnelsController.__init__: creating the TunnelsController")
		self.server = server

	def __del__(self):
		pass

	def init_run(self):
		delete(to_root_path("run/ssh/external-others"), suffix=".pid")
		delete(to_root_path("run/ssh/internal-others"), suffix=".pid")
		delete(to_root_path("run/ssh/external-ssh"), suffix=".pid")
		delete(to_root_path("run/ssh/internal-ssh"), suffix=".pid")


	#######################
	#	 START TUNNELS	  #
	#######################

	# Start tunnels for cowrie traffic
	def start_ssh(self):
		for honeypot in self.server.run_config["honeypots"]:
			# Tunnel controller -> device
			self.start_tunnel(
				socket_dir    = to_root_path("run/ssh/internal-ssh/"),
				bind_addr     = "127.0.0.1",
				bind_port     = TunnelsController.TUNNEL_PORTS+honeypot["id"],
				dst_addr      = honeypot["device"]["ip"],
				dst_port      = 22,
				remote_ip     = "10.0.0.2",
				key_path      = TunnelsController.VM_PRIV_KEY,
				remote_origin = False
			)
			# Tunnel door -> controller
			self.start_tunnel(
				socket_dir    = to_root_path("run/ssh/external-ssh/"),
				bind_addr     = "127.0.0.1",
				bind_port     = TunnelsController.TUNNEL_PORTS,
				dst_addr      = "127.0.0.1",
				dst_port      = TunnelsController.TUNNEL_PORTS+honeypot["id"],
				remote_ip     = honeypot["door"]["host"],
				key_path      = TunnelsController.DOOR_PRIV_KEY,
				remote_origin = True
			)

	# Start tunnels for other exposed ports
	def start_other(self):
		for honeypot in self.server.run_config["honeypots"]:
			if len(honeypot["ports"]) > TunnelsController.PORTS_LIMIT:
				log(ERROR, "We only accept "+str(TunnelsController.PORTS_LIMIT)
					+" exposed ports per honeypot - honeypot "+honeypot["id"]
					+"does not meet this requirement")
				continue
			cpt = 0
			for port in honeypot["ports"]:
				# Controller --> Device
				self.start_tunnel(
					socket_dir    = to_root_path("run/ssh/internal-others/"),
					bind_addr     = "127.0.0.1",
					bind_port     = TunnelsController.EXPOSE_PORTS+(honeypot["id"]*TunnelsController.PORTS_LIMIT)+cpt,
					dst_addr      = honeypot["device"]["ip"],
					dst_port      = port,
					remote_ip     = "10.0.0.2",
					key_path      = TunnelsController.VM_PRIV_KEY,
					remote_origin = False
				)
				# Door --> Controller
				self.start_tunnel(
					socket_dir    = to_root_path("run/ssh/external-others/"),
					bind_addr     = "0.0.0.0",
					bind_port     = port,
					dst_addr      = "127.0.0.1",
					dst_port      = TunnelsController.EXPOSE_PORTS+(honeypot["id"]*TunnelsController.PORTS_LIMIT)+cpt,
					remote_ip     = honeypot["door"]["host"],
					key_path      = TunnelsController.DOOR_PRIV_KEY,
					remote_origin = True
				)
				cpt += 1


	#######################
	#     STOP TUNNELS    #
	#######################

	# For additional ports (not ssh)
	def stop_other(self):
		self.stop_tunnels("external-others")
		self.stop_tunnels("internal-others")

	def stop_ssh(self):
		self.stop_tunnels("external-ssh")
		self.stop_tunnels("internal-ssh")

	def stop(self):
		self.stop_other()
		self.stop_ssh()


	#######################
	#   START UTILITIES   #
	#######################

	def gen_sock_filename(self, socketdir):
		# Warning: using a __deprecated__ function
		# May need to be changed, but I think the ssh
		# command expects that the file does not exist
		socketfile = tempfile.mktemp(".sock", "", dir=socketdir)
		try:
			os.remove(socketfile)
		except OSError:
			pass
		return socketfile

	def start_tunnel(self, socket_dir, bind_addr, bind_port, dst_addr, dst_port, remote_ip, key_path, remote_origin=True):
		origin = "-R" if remote_origin else "-L"
		socket = self.gen_sock_filename(socketdir)

		tunnel_template = Template("ssh -f -N -M -S ${socket} \
			${origin} ${bind_addr}:${bind_port}:${dst_addr}:${dst_port} \
			root@${remote_ip} \
			-i ${key_path}")

		tunnel_command = tunnel_template.substitute({
			"socket"    : socket,
			"origin"    : origin,
			"bind_addr" : bind_addr,
			"bind_port" : bind_port,
			"dst_addr"  : dst_addr,
			"dst_port"  : dst_port,
			"remote_ip" : remote_ip,
			"key_path"  : key_path
		})

		if not run(tunnel_command):
			log(ERROR, "failed to create a tunnel")


	#######################
	#   STOP UTILITIES    #
	#######################

	def stop_tunnels(self, directory):
		path = to_root_path("run/ssh/"+directory)
		for killpath in os.listdir(path):
			if killpath.endswith(".sock"):
				try:
					kill_from_file(os.path.join(path, killpath), filetype="ssh")
				except:
					log(WARNING, "Failed to close a SSH tunnel. The control socket is: "+str(killpath))