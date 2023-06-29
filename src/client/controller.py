# External
import ssl, threading
from rpyc.utils.server import ThreadedServer
from rpyc.utils.authenticators import SSLAuthenticator

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.rpc import AbstractService

class ClientController():

	CLIENT_PORT = 9999

	def __init__(self, server):
		log(INFO, "Creating the ClientController")
		self.server = server

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
		ClientService = CustomizedClientService(self.server)
		self.threaded_server = ThreadedServer(ClientService, port=ClientController.CLIENT_PORT, authenticator=authenticator)
		self.service_thread = threading.Thread(target=self.run)
		self.service_thread.start()

	def run(self):
		self.threaded_server.start()

	def stop(self):
		if self.threaded_server is not None: self.threaded_server.close()
		if self.service_thread is not None: self.service_thread.join()


# This function customizes the ClientService class so that it takes the server as a parameter parameter
def CustomizedClientService(server):
	class ClientService(AbstractService):
		def __init__(self):
			AbstractService.__init__(self, ignore_client=False)

			self.server = server



		##################
		#      STATE     #
		##################
		
		def exposed_start(self):
			return self.call(self.server.state_manager.start)

		def exposed_commit(self, regen=True):
			return self.call(self.server.state_manager.commit, regen=regen)

		def exposed_stop(self):
			return self.call(self.server.state_manager.stop)

		def exposed_restart(self, regen=False):
			return self.call(self.server.state_manager.restart, regen=regen)

		def exposed_status(self):
			return self.call(self.server.state_manager.status)



		##################
		#    HONEYPOT    #
		##################

		def exposed_honeypot_add(self, door, device_name, device_mac, image, username=None, password=None, ports=None):
			return self.call(self.server.honeypot_manager.add,
				door,
				device_name,
				device_mac,
				image,
				username=username,
				password=password,
				ports=ports
			)

		def exposed_honeypot_chg(self, ident, door=None, device_name=None, device_mac=None, image=None, username=None, password=None, ports=None):
			return self.call(self.server.honeypot_manager.change,
				ident,
				door=door,
				device_name=device_name,
				device_mac=device_mac,
				image=image,
				username=username,
				password=password,
				ports=ports
			)

		def exposed_honeypot_del(self, ident):
			return self.call(self.server.honeypot_manager.delete, ident)

		def exposed_honeypot_show(self):
			return self.call(self.server.honeypot_manager.show)



		##################
		#       VM       #
		##################

		def exposed_vm_shell(self):
			return self.call(self.server.vm_manager.shell)

		def exposed_vm_start(self, phase):
			return self.call(self.server.vm_manager.start, phase)

		def exposed_vm_stop(self):
			return self.call(self.server.vm_manager.stop)

	return ClientService