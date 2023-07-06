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
	def __init__(self, server):
		Controller.__init__(self)
		self.server = server
		self.socket = ServerSocket(CONTROL_PORT, addr=socket.VMADDR_CID_HOST, socktype=socket.AF_VSOCK, reusable = True)
		self.socket.set_name("Socket(Controller-VM)")
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
			log(ERROR, self.get_name()+".start: failed to start the VM")
		# Waiting for the VM to connect
		if not self.connect():
			log(ERROR, self.get_name()+".start: failed to accept the VM connection")

	def stop(self):
		self.phase = None

		# Don't try to stop if it is already stopped
		if not self.pid():
			return None

		# Schedule hard shutdown in case of fail of soft shutdown
		timer = threading.Timer(20, self.hard_shutdown)
		timer.start()

		# Trying soft shutdown (run shutdown command)
		self.soft_shutdown()

		# We wait at most 20 seconds, actively trying to know if the VM is still alive
		max_wait = 20
		one_wait = 0.5
		waited = 0
		while self.pid() and waited < max_wait:
			time.sleep(one_wait)
			waited += one_wait

		# Cancel hard shutdown if soft shutdown was successful
		if not self.pid():
			timer.cancel()
			self.socket.reinit()
		else:
			timer.join()

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
			log(DEBUG, self.get_name()+".connect: failed to bind socket, VM probably failed to boot")
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

	def connected(self):
		if self.socket.connected():
			return self.exchange(commands=[CMD_VM_LIVE])
		else:
			return False

	def send_phase(self, phase=None):
		phase = self.phase if phase is None else phase
		return self.exchange(commands=[CMD_VM_PHASE], data=phase)

	def send_honeypots(self, honeypots):
		return self.exchange(commands=[CMD_VM_HONEYPOTS], data=honeypots, timeout=600) # We wait 10min

	def get_ips(self):
		return self.exchange(commands=[CMD_VM_IPS])

	def wg_keygen(self):
		return self.exchange(commands=[CMD_VM_WG_KEYGEN])

	def wg_up(self):
		return self.exchange(commands=[CMD_VM_WG_UP])

	def wg_down(self):
		return self.exchange(commands=[CMD_VM_WG_DOWN])

	def firewall_up(self):
		return self.exchange(commands=[CMD_VM_FW_UP])

	def firewall_down(self):
		return self.exchange(commands=[CMD_VM_FW_DOWN])

	def commit(self):
		return self.exchange(commands=[CMD_VM_COMMIT])

	def soft_shutdown(self):
		log(INFO, "starting vm soft shutdown")
		return self.exchange(commands=[CMD_VM_SHUTDOWN], timeout=10)

	def hard_shutdown(self):
		self.socket.reinit()

		# Killing the process if the PID is still matching a running process
		path = to_root_path("run/vm.pid")
		if self.pid() is not None:
			log(INFO, "starting vm hard shutdown")

			# Trying to run "shutdown now" through ssh
			run("ssh -o ConnectTimeout=5 root@10.0.0.2 -i "+to_root_path("var/key/id_olim")+" -p 22 \"shutdown now\"")

			# Giving 5 seconds for qemu process to shutdown with the VM
			time.sleep(5)

			try:
				if self.pid() is not None: kill_from_file(path)
			except:
				log(WARNING, "Failed to stop the VM (pidfile:"+str(path)+").")
