# External
import os, sys, time

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
from config import set_conf
import glob
import tools.cowrie as cowrie
import tools.traffic as traffic
import tools.tunnel as tunnel
import tools.wireguard as wg
from utils import *
from control_socket import ControlSocket


# Start HoneyWalt
def start():
	res={"success":True}

	if is_running():
		res["success"] = False
		res["msg"] = "please stop HoneyWalt before to start"
		return res

	# Check if changes were commited
	if glob.CONFIG["need_commit"] == "Empty":
		res["success"] = False
		res["msg"] = "your configuration is empty"
		return res
	elif glob.CONFIG["need_commit"] == "True":
		res["success"] = False
		res["msg"] = "you need to commit your configuration before to run HoneyWalt"
		return res

	delete(to_root_path("run/cowrie/pid"), suffix=".pid")
	delete(to_root_path("run/ssh/cowrie-dmz"), suffix=".pid")
	delete(to_root_path("run/ssh/cowrie-out"), suffix=".pid")
	delete(to_root_path("run/traffic-shaper"), suffix=".pid")

	# Allow cowrie user to access cowrie files
	run("chown -R cowrie "+to_root_path("run/cowrie/"), "failed chown cowrie")

	# Start the VM
	log(glob.INFO, "starting VM")
	glob.SERVER.VM_CONTROLLER.start(2)
	glob.VM_SOCK = ControlSocket(2)
	
	# List the backends
	backends = []
	i=0
	for dev in glob.CONFIG["device"]:
		backends += [ dev["node"] ]
		i+=1
	
	# List the images
	images = []
	i=0
	for img in glob.CONFIG["image"]:
		images += [ img["short_name"] ]

	# Initiate control
	log(glob.INFO, "initiating VM control")
	glob.VM_SOCK.initiate(backends=backends, images=images)
	
	# Start tunnels between cowrie and devices
	log(glob.INFO, "starting tunnels between cowrie and Walt nodes")
	tunnel.start_cowrie_tunnels_dmz()

	# Start cowrie
	log(glob.INFO, "starting cowrie")
	cowrie.start()

	# Start doors firewalls
	log(glob.INFO, "starting doors firewalls")
	traffic.start_door_firewall()

	# Start wireguard
	log(glob.INFO, "starting wireguard")
	wg.start_tunnels()
	log(glob.INFO, "starting udp to tcp adapter")
	wg.start_tcp_tunnels()

	# Start traffic control
	log(glob.INFO, "starting traffic control")
	traffic.start_control()

	# Start tunnels between cowrie and doors
	log(glob.INFO, "starting tunnels between doors and cowrie")
	tunnel.start_cowrie_tunnels_out()

	# Start to expose other ports
	log(glob.INFO, "starting exposed ports tunnels")
	tunnel.start_exposure_tunnels()

	return res


# Commit some persistent information on the VM so it is taken
# into acount on the next boot
def commit(regen=True, force=False):
	res={"success":True}

	if is_running():
		res["success"] = False
		res["msg"] = "please stop HoneyWalt before to commit"
		return res

	if glob.CONFIG["need_commit"] == "Empty":
		res["success"] = False
		res["msg"] = "Your configuration is empty"
		return res
	elif glob.CONFIG["need_commit"] == "False" and not force:
		res["success"] = False
		res["msg"] = "Nothing new to commit"
		return res

	if regen:
		log(INFO, "generating cowrie configurations")
		cowrie.gen_configurations()

	log(INFO, "generating doors wireguard keys")
	doors_keys = glob.SERVER.DOORS_CONTROLLER.wg_keygen()

	# Format door data for VM
	doors = []
	for door_key in doors_keys:
		door = find(glob.CONFIG["door"], door_key["host"], "host")
		doors += [{
			"ip":glob.IP_FOR_DMZ,
			"door":glob.WIREGUARD_PORTS+int(door["id"]),
			"dev":door["dev"],
			"wg_pubkey":door_key["wg_pubkey"]
		}]

	# Format device data for VM
	devices = []
	for dev in glob.CONFIG["device"]:
		image = find(glob.CONFIG["image"], dev["image"], "short_name")
		devices += [{
			"name": dev["node"],
			"mac": dev["mac"],
			"image": dev["image"],
			"username": image["user"],
			"password": image["pass"],
			"id": dev["id"]
		}]

	log(INFO, "starting VM")
	glob.SERVER.VM_CONTROLLER.start(1)
	log(INFO, "waiting for VM to boot and connect")
	glob.SERVER.VM_CONTROLLER.connect()
	log(INFO, "sending phase to VM")
	glob.SERVER.VM_CONTROLLER.send_phase()
	log(INFO, "sending devices to VM")
	glob.SERVER.VM_CONTROLLER.send_devices(devices)
	log(INFO, "sending doors to VM")
	glob.SERVER.VM_CONTROLLER.send_doors(doors)
	log(INFO, "generating VM wireguard keys")
	vm_keys = glob.SERVER.VM_CONTROLLER.wg_keygen()
	log(INFO, "generating VM wireguard configuration (VM commit)")
	glob.SERVER.VM_CONTROLLER.commit()
	
	if regen:
		log(INFO, "generating doors wireguard configurations")
		glob.SERVER.DOORS_CONTROLLER.commit(vm_keys) # <dev_name,dev_wg_pubkey>

	log(INFO, "updating configuration file")
	set_conf(glob.CONFIG, need_commit=False)

	log(INFO, "stopping VM")
	glob.SERVER.VM_CONTROLLER.stop()

	return res


def stop():
	res={"success":True}

	log(glob.INFO, "stopping exposed ports tunnels")
	tunnel.stop_exposure_tunnels()
	log(glob.INFO, "stopping cowrie tunnels to doors")
	tunnel.stop_cowrie_tunnels_out()
	log(glob.INFO, "stopping cowrie")
	cowrie.stop()
	log(glob.INFO, "stopping cowrie tunnels to dmz")
	tunnel.stop_cowrie_tunnels_dmz()
	log(glob.INFO, "stopping udp tcp adapter")
	wg.stop_tcp_tunnels()
	log(glob.INFO, "stopping wireguard")
	wg.stop_tunnels()
	log(glob.INFO, "stopping VM")
	glob.SERVER.VM_CONTROLLER.stop()
	log(glob.INFO, "stopping traffic control")
	traffic.stop_control()
	log(glob.INFO, "stopping doors firewalls")
	traffic.stop_door_firewall()

	return res


def restart(regen=False):
	res = {"success":True}

	# Stop
	res_stop = stop(None)
	if not res_stop["success"]:
		return res_stop

	# Commit
	if regen:
		res_commit = commit(None, force=True)
		if not res_commit["success"]:
			return res_commit
	
	# Start
	res_start = start(None)
	if not res_start["success"]:
		return res_start

	return res


def status():
	res={"success":True, "answer":{}}

	# VM
	vm_pid = glob.SERVER.VM_CONTROLLER.pid()
	res["answer"]["running"] = vm_pid is not None
	if vm_pid is not None:
		res["answer"]["vm_pid"] = vm_pid
	
	# Cowrie
	nb_cowrie_pids = cowrie.state()
	res["answer"]["cowrie_instances"] = nb_cowrie_pids
	
	# Configuration
	res["answer"]["nb_devs"] = len(glob.CONFIG["device"])
	res["answer"]["nb_doors"] = len(glob.CONFIG["door"])

	return res


# We consider the state of the VM determines whether HoneyWalt is running or not
def is_running():
	return glob.SERVER.VM_CONTROLLER.pid() is not None