# External
import os, pickle, socket, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from utils.logs import *

# CONSTANTS
global OBJECT_SIZE, COMMAND_SIZE
OBJECT_SIZE = 4 # Objects size encoded on 4 bytes
COMMAND_SIZE = 1 # Commands encoded on 1 bytes

class ProtoSocket:
	def __init__(self):
		self.socket = None

	# Get the class name to generate logs (this class is abstract for Door and VM sockets)
	def name(self):
		return self.__class__.__name__

	def connected(self):
		return self.socket is not None

	# Send an object (object size on OBJECT_SIZE bytes followed by the object on the corresponding amount of bytes)
	def send_obj(self, obj):
		if not self.connected():
			log(ERROR, self.name()+".send_obj: Failed to send an object. The socket is not connected")
		else:
			self.socket.send(serialize(obj))

	# Receive an object (object size on OBJECT_SIZE bytes followed by the object on the corresponding amount of bytes)
	def recv_obj(self):
		bytlen = self.recv(size=OBJECT_SIZE)
		if bytlen is not None:
			bytobj = self.recv(size=from_bytes(bytlen, 'big'))
			if bytobj is not None:
				return deserialize(bytobj)
		return None

	# Send a command (should be on COMMAND_SIZE bytes)
	def send_cmd(self, cmd):
		if not self.connected():
			log(ERROR, self.name()+".send_cmd: Failed to send a command. The socket is not connected")
		else:
			self.socket.send(cmd_to_bytes(cmd))

	# Send a command (should be on COMMAND_SIZE bytes)
	def recv_cmd(self):
		if not self.connected():
			log(ERROR, self.name()+".recv_cmd: Failed to send a command. The socket is not connected")
			return None
		else:
			return bytes_to_cmd(self.socket.recv(COMMAND_SIZE))

	# Send one byte to 1
	def send_confirm(self):
		self.send(to_nb_bytes(1, 1))

	# Send one byte to 0
	def send_fail(self, msg=""):
		self.send(to_nb_bytes(0, 1))
		self.send_obj(msg)

	# Wait for one byte, return True if the byte is 1
	def wait_confirm(self, timeout=30):
		res = self.recv(size=1, timeout=timeout)
		return res == to_nb_bytes(1, 1)

	# Send data to the socket
	def send(self, bytes_msg):
		self.socket.send(bytes_msg)

	# Receive data on socket, with a timeout
	def recv(self, size=2048, timeout=30):
		self.socket.settimeout(timeout)
		try:
			res = self.socket.recv(size)
		except socket.timeout:
			log(WARNING, self.name()+".recv: reached timeout")
			return None
		except:
			eprint(self.name()+".recv: an unknown error occured")
		else:
			if not res:
				log(WARNING, self.name()+".recv: Connection terminated")
				return None
			return res


def serialize(obj):
	serial = pickle.dumps(obj)
	length = len(serial)
	bytlen = to_nb_bytes(length, OBJECT_SIZE)
	return bytlen+serial

def deserialize(strg):
	return pickle.loads(strg)

def cmd_to_bytes(cmd):
	return cmd.to_bytes(COMMAND_SIZE, 'big')

def bytes_to_cmd(byt):
	return int.from_bytes(byt, 'big')

def to_nb_bytes(integer, nb):
	try:
		byt = integer.to_bytes(nb, 'big')
	except OverflowError:
		log(ERROR, "utils.sockets.to_nb_bytes: the object is too big")
		return bytes(0)
	return byt