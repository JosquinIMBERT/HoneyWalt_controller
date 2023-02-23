# External
import fileinput, os, sys

# Internal
sys.path.insert(0, os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/"))
import glob
from config import get_conf
from utils.files import *
from vm.proto import *
from vm.controller import *

class VMControllerClient:
	def __init__(self):
		self.controller = VMController()
		self.controller.connect()

	def __del__(self):
		del self.controller

	def print_help(self):
		print("Enter one of the following numbers:")
		print("\t-  0 - QUIT")
		print("\t-  1 - CMD_VM_PHASE")
		print("\t-  2 - CMD_VM_WALT_ADD_DEV")
		print("\t-  3 - CMD_VM_WALT_DEV_IP")
		print("\t-  4 - CMD_VM_WG_KEYGEN")
		print("\t-  5 - CMD_VM_WG_DOORS")
		print("\t-  6 - CMD_VM_WG_DEL_CONF")
		print("\t-  7 - CMD_VM_WG_UP")
		print("\t-  8 - CMD_VM_WG_DOWN")
		print("\t-  9 - CMD_VM_COMMIT")
		print("\t- 10 - CMD_VM_SHUTDOWN")
		print("\t- 11 - CMD_VM_LIVE")
		print("\t- 12 - HELP")

	def execute(self, cmd):
		if cmd == CMD_VM_PHASE:
			print("Enter phase > ")
			phase = int(fileinput.input())
			print(self.controller.send_phase(phase))
		elif cmd == CMD_VM_WALT_ADD_DEV:
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
		elif cmd == CMD_VM_WALT_DEV_IP:
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
		elif cmd == CMD_VM_WG_DEL_CONF:
			print(self.controller.wg_del_conf())
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
			if cmd == 12:
				self.print_help()
			elif cmd == 0:
				print("QUIT")
				break
			else:
				self.execute(cmd)

def main():
	glob.init(None, get_conf(), to_root_path("var/key/id_olim"), to_root_path("var/key/id_olim.pub"), to_root_path("var/key/id_door"), to_root_path("var/key/id_door.pub"))
	cli = VMControllerClient({"ip":"127.0.0.1", "port":9999})
	cli.run()

if __name__ == '__main__':
	main()