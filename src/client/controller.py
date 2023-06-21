# External
import ssl, threading
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
from common.utils.logs import *
from common.utils.rpc import AbstractService

class ClientController():
	def __init__(self):
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
		self.threaded_server = ThreadedServer(ClientService, port=CLIENT_PORT, authenticator=authenticator)
		self.service_thread = threading.Thread(target=self.run)
		self.service_thread.start()

	def run(self):
		self.threaded_server.start()

	def stop(self):
		if self.threaded_server is not None: self.threaded_server.close()
		if self.service_thread is not None: self.service_thread.close()

class ClientService(AbstractService):
	def __init__(self):
		AbstractService.__init__(self)

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
