# External
import json, os, rpyc, ssl, sys
from rpyc.utils.server import ThreadedServer
from rpyc.utils.authenticators import SSLAuthenticator

# Internal
import commands.controller
import commands.device
import commands.door
import commands.image
import commands.state
import commands.vm
from common.client.proto import *
from common.utils.files import *
from common.utils.controller import Controller
from common.utils.logs import *

class ClientController(Controller):
	def __init__(self):
		Controller.__init__(self)
		log(INFO, "Creating the ClientController")

	def __del__(self):
		log(INFO, "Deleting the ClientController")

	def start(self):
		authenticator = SSLAuthenticator(
			to_root_path("var/key/pki/private/controller-server.key"),
			to_root_path("var/key/pki/controller-server.crt"),
			ca_certs=to_root_path("var/key/pki/ca.crt"),
			cert_reqs=ssl.CERT_REQUIRED,
			ssl_version=ssl.PROTOCOL_TLS
		)
		self.service_thread = ThreadedServer(ClientService, port=CLIENT_PORT, authenticator=authenticator)
		self.service_thread.start()

	def stop(self):
		self.service_thread.close()

class ClientService(rpyc.Service):
	def __init__(self):
		self.remote_stdout = None
		self.remote_stderr = None
		self.loglevel = INFO
		self.conn = None
		self.remote_ip = None

	def __del__(self):
		del self.remote_stdout
		del self.remote_stderr
		del self.loglevel
		del self.conn
		del self.remote_ip

	def on_connect(self, conn):
		self.conn = conn
		self.remote_ip = conn.root.get_ip()
		log(INFO, self.__class__.__name__+": New connection from", self.remote_ip)

	def on_disconnect(self, conn):
		log(INFO, self.__class__.__name__+": End of connection with", self.remote_ip)

	def exposed_set_stdout(self, stdout):
		# TODO: verify what the client is giving as argument
		self.remote_stdout = stdout

	def exposed_set_stderr(self, stderr):
		# TODO: verify what the client is giving as argument
		self.remote_stderr = stderr

	def exposed_set_log_level(self, loglevel):
		if loglevel not in [COMMAND, DEBUG, INFO, WARNING, ERROR, FATAL]:
			self.log(ERROR, "invalid loglevel")
		else:
			self.loglevel = loglevel

	def log(self, level, *args, **kwargs):
		if self.remote_stdout is not None and self.remote_stderr is not None:
			log_remote(level, self.loglevel, self.remote_stdout, self.remote_stderr, *args, **kwargs)

	def call(self, func, *args, **kwargs):
		return json.dumps(func(self, *args, **kwargs))



	##################
	#      STATE     #
	##################
	
	def exposed_start(self):
		return self.call(commands.state.start)

	def exposed_commit(self, regen=True):
		return self.call(commands.state.commit, regen=regen)

	def exposed_stop(self):
		return self.call(commands.state.stop)

	def exposed_restart(self, regen=False):
		return self.call(commands.state.restart, regen=regen)

	def exposed_status(self):
		return self.call(commands.status)



	##################
	#      DOOR      #
	##################

	def exposed_door_add(self, ip, dev):
		return self.call(commands.door.add, ip, dev)

	def exposed_door_chg(self, ip, new_ip=None, new_dev=None):
		return self.call(commands.door.chg, ip, new_ip=new_ip, new_dev=new_dev)

	def exposed_door_del(self, ip):
		return self.call(commands.door.delete, ip)

	def exposed_door_show(self):
		return self.call(commands.door.show)



	##################
	#   CONTROLLER   #
	##################

	def exposed_controller_set(self, throughput=None, latency=None):
		return self.call(commands.controller.set, throughput=throughput, latency=latency)

	def exposed_controller_show(self):
		return self.call(commands.controller.show)



	##################
	#     DEVICE     #
	##################

	def exposed_device_add(self, name, mac, image, ports=[]):
		return self.call(commands.device.add, name, mac, image, ports)

	def exposed_device_chg(self, name, new_name=None, new_image=None, new_ports=None):
		return self.call(commands.device.chg, name, new_name=new_name, new_image=new_image, new_ports=new_ports)

	def exposed_device_del(self, name):
		return self.call(commands.device.delete, name)

	def exposed_device_show(self):
		return self.call(commands.device.show)



	##################
	#      IMAGE     #
	##################

	def exposed_image_add(self, name, username="root", password="root"):
		return self.call(commands.image.add, name, username=username, password=password)

	def exposed_image_chg(self, name, username=None, password=None):
		return self.call(commands.image.chg, name, username=username, password=password)

	def exposed_image_del(self, name):
		return self.call(commands.image.delete, name)

	def exposed_image_show(self):
		return self.call(commands.image.show)



	##################
	#       VM       #
	##################

	def exposed_vm_shell(self):
		return self.call(commands.vm.shell)

	def exposed_vm_start(self, phase):
		return self.call(commands.vm.start, phase)

	def exposed_vm_stop(self):
		return self.call(commands.vm.stop)
