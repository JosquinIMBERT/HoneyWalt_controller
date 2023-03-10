# External
import argparse, fileinput, os, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
import glob
from config import get_conf
from common.door.proto import *
from door.controller import *
from common.utils.files import *
from common.utils.logs import *

class DoorControllerClient:
	def __init__(self, door):
		self.controller = DoorController(door)
		self.controller.connect()
		self.help = len(DOOR_COMMANDS)+1
		self.quit = len(DOOR_COMMANDS)+2

	def __del__(self):
		del self.controller

	def print_help(self):
		print("Enter one of the following numbers:")
		for key in DOOR_COMMANDS:
			if DOOR_COMMANDS[key] == CMD_DOOR_WG_ADD_PEER:
				print("\t-  "+str(DOOR_COMMANDS[key])+" - "+str(key)+" <pubkey> <dev_id>")
			else:
				print("\t-  "+str(DOOR_COMMANDS[key])+" - "+str(key))
		print("\t- "+str(self.help)+" - HELP")
		print("\t- "+str(self.quit)+" - QUIT")

	def execute(self, cmd, line):
		if cmd == CMD_DOOR_FIREWALL_UP:
			print(self.controller.firewall_up())
		elif cmd == CMD_DOOR_FIREWALL_DOWN:
			print(self.controller.firewall_down())
		elif cmd == CMD_DOOR_WG_KEYGEN:
			print(self.controller.wg_keygen())
		elif cmd == CMD_DOOR_WG_UP:
			print(self.controller.wg_up())
		elif cmd == CMD_DOOR_WG_DOWN:
			print(self.controller.wg_down())
		elif cmd == CMD_DOOR_WG_ADD_PEER:
			if len(line) != 2:
				print("[ERROR] invalid arguments")
				return None
			pubkey = line[0]
			dev_id = int(line[1])
			print(self.controller.wg_add_peer(pubkey, dev_id))
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_UP:
			print(self.controller.traffic_shaper_up())
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_DOWN:
			print(self.controller.traffic_shaper_down())
		elif cmd == CMD_DOOR_LIVE:
			print(self.controller.connected())
		else:
			print("Unknown command")

	def run(self):
		self.print_help()

		print("cli>", end='', flush=True)
		for line in fileinput.input(files=[]):
			line = line.split(" ")
			try:
				cmd = int(line[0])
			except:
				pass
			else:
				if cmd == self.help:
					self.print_help()
				elif cmd == self.quit:
					print("QUIT")
					break
				else:
					self.execute(cmd, line[1:])
			print("cli>", end='', flush=True)

def main():
	parser = argparse.ArgumentParser(description='HoneyWalt Door Client: test the door protocol from a command line interface')
	parser.add_argument("-a", "--ip-address", nargs=1, help="IP address of the door")
	parser.add_argument("-p", "--port", nargs=1, help="Port where the door listens")
	parser.add_argument("-l", "--log-level", nargs=1, help="Set log level (CMD, DEBUG, INFO, WARNING, ERROR, FATAL)")
	options = parser.parse_args()

	ip = "127.0.0.1"
	port = 5556

	if options.log_level is not None:
		log_level = options.log_level[0]
		set_log_level(log_level)
	if options.ip_address is not None:
		ip = options.ip_address[0]
	if options.port is not None:
		port = int(options.port[0])

	glob.init(None, get_conf(), to_root_path("var/key/id_olim"), to_root_path("var/key/id_olim.pub"), to_root_path("var/key/id_door"), to_root_path("var/key/id_door.pub"))
	cli = DoorControllerClient({"host":ip, "port":port})
	cli.run()

if __name__ == '__main__':
	main()