# External
import socket, time

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from utils.logs import *
from utils.sockets import *
from client.proto import *

class ClientSocket(ProtoSocket):
	def __init__(self):
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket = None

	def __del__(self):
		if self.socket is not None:
			self.socket.close()
		if self.listen_socket is not None:
			self.listen_socket.close()

	def connect(self):
		try:
			self.listen_socket.bind(("", CLIENT_PORT))
		except:
			log(ERROR, "ClientSocket.connect: failed to bind socket")
			return False
		self.listen_socket.listen(1)
		return True

	def accept(self):
		try:
			self.socket, addr = self.listen_socket.accept()
		except:
			eprint("ClientSocket.run: an error occured when waiting for client connection")