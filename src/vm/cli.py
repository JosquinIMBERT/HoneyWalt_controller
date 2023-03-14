# External
import argparse, fileinput, os, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
import glob
from config import get_conf
from common.utils.files import *
from common.utils.logs import *
from common.vm.proto import *
from vm.controller import *

class VMControllerClient:
	def __init__(self):
		self.controller = VMController()
		self.help = len(VM_COMMANDS)+1
		self.quit = len(VM_COMMANDS)+2

	def __del__(self):
		del self.controller

	def print_help(self):
		print("Enter one of the following numbers:")
		for key in VM_COMMANDS:
			spaces = " " * (3-len(str(VM_COMMANDS[key])))
			if VM_COMMANDS[key] == CMD_VM_PHASE:
				print("\t-"+spaces+str(VM_COMMANDS[key])+" - "+str(key)+" <phase> [start]")
			elif VM_COMMANDS[key] == CMD_VM_WALT_DEVS:
				print("\t-"+spaces+str(VM_COMMANDS[key])+" - "+str(key)+" [<name>,<image>,<username>,<password>,<mac_addr> ...]")
			elif VM_COMMANDS[key] == CMD_VM_WG_DOORS:
				print("\t-"+spaces+str(VM_COMMANDS[key])+" - "+str(key)+" [<host>,<port>,<pubkey> ...]")
			else:
				print("\t-"+spaces+str(VM_COMMANDS[key])+" - "+str(key))
		print("\t- "+str(self.help)+" - HELP")
		print("\t- "+str(self.quit)+" - QUIT")

	def execute(self, cmd, args):
		if cmd == CMD_VM_PHASE:
			try: phase=int(args[0])
			except: log(ERROR, "invalid phase")
			else:
				if len(args)>1 and args[1].lower() == "start":
					log(INFO, "Starting the VM")
					self.controller.start(phase)
				print(self.controller.send_phase(phase=phase))
		elif cmd == CMD_VM_WALT_DEVS:
			# Build object
			devs = []
			for dev in devs:
				dev = dev.split(",")
				if len(dev) != 5:
					log(ERROR, "invalid device")
					continue
				devs += [{"name":dev[0], "image":dev[1], "username":dev[2], "password":dev[3], "mac":dev[4]}]
			# Send
			print(self.controller.send_devices(devs))
		elif cmd == CMD_VM_WALT_IPS:
			print(self.controller.get_ips())
		elif cmd == CMD_VM_WG_KEYGEN:
			print(self.controller.wg_keygen())
		elif cmd == CMD_VM_WG_DOORS:
			doors = []
			for door in doors:
				door = door.split(",")
				if len(door) != 3:
					log(ERROR, "invalid door")
					continue
				doors += [{"ip":door[0], "port":door[1], "wg_pubkey": door[2]}]
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

		print("cli>", end='', flush=True)
		for line in fileinput.input(files=[]):
			args = [arg.strip() for arg in line.split(" ")]
			try:
				cmd = int(args[0])
			except:
				pass
			else:
				if cmd == self.help:
					self.print_help()
				elif cmd == self.quit:
					print("QUIT")
					break
				else:
					self.execute(cmd, args[1:])
			print("cli>", end='', flush=True)

def main():
	parser = argparse.ArgumentParser(description='HoneyWalt VM Client: test the VM protocol from a command line interface')
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (CMD, DEBUG, INFO, WARNING, ERROR, FATAL)")
	options = parser.parse_args()

	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)
	
	glob.init(None, get_conf(), to_root_path("var/key/id_olim"), to_root_path("var/key/id_olim.pub"), to_root_path("var/key/id_door"), to_root_path("var/key/id_door.pub"))
	cli = VMControllerClient()
	cli.run()

if __name__ == '__main__':
	main()