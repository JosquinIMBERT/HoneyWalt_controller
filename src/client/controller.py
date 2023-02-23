# External
import os, sys

# Internal
sys.path.insert(0, os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/"))
from client.proto import *
from client.sock import ClientSocket

class ClientController:
	def __init__(self):
		self.socket = ClientSocket()

	def __del__(self):
		del self.socket

	def connect(self):
		self.socket.connect()

	# CMD_CLI_LIVE
	def connected(self):
		if self.socket.connected():
			self.socket.send_cmd(CMD_CLIENT_LIVE)
			return self.socket.wait_confirm()
		else:
			return False

	# CMD_CLI_TODO
	def todo(self):
		self.socket.send_cmd(CMD_CLI_TODO)
		self.socket.send_obj(todo())
		return self.socket.wait_confirm()