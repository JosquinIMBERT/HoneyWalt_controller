# External
import os, re, sys, time

# Internal
from common.utils.logs import *
from common.utils.rpc import FakeClient

class VMManager:

	VM_IP = "10.0.0.2"

	def __init__(self, server):
		self.server = server

	def __del__(self):
		pass

	def shell(self, client=FakeClient()):
		if not self.server.vm.pid():
			client.log(ERROR, "the VM seems to be stopped")
			return None
		else:
			res = {}
			if self.server.vm.phase != 1:
				client.log(WARNING, "the VM is in run mode. Your modifications will be lost after reboot and an attacker could infect the VM")
			res["ip"] = VMManager.VM_IP
			with open(to_root_path("var/key/id_olim"), "r") as keyfile:
				res["key"] = keyfile.read()
			return res

	def start(self, phase, client=FakeClient()):
		if self.server.vm.pid() is not None:
			client.log(ERROR, "the VM is already running")
			return None
		self.server.vm.start(phase)

		return True

	def stop(self, client=FakeClient()):
		if self.server.vm.pid() is None:
			client.log(ERROR, "the VM is already stopped")
			return None
		self.server.vm.stop()

		return True