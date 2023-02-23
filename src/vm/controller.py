# External
import os, sys

# Internal
sys.path.insert(0, os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/"))
from vm.proto import *
from vm.sock import VMSocket

class VMController:
	def __init__(self):
		self.socket = VMSocket()

	def __del__(self):
		del self.socket

	def connect(self):
		self.socket.connect()

	# CMD_VM_LIVE
	def connected(self):
		if self.socket.connected():
			self.socket.send_cmd(CMD_VM_LIVE)
			return self.socket.wait_confirm()
		else:
			return False

	# CMD_VM_PHASE
	def send_phase(self, phase):
		self.socket.send_cmd(CMD_VM_PHASE)
		self.socket.send_obj(phase)
		return self.socket.wait_confirm()

	def send_devices(self, devs):
		for dev in devs:
			if not self.send_device(dev):
				return False

	# CMD_VM_WALT_ADD_DEV
	def send_device(self, dev):
		self.socket.send_cmd(CMD_VM_WALT_ADD_DEV)
		self.socket.send_obj(dev)
		return self.socket.wait_confirm()

	# CMD_VM_WALT_DEV_IP
	def get_ips(self):
		self.socket.send_cmd(CMD_VM_WALT_DEV_IP)
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

	# CMD_VM_WG_DEL_CONF
	def wg_del_conf(self):
		self.socket.send_cmd(CMD_VM_WG_DEL_CONF)
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
