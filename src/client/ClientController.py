# External
import os, rpyc, ssl, sys
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
			to_root_path("var/key/pki/private/server.key"),
			to_root_path("var/key/pki/server.crt"),
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
		log(INFO, "Creating the ClientService")

	def __del__(self):
		log(INFO, "Deleting the ClientService")

	def on_connect(self, conn):
		log(INFO,"New connection from", conn)

	def on_disconnect(self, conn):
		log(INFO, "End of connection with", conn)



	##################
	#      STATE     #
	##################
	
	def exposed_start(self):
		return commands.state.start()

	def exposed_commit(self, regen=True):
		return commands.state.commit(regen=regen)

	def exposed_stop(self):
		return commands.state.stop()

	def exposed_restart(self, regen=False):
		return commands.state.restart(regen=regen)

	def exposed_status(self):
		return commands.status()



	##################
	#      DOOR      #
	##################

	def exposed_door_add(self, ip, dev):
		return commands.door.add(ip, dev)

	def exposed_door_chg(self, ip, new_ip=None, new_dev=None):
		return commands.door.chg(ip, new_ip=new_ip, new_dev=new_dev)

	def exposed_door_del(self, ip):
		return commands.door.delete(ip)

	def exposed_door_show(self):
		return commands.door.show()



	##################
	#   CONTROLLER   #
	##################

	def exposed_controller_set(self, throughput=None, latency=None):
		return commands.controller.set(throughput=throughput, latency=latency)

	def exposed_controller_show(self):
		return commands.controller.show()



	##################
	#     DEVICE     #
	##################

	def exposed_device_add(self, name, mac, image, ports=[]):
		return commands.device.add(name, mac, image, ports)

	def exposed_device_chg(self, name, new_name=None, new_image=None, new_ports=None):
		return commands.device.chg(name, new_name=new_name, new_image=new_image, new_ports=new_ports)

	def exposed_device_del(self, name):
		return commands.device.delete(name)

	def exposed_device_show(self):
		return commands.device.show()



	##################
	#      IMAGE     #
	##################

	def exposed_image_add(self, name, username="root", password="root"):
		return commands.image.add(name, username=username, password=password)

	def exposed_image_chg(self, name, username=None, password=None):
		return commands.image.chg(name, username=username, password=password)

	def exposed_image_del(self, name):
		return commands.image.delete(name)

	def exposed_image_show(self):
		return commands.image.show()



	##################
	#       VM       #
	##################

	def exposed_vm_shell(self):
		return commands.vm.shell()

	def exposed_vm_start(self, phase):
		return commands.vm.start(phase)

	def exposed_vm_stop(self):
		return commands.vm.stop()
