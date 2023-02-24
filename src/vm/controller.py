# External
import os, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from utils.files import *
from vm.proto import *
from vm.sock import VMSocket

class VMController:
	def __init__(self):
		self.socket = VMSocket()
		self.phase = None
		self.ips = None

	def __del__(self):
		del self.socket


	#############################
	#	 LOCAL VM MANAGEMENT	#
	#############################


	def pid(self):
		return read_pid_file(to_root_path("run/vm.pid"))

	def start(self, phase):
		# Starting the VM
		with open(to_root_path("var/template/vm_phase"+str(phase)+".txt"), "r") as temp_file: template = Template(temp_file.read())
		vm_cmd = template.substitute({
			"pidfile": to_root_path("run/vm.pid"),
			"diskfile": "/persist/disk.dd",
			"swapfile": "/persist/swap.dd",
			"wimgfile": "/persist/wimg.dd",
			"tapout_up": to_root_path("src/script/tapout-up.sh"),
			"tapout_down": to_root_path("src/script/tapout-down.sh")
		})
		run(vm_cmd, "failed to start the VM")

	def stop(self):
		self.phase = None

	def connect(self):
		self.socket.connect()


	#############################
	# COMMUNICATION WITH THE VM #
	#############################


	def initiate(self):
		else:
			# RUN PHASE
			self.ips = self.get_ips() # IPs needed for tunnels (Cowrie <-> Device)
			self.wg_up()

	# CMD_VM_LIVE
	def connected(self):
		if self.socket.connected():
			self.socket.send_cmd(CMD_VM_LIVE)
			return self.socket.wait_confirm()
		else:
			return False

	# CMD_VM_PHASE
	def send_phase(self):
		self.socket.send_cmd(CMD_VM_PHASE)
		self.socket.send_obj(self.phase)
		return self.socket.wait_confirm()

	# CMD_VM_WALT_DEVS
	def send_devices(self, devs):
		self.socket.send_cmd(CMD_VM_WALT_DEVS)
		self.socket.send_obj(devs)
		return self.socket.wait_confirm()

	# CMD_VM_WALT_IPS
	def get_ips(self):
		self.socket.send_cmd(CMD_VM_WALT_IPS)
		ips = self.socket.recv_obj()
		if str(ips) == "0": # Failed
			return False
		else:
			return ips

	# CMD_VM_WG_KEYGEN
	def wg_keygen(self):
		self.socket.send_cmd(CMD_VM_WG_KEYGEN)
		keys = self.socket.recv_obj()
		if str(keys) == "0":
			# Failed
			return False
		else:
			return keys

	# CMD_VM_WG_DOORS
	def send_doors(self, doors):
		self.socket.send_cmd(CMD_VM_WG_DOORS)
		self.socket.send_obj(doors)
		return self.socket.wait_confirm()

	# CMD_VM_WG_UP
	def wg_up(self):
		self.socket.send_cmd(CMD_VM_WG_UP)
		return self.socket.wait_confirm()

	# CMD_VM_WG_DOWN
	def wg_down(self):
		self.socket.send_cmd(CMD_VM_WG_DOWN)
		return self.socket.wait_confirm()

	# CMD_VM_COMMIT
	def commit(self):
		self.socket.send_cmd(CMD_VM_COMMIT)
		return self.socket.wait_confirm()

	# CMD_VM_SHUTDOWN
	def shutdown(self):
		self.socket.send_cmd(CMD_VM_SHUTDOWN)
		return self.socket.wait_confirm()
