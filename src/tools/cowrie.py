# External
import os
from string import Template

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
from common.utils.misc import *
import common.utils.settings as settings
import glob

class CowrieController:
	def __init__(self):
		log(INFO, "CowrieController.__init__: creating the CowrieController")

	def __del__(self):
		pass

	def delete_configurations(self):
		delete(to_root_path("run/cowrie/conf"), suffix=".conf")

	def generate_configurations(self):
		LISTEN_PORTS = settings.get("LISTEN_PORTS")
		BACKEND_PORTS = settings.get("BACKEND_PORTS")
		SOCKET_PORTS = settings.get("SOCKET_PORTS")

		self.delete_configurations()
		
		i=0
		with open(to_root_path("var/template/cowrie_conf.txt"), "r") as temp_file:
			temp = Template(temp_file.read())
		for dev in glob.CONFIG["device"]:
			img = find(glob.CONFIG["image"], dev["image"], "short_name")
			if img is None:
				log(WARNING, "image not found for device "+str(dev["node"]))
			else:
				backend_user = img["user"]
				backend_pass = img["pass"]
				download_path = to_root_path("run/cowrie/download/"+str(i)+"/")
				if not exists(download_path):
					os.mkdir(download_path)
				params = {
					'download_path' : download_path,
					'listen_port' : LISTEN_PORTS+i,
					'backend_host' : "127.0.0.1",
					'backend_port' : BACKEND_PORTS+i,
					'backend_user' : backend_user,
					'backend_pass' : backend_pass,
					'logfile' : to_root_path("run/cowrie/log/"+str(i)+".json"),
					'socket_port' : SOCKET_PORTS+i
				}
				content = temp.substitute(params)
				with open(to_root_path("run/cowrie/conf/"+str(i)+".conf"), "w") as conf_file:
					conf_file.write(content)
				i+=1

	# Prepare cowrie to run
	def init_run(self):
		# Delete previous pid files
		delete(to_root_path("run/cowrie/pid"), suffix=".pid")

		# Allow cowrie user to access cowrie files
		if not run("chown -R cowrie "+to_root_path("run/cowrie/")):
			log(ERROR, "CowrieController.init_run: failed chown cowrie")

	def start_cowrie(self):
		# TODO: try to start cowrie without a shell command
		with open(to_root_path("var/template/start_cowrie.txt"), "r") as file:
			template = Template(file.read())
		for dev in glob.RUN_CONFIG["device"]:
			cmd = template.substitute({
				"conf_path": to_root_path("run/cowrie/conf/"+str(dev["id"])+".conf"),
				"pid_path": to_root_path("run/cowrie/pid/"+str(dev["id"])+".pid"),
				"log_path": to_root_path("run/cowrie/log/"+str(dev["id"])+".log")
			})
			if not run(cmd):
				log(ERROR, "CowrieController.strat_cowrie: failed to start cowrie")

	def stop(self):
		path = to_root_path("run/cowrie/pid")
		for pidpath in os.listdir(path):
			if pidpath.endswith(".pid"):
				try:
					kill_from_file(os.path.join(path, pidpath))
				except:
					log(WARNING, "Failed to stop a cowrie instance. The pid file is: "+str(pidpath))

	def running_cowries(self):
		# code from https://stackoverflow.com/questions/2632205/how-to-count-the-number-of-files-in-a-directory-using-python#2632251
		DIR = to_root_path("run/cowrie/pid")
		nb_pids = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name)) and name.endswith(".pid") and read_pid_file(os.path.join(DIR, name))])
		return nb_pids

	# Listen the logs for a given device name
	# Print the output to stdout
	# This may be piped into another program that analyzes the logs from its standard input
	def read_logs(self, dev):
		device = find(glob.RUN_CONFIG, dev, "node")
		run("nc -lp "+str(dev["id"]))