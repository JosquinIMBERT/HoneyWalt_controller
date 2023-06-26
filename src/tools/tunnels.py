# External
from sshtunnel import SSHTunnelForwarder
from string import Template
import tempfile

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.misc import *
import common.utils.settings as settings
from common.utils.system import *

class TunnelsController:

	VM_PRIV_KEY   = to_root_path("var/key/id_olim")
	VM_PUB_KEY    = to_root_path("var/key/id_olim.pub")
	DOOR_PRIV_KEY = to_root_path("var/key/id_door")
	DOOR_PUB_KEY  = to_root_path("var/key/id_door.pub")

	def __init__(self, server):
		log(INFO, "TunnelsController.__init__: creating the TunnelsController")
		self.server = server

	def __del__(self):
		pass

	def init_run(self):
		delete(to_root_path("run/ssh/cowrie-dmz"), suffix=".pid")
		delete(to_root_path("run/ssh/cowrie-out"), suffix=".pid")


	#######################
	#	 START TUNNELS	  #
	#######################

	def start_cowrie_dmz(self):
		BACKEND_PORTS = settings.get("BACKEND_PORTS")

		for honeypot in self.server.run_config["honeypots"]:
			self.start_tunnel_controller_dmz(
				to_root_path("run/ssh/cowrie-dmz/"),
				BACKEND_PORTS+honeypot["id"],
				honeypot["device"]["ip"],
				22
			)

	def start_door_cowrie(self):
		LISTEN_PORTS = settings.get("LISTEN_PORTS")

		for honeypot in self.server.run_config["honeypots"]:
			self.start_tunnel_door_controller(
				to_root_path("run/ssh/cowrie-out/"),
				22,
				LISTEN_PORTS+honeypot["id"],
				honeypot["door"]["host"]
			)

	# For additional ports (not ssh)
	def start_expose_ports(self):
		EXPOSE_PORTS = settings.get("EXPOSE_PORTS")

		for honeypot in self.server.run_config["honeypots"]:
			for port in honeypot["ports"]:
				# Controller --> Device
				self.start_tunnel_controller_dmz(
					to_root_path("run/ssh/expose-dmz/"),
					EXPOSE_PORTS+honeypot["id"],
					honeypot["device"]["ip"],
					port
				)
				# Door --> Controller
				self.start_tunnel_door_controller(
					to_root_path("run/ssh/expose-out/"),
					port,
					EXPOSE_PORTS+honeypot["id"],
					honeypot["door"]["host"]
				)


	#######################
	#     STOP TUNNELS    #
	#######################

	# For additional ports (not ssh)
	def stop_expose_ports(self):
		for directory in ["expose-out", "expose-dmz"]:
			self.stop_tunnels(directory)

	def stop_cowrie_tunnels_out(self):
		self.stop_tunnels("cowrie-out")

	def stop_cowrie_tunnels_dmz(self):
		self.stop_tunnels("cowrie-dmz")

	def stop(self):
		self.stop_expose_ports()
		self.stop_cowrie_tunnels_out()
		self.stop_cowrie_tunnels_dmz()


	#######################
	#   START UTILITIES   #
	#######################

	def gen_sock_filename(self, socketdir):
		# Warning: using a __deprecated__ function
		# May need to be changed, but I think the ssh
		# command expects that the file doesn't exist
		socketfile = tempfile.mktemp(".sock", "", dir=socketdir)
		try:
			os.remove(socketfile)
		except OSError:
			pass
		return socketfile

	def start_tunnel_door_controller(self, socketdir, door_port, local_port, door):
		# TODO: use sshtunnels library
		toDoor_template = Template("ssh -f -N -M -S ${socket} \
			-R *:${door_port}:127.0.0.1:${local_port} \
			-i ${key_path} \
			root@${host} \
			-p ${realssh_port}")

		tunnel_cmd = toDoor_template.substitute({
			"socket": self.gen_sock_filename(socketdir),
			"door_port": door_port,
			"local_port": local_port,
			"key_path": TunnelsController.DOOR_PRIV_KEY,
			"host": door["host"],
			"realssh_port": door["realssh"]
		})
		if not run(tunnel_cmd):
			log(ERROR, "TunnelsController.start_tunnel_door_controller: failed to start tunnel between door and controller")

	def start_tunnel_controller_dmz(self, socketdir, local_port, dev_ip, dev_port):
		# TODO: use sshtunnels library
		VM_IP = settings.get("VM_IP")

		toDMZ_template = Template("ssh -f -N -M -S ${socket} \
			-L ${local_port}:${ip}:${dev_port} \
			root@${vm_ip} \
			-i ${key_path}")

		tunnel_cmd = toDMZ_template.substitute({
			"socket": self.gen_sock_filename(socketdir),
			"local_port": local_port,
			"ip": dev_ip,
			"dev_port": dev_port,
			"vm_ip": VM_IP,
			"key_path": TunnelsController.VM_PRIV_KEY
		})
		if not run(tunnel_cmd):
			log(ERROR, "TunnelsController.start_tunnel_controller_dmz: failed to start tunnel between controller and dmz")


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