# External
import fileinput, os, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
import glob
from config import get_conf
from common.utils.files import *
from vm.proto import *
from vm.controller import *

class VMControllerClient:
	def __init__(self):
		self.controller = VMController()
		self.controller.connect()
		self.help = len(VM_COMMANDS)
		self.quit = len(VM_COMMANDS)+1

	def __del__(self):
		del self.controller

	def print_help(self):
		print("Enter one of the following numbers:")
		for key in VM_COMMANDS:
			print("\t-  "+str(VM_COMMANDS[key])+" - "+str(key))
		print("\t- "+str(self.help)+" - HELP")
		print("\t- "+str(self.quit)+" - QUIT")

	def execute(self, cmd):
		if cmd == CMD_VM_PHASE:
			print("Enter phase > ")
			phase = int(fileinput.input())
			print(self.controller.send_phase(phase))
		elif cmd == CMD_VM_WALT_DEVS:
			# Get info
			print("Enter name > ")
			name = fileinput.input()
			print("Enter image > ")
			image = fileinput.input()
			print("Enter username > ")
			username = fileinput.input()
			print("Enter password > ")
			password = fileinput.input()			
			print("Enter MAC address > ")
			mac = fileinput.input()
			# Build object
			dev = {"name":name, "image":image, "username":username, "password":password, "mac":mac}
			# Send
			print(self.controller.send_device())
		elif cmd == CMD_VM_WALT_IPS:
			print(self.controller.get_ips())
		elif cmd == CMD_VM_WG_KEYGEN:
			print(self.controller.wg_keygen())
		elif cmd == CMD_VM_WG_DOORS:
			doors = []
			while True:
				print("Do you want to add more doors? (y/N)")
				more = fileinput.input()
				if more == "y" or more =="Y":
					print("Enter door IP address >")
					ip = fileinput.input()
					print("Enter door port >")
					port = fileinput.input()
					print("Enter door wireguard pubkey >")
					key = fileinput.input()
					doors += [{"ip":ip, "port":port, "wg_pubkey": key}]
				else:
					break
			print(self.controller.send_doors(doors))
		elif cmd == CMD_VM_WG_UP:
			print(self.controller.wg_up())
		elif cmd == CMD_VM_WG_DOWN:
			print(self.controller.wg_down())
		elif cmd == CMD_VM_COMMIT:
			print(self.controller.commit())
		elif cmd == CMD_VM_SHUTDOWN:
			print(self.controller.shutdown())
		elif cmd == CMD_VM_LIVE:
			print(self.controller.connected())
		else:
			print("Unknown command")

	def run(self):
		self.print_help()

		for line in fileinput.input():
			cmd = int(line)
			if cmd == self.help:
				self.print_help()
			elif cmd == self.quit:
				print("QUIT")
				break
			else:
				self.execute(cmd)

def main():
	glob.init(None, get_conf(), to_root_path("var/key/id_olim"), to_root_path("var/key/id_olim.pub"), to_root_path("var/key/id_door"), to_root_path("var/key/id_door.pub"))
	cli = VMControllerClient()
	cli.run()

if __name__ == '__main__':
	main()