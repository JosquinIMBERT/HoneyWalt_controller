# External
import socket, time

# Internal
sys.path.insert(0, os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/"))
from utils.logs import *
from utils.sockets import *
from vm.proto import *

class VMSocket(ProtoSocket):
	def __init__(self):
		self.listen_socket = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
		self.socket = None

	def __del__(self):
		if self.socket is not None:
			self.socket.close()
		if self.listen_socket is not None:
			self.listen_socket.close()

	# Connect:
	#	1 - Bind the socket (the VM needs to be booted)
	#	2 - Start listening
	#	3 - Accept a connection (the VM needs to run the honeywalt_vm daemon and to connect to the socket)
	def connect(self):
		i = 0
		while i<15:
			i+=1
			try: self.listen_socket.bind((socket.VMADDR_CID_HOST, CONTROL_PORT))
			except:
				time.sleep(1)
			else:
				break
		if i>=15:
			log(ERROR, "VMSocket.connect: failed to bind socket, VM probably failed to boot")
			return False
		self.listen_socket.settimeout(240) # Timeout for VM connection is 4min
		self.listen_socket.listen(1)
		try:
			self.socket, addr = self.listen_socket.accept()
		except socket.timeout:
			log(ERROR, "VMSocket.connect: it seems like the VM failed to connect to the socket")
			return False
		except:
			eprint("VMSocket.initiate: unknown error occured when waiting for the VM")
		else:
			return True