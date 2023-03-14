# External
import os, socket, sys, threading, time

# Internal
from common.utils.controller import Controller
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
from common.vm.proto import *
from common.utils.sockets import ServerSocket

class VMController(Controller):
	def __init__(self):
		log(INFO, "VMController.__init__: creating the VMController")
		self.socket = ServerSocket(CONTROL_PORT, addr=socket.VMADDR_CID_HOST, socktype=socket.AF_VSOCK)
		self.phase = None

	def __del__(self):
		del self.socket


	#############################
	#	 LOCAL VM MANAGEMENT	#
	#############################


	def pid(self):
		return read_pid_file(to_root_path("run/vm.pid"))

	def start(self, phase):
		self.phase = phase
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
		# Starting the VM
		if not run(vm_cmd):
			log(ERROR, self.name()+".start: failed to start the VM")
		# Waiting for the VM to connect
		if not self.connect():
			log(ERROR, self.name()+".start: failed to accept the VM connection")

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

	# Bind the socket and accept a new connection
	#	retry: number of times we will try to bind the socket (if the VM takes time to boot, the bind operation will fail)
	#	sleep: duration (in seconds) to sleep before we retry to bind
	def connect(self, retry=3, sleep=3):
		retries = 0
		while retries <= retry:
			if not self.socket.bind(): # Failed to bind
				time.sleep(sleep)
			else: # Successful bind
				break
			retries += 1
		if retries>retry:
			log(DEBUG, self.name()+".connect: failed to bind socket, VM probably failed to boot")
			return False
		return self.socket.accept(timeout=240)

	# Run a complete "command (+subcommands) - data - answer" exchange on a TCLIENT+HCLIENT socket
	def exchange(self, commands=[], data=None, timeout=30, retry=1):
		res = None
		trials = 0
		reconnect = False
		while trials <= retry:
			trials += 1
			if reconnect:
				self.socket.close()
				if not self.connect(): return None
				reconnect = False
			for cmd in commands:
				if self.socket.send_cmd(cmd) == 0:
					reconnect = True
					break
			else:
				if data is not None and self.socket.send_obj(data) <= 0:
					reconnect = True
					continue
				res = self.socket.get_answer(timeout=timeout)
				if res is None: reconnect = True
				else: break
		return res


	#############################
	# COMMUNICATION WITH THE VM #
	#############################

	# CMD_VM_LIVE
	def connected(self):
		if self.socket.connected():
			return self.exchange(commands=[CMD_VM_LIVE])
		else:
			return False

	# CMD_VM_PHASE
	def send_phase(self, phase=None):
		phase = self.phase if phase is None else phase
		return self.exchange(commands=[CMD_VM_PHASE], data=phase)

	# CMD_VM_WALT_DEVS
	def send_devices(self, devs):
		return self.exchange(commands=[CMD_VM_WALT_DEVS], data=devs)

	# CMD_VM_WALT_IPS
	def get_ips(self):
		return self.exchange(commands=[CMD_VM_WALT_IPS])

	# CMD_VM_WG_KEYGEN
	def wg_keygen(self):
		return self.exchange(commands=[CMD_VM_WG_KEYGEN])

	# CMD_VM_WG_DOORS
	def send_doors(self, doors):
		return self.exchange(commands=[CMD_VM_WG_DOORS], data=doors)

	# CMD_VM_WG_UP
	def wg_up(self):
		return self.exchange(commands=[CMD_VM_WG_UP])

	# CMD_VM_WG_DOWN
	def wg_down(self):
		return self.exchange(commands=[CMD_VM_WG_DOWN])

	# CMD_VM_COMMIT
	def commit(self):
		return self.exchange(commands=[CMD_VM_COMMIT])

	# CMD_VM_SHUTDOWN
	def soft_shutdown(self):
		log(INFO, "starting vm soft shutdown")
		return self.exchange(commands=[CMD_VM_SHUTDOWN], timeout=10)

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