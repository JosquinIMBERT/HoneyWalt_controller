# External
import os, sys

# Internal
from common.utils.controller import Controller
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
from common.vm.proto import *
from vm.sock import VMSocket

class VMController(Controller):
	def __init__(self):
		log(INFO, "VMController.__init__: creating the VMController")
		self.socket = VMSocket()
		self.phase = None

	def __del__(self):
		del self.socket


	#############################
	#	 LOCAL VM MANAGEMENT	#
	#############################


	def pid(self):
		return read_pid_file(to_root_path("run/vm.pid"))

	def start(self, phase):
		# Starting the VM
		with open(to_root_path("var/template/vm_phase"+str(phase)+".txt"), "r") as temp_file:
			template = Template(temp_file.read())
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

		# Schedule hard shutdown in case of fail of soft shutdown
		timer = threading.Timer(10, self.hard_shutdown)
		timer.start()

		# Trying soft shutdown (run shutdown command)
		self.soft_shutdown()

		# Cancel hard shutdown if soft shutdown was successful
		if not self.pid():
			timer.cancel()

	def connect(self):
		self.socket.connect()


	#############################
	# COMMUNICATION WITH THE VM #
	#############################

	# CMD_VM_LIVE
	def connected(self):
		if self.socket.connected():
			self.socket.send_cmd(CMD_VM_LIVE)
			return self.socket.get_answer()
		else:
			return False

	# CMD_VM_PHASE
	def send_phase(self):
		self.socket.send_cmd(CMD_VM_PHASE)
		self.socket.send_obj(self.phase)
		return self.socket.get_answer()

	# CMD_VM_WALT_DEVS
	def send_devices(self, devs):
		self.socket.send_cmd(CMD_VM_WALT_DEVS)
		self.socket.send_obj(devs)
		return self.socket.get_answer()

	# CMD_VM_WALT_IPS
	def get_ips(self):
		self.socket.send_cmd(CMD_VM_WALT_IPS)
		ips = self.socket.recv_obj()
		if str(ips) == "0" or str(ips) == "": # Failed
			return None
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
		return self.socket.get_answer()

	# CMD_VM_WG_UP
	def wg_up(self):
		self.socket.send_cmd(CMD_VM_WG_UP)
		res = self.socket.get_answer()
		return res["success"]

	# CMD_VM_WG_DOWN
	def wg_down(self):
		self.socket.send_cmd(CMD_VM_WG_DOWN)
		return self.socket.get_answer()

	# CMD_VM_COMMIT
	def commit(self):
		self.socket.send_cmd(CMD_VM_COMMIT)
		return self.socket.get_answer()

	# CMD_VM_SHUTDOWN
	def soft_shutdown(self):
		log(INFO, "starting vm soft shutdown")
		self.socket.send_cmd(CMD_VM_SHUTDOWN)
		return self.socket.get_answer(timeout=10)

	def hard_shutdown(self):
		log(INFO, "starting vm hard shutdown")
		path = to_root_path("run/vm.pid")
		if exists(path):
			try:
				kill_from_file(path)
				return
			except:
				pass
		log(WARNING, "Failed to stop the VM (pidfile:"+str(path)+").")