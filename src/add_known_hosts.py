# External
from string import Template

# Internal
from config import get_conf
from tools.tunnels import Tunnels

# Common
from common.utils.files import *
from common.utils.system import run

def main():
	command_template = Template("ssh -i ${key} ${user}@${host} -p ${port} exit")

	conf = get_conf()
	for honeypot in conf["honeypots"]:
		command = command_template.substitute({
			"key"  : to_root_path("var/key/id_door"),
			"user" : "root",
			"host" : honeypot["door"]["host"],
			"port" : Tunnels.REAL_SSH
		})
		run(command)

if __name__ == '__main__':
	main()