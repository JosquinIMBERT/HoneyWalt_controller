# External
import os, socket, sys, time

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from utils.logs import *
from utils.sockets import ProtoSocket

class DoorSocket(ProtoSocket):
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def __del__(self):
		if self.socket is not None:
			self.socket.close()

	def connect(self, ip, port):
		try:
			self.socket.connect((ip, port))
		except:
			log(ERROR, "DoorSocket.connect: failed to connect to the door")
			return False
		else:
			return True