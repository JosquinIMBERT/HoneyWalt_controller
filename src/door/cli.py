# External
import fileinput, os, sys

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
import glob
from config import get_conf
from door.proto import *
from door.controller import *
from utils.files import *

class DoorControllerClient:
	def __init__(self, door):
		self.controller = DoorController(door)
		self.controller.connect()
		self.help = len(DOOR_COMMANDS)
		self.quit = len(DOOR_COMMANDS)+1

	def __del__(self):
		del self.controller

	def print_help(self):
		print("Enter one of the following numbers:")
		for key in DOOR_COMMANDS:
			print("\t-  "+str(DOOR_COMMANDS[key])+" - "+str(key))
		print("\t-  "+str(self.help)+" - HELP")
		print("\t- "+str(self.quit)+" - QUIT")

	def execute(self, cmd):
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
		elif cmd == CMD_DOOR_WG_GEN_CONF:
			print(self.controller.wg_gen_conf())
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_UP:
			print(self.controller.traffic_shaper_up())
		elif cmd == CMD_DOOR_TRAFFIC_SHAPER_DOWN:
			print(self.controller.traffic_shaper_down())
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
	cli = DoorControllerClient({"ip":"127.0.0.1", "port":9999})
	cli.run()

if __name__ == '__main__':
	main()