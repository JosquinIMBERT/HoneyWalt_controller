# External
import os, sys

# Internal
from common.client.proto import *
from client.sock import ClientSocket
import commands
from common.utils.controller import Controller

class ClientController(Controller):
	def __init__(self):
		self.socket = ClientSocket()
		self.keep_running = False

	def __del__(self):
		del self.socket

	def start(self):
		self.socket.start()

	def run(self):
		self.keep_running = True
		while self.keep_running:
			self.socket.accept()
			while self.keep_running:
				cmd = self.socket.recv_cmd()
				self.execute(cmd)

	def execute(self, cmd):
		if cmd == CMD_CLIENT_DOOR:
			self.door_execute()
		elif cmd == CMD_CLIENT_CTRL:
			self.ctrl_execute()
		elif cmd == CMD_CLIENT_DEV:
			self.dev_execute()
		elif cmd == CMD_CLIENT_IMG:
			self.img_execute()
		elif cmd == CMD_CLIENT_VM:
			self.vm_execute()
		elif cmd == CMD_CLIENT_START:
			self.exec(commands.state.start)
		elif cmd == CMD_CLIENT_COMMIT:
			options = self.socket.recv_obj()
			self.exec(commands.state.commit, regen=options["regen"])
		elif cmd == CMD_CLIENT_STOP:
			self.exec(commands.state.stop)
		elif cmd == CMD_CLIENT_RESTART:
			options = self.socket.recv_obj()
			self.exec(commands.state.restart, regen=options["regen"])
		elif cmd == CMD_CLIENT_STATUS:
			self.exec(commands.state.status)
		else:
			self.socket.send_fail(msg="Unknown command")

	def door_execute(self):
		cmd = self.socket.recv_cmd()
		if cmd == CMD_CLIENT_DOOR_ADD:
			options = self.socket.recv_obj()
			self.exec(commands.door.add, options["ip"], options["dev"])
		elif cmd == CMD_CLIENT_DOOR_CHG:
			options = self.socket.recv_obj()
			self.exec(commands.door.chg, options["ip"], new_ip=options["new_ip"], new_dev=options["new_dev"])
		elif cmd == CMD_CLIENT_DOOR_DEL:
			options = self.socket.recv_obj()
			self.exec(commands.door.delete, options["ip"])
		elif cmd == CMD_CLIENT_DOOR_SHOW:
			self.exec(commands.door.show)
		else:
			self.socket.send_fail(msg="Unknown command")

	def ctrl_execute(self):
		cmd = socket.recv_cmd()
		if cmd == CMD_CLIENT_CTRL_SET:
			options = self.socket.recv_obj()
			self.exec(commands.controller.set, throughput=options["throughput"], latency=options["latency"])
		elif cmd == CMD_CLIENT_CTRL_SHOW:
			self.exec(commands.controller.show)
		else:
			self.socket.send_fail(msg="Unknown command")

	def dev_execute(self):
		cmd = socket.recv_cmd()
		if cmd == CMD_CLIENT_DEV_ADD:
			options = self.socket.recv_obj()
			self.exec(commands.device.add, options["name"], options["mac"], options["image"], options["ports"])
		elif cmd == CMD_CLIENT_DEV_CHG:
			options = self.socket.recv_obj()
			self.exec(commands.device.chg, options["name"], new_name=options["new_name"], new_image=options["new_image"], new_ports=options["new_ports"])
		elif cmd == CMD_CLIENT_DEV_DEL:
			options = self.socket.recv_obj()
			self.exec(commands.device.delete, options["name"])
		elif cmd == CMD_CLIENT_DEV_SHOW:
			self.exec(commands.device.show)
		else:
			self.socket.send_fail(msg="Unknown command")

	def img_execute(self):
		cmd = socket.recv_cmd()
		if cmd == CMD_CLIENT_IMG_ADD:
			options = self.socket.recv_obj()
			self.exec(commands.image.add, options["name"], options["username"], options["password"])
		elif cmd == CMD_CLIENT_IMG_CHG:
			options = self.socket.recv_obj()
			self.exec(commands.image.chg, options["name"], username=options["username"], password=options["password"])
		elif cmd == CMD_CLIENT_IMG_DEL:
			options = self.socket.recv_obj()
			self.exec(commands.image.delete, options["name"])
		elif cmd == CMD_CLIENT_IMG_SHOW:
			self.exec(commands.image.show)
		else:
			self.socket.send_fail(msg="Unknown command")

	def vm_execute(self):
		cmd = socket.recv_cmd()
		if cmd == CMD_CLIENT_VM_SHELL:
			self.socket.send_fail(msg="VM SHELL is not implemented yet")
		elif cmd == CMD_CLIENT_VM_START:
			options = self.socket.recv_obj()
			self.exec(commands.vm.start, options["phase"])
		elif cmd == CMD_CLIENT_VM_STOP:
			self.exec(commands.vm.stop)
		else:
			self.socket.send_fail(msg="Unknown command")

	def stop(self):
		self.keep_running = False