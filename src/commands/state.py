# External
import os, sys, time

# Internal
from config import *
import glob
from common.utils.logs import *
from common.utils.misc import *
import common.utils.settings as settings


# Start HoneyWalt
def start(client):
	#####################
	#		CHECKS		#
	#####################

	if glob.SERVER.VM_CONTROLLER.pid() is not None:
		client.log(ERROR, "please stop HoneyWalt before to start")
		return None


	#####################
	#  LOAD RUN CONFIG  #
	#####################

	glob.RUN_CONFIG = get_conf()

	if glob.CONFIG["need_commit"] == "True":
		client.log(WARNING, "you have uncommited changes. Running with the previous commited configuration")

	glob.SERVER.DOORS_CONTROLLER.reload(glob.RUN_CONFIG)
	glob.SERVER.DOORS_CONTROLLER.start()


	#####################
	#	   CLEAN UP 	#
	#####################

	glob.SERVER.TUNNELS_CONTROLLER.init_run()
	glob.SERVER.COWRIE_CONTROLLER.init_run()
	glob.SERVER.TRAFFIC_CONTROLLER.init_run()


	#####################
	#		VM BOOT		#
	#####################

	log(INFO, "starting VM")
	glob.SERVER.VM_CONTROLLER.start(2)
	log(INFO, "waiting for VM to boot and connect")
	glob.SERVER.VM_CONTROLLER.connect()
	log(INFO, "sending phase to VM")
	glob.SERVER.VM_CONTROLLER.send_phase()
	log(INFO, "getting devices IPs")
	ips = glob.SERVER.VM_CONTROLLER.get_ips()

	if not ips:
		client.log(ERROR, "failed to get devices IPs")
		return None

	for ip in ips:
		dev = find(glob.RUN_CONFIG["device"], ip["id"], "id")
		dev["ip"] = ip["ip"]


	#####################
	#	 START COWRIE	#
	#####################
	
	# Start tunnels between cowrie and devices
	log(INFO, "starting tunnels between cowrie and Walt nodes")
	glob.SERVER.TUNNELS_CONTROLLER.start_cowrie_dmz()

	# Start cowrie
	log(INFO, "starting cowrie")
	glob.SERVER.COWRIE_CONTROLLER.start_cowrie()


	#####################
	#	  FIREWALL		#
	#####################

	# Start doors firewalls
	log(INFO, "starting doors firewalls")
	glob.SERVER.DOORS_CONTROLLER.firewall_up()


	#####################
	#	  WIREGUARD 	#
	#####################

	# Formatting devices wireguard public keys
	keys = [] #<door_id,dev_id,pubkey>
	for door in glob.RUN_CONFIG["door"]:
		dev = find(glob.RUN_CONFIG["device"], door["dev"], "node")
		keys += [{"door_id": door["id"], "dev_id": dev["id"], "pubkey": dev["pubkey"]}]

	log(INFO, "removing doors wireguard peers")
	glob.SERVER.DOORS_CONTROLLER.wg_reset()
	log(INFO, "adding doors wireguard peers")
	glob.SERVER.DOORS_CONTROLLER.wg_add_peer(keys)
	log(INFO, "starting vm wireguard")
	glob.SERVER.VM_CONTROLLER.wg_up()
	log(INFO, "starting doors wireguard")
	glob.SERVER.DOORS_CONTROLLER.wg_up()
	log(INFO, "starting doors traffic-shaper")
	glob.SERVER.DOORS_CONTROLLER.traffic_shaper_up()
	log(INFO, "starting local traffic-shaper")
	glob.SERVER.TRAFFIC_CONTROLLER.traffic_shaper_up()


	#####################
	#  TRAFFIC CONTROL  #
	#####################

	# Start traffic control
	log(INFO, "starting traffic control")
	glob.SERVER.TRAFFIC_CONTROLLER.start_control()


	#####################
	#		EXPOSE		#
	#####################

	# Start tunnels between cowrie and doors
	log(INFO, "starting tunnels between doors and cowrie")
	glob.SERVER.TUNNELS_CONTROLLER.start_door_cowrie()

	# Start to expose other ports
	log(INFO, "starting exposed ports tunnels")
	glob.SERVER.TUNNELS_CONTROLLER.start_expose_ports()

	return True


# Commit some persistent information on the VM so it is taken
# into acount on the next boot
def commit(client, regen=True, force=False):
	if glob.SERVER.VM_CONTROLLER.pid() is not None:
		client.log(ERROR, "please stop HoneyWalt before to commit")
		return None

	if glob.CONFIG["need_commit"] == "Empty":
		client.log(ERROR, "Your configuration is empty")
		return None
	elif glob.CONFIG["need_commit"] == "False" and not force:
		client.log(ERROR, "Nothing new to commit")
		return None

	if regen:
		log(INFO, "generating cowrie configurations")
		glob.SERVER.COWRIE_CONTROLLER.generate_configurations()

	log(INFO, "reloading doors controller")
	glob.SERVER.DOORS_CONTROLLER.reload(glob.CONFIG)
	glob.SERVER.DOORS_CONTROLLER.start()

	log(INFO, "generating doors wireguard keys")
	doors_keys = glob.SERVER.DOORS_CONTROLLER.wg_keygen()

	# Format door data for VM
	doors = []
	for door_key in doors_keys:
		door = find(glob.CONFIG["door"], door_key["host"], "host")
		dev = find(glob.CONFIG["device"], door["dev"], "node")
		doors += [{
			"ip":settings.get("IP_FOR_DMZ"),
			"port":settings.get("WIREGUARD_PORTS")+int(door["id"]),
			"dev_id":dev["id"],
			"wg_pubkey":door_key["pubkey"]
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
	log(INFO, "sending phase to VM")
	glob.SERVER.VM_CONTROLLER.send_phase()
	log(INFO, "sending devices to VM")
	glob.SERVER.VM_CONTROLLER.send_devices(devices)
	log(INFO, "sending doors to VM")
	glob.SERVER.VM_CONTROLLER.send_doors(doors)
	log(INFO, "generating VM wireguard keys")
	vm_keys = glob.SERVER.VM_CONTROLLER.wg_keygen()
	log(INFO, "commit on VM")
	glob.SERVER.VM_CONTROLLER.commit()
	
	# Adding wireguard public keys to devices in config
	for dev_key in vm_keys: #<dev_id,pubkey>
		dev = find(glob.CONFIG["device"], dev_key["dev_id"], "id")
		dev["pubkey"] = dev_key["pubkey"]

	log(INFO, "updating local configuration file")
	set_conf(glob.CONFIG, need_commit=False)

	log(INFO, "stopping VM")
	glob.SERVER.VM_CONTROLLER.stop()

	return True


def stop(client):
	# Tunnels and Cowrie
	log(INFO, "stopping exposed ports tunnels")
	glob.SERVER.TUNNELS_CONTROLLER.stop_expose_ports()
	log(INFO, "stopping cowrie tunnels to doors")
	glob.SERVER.TUNNELS_CONTROLLER.stop_cowrie_tunnels_out()
	log(INFO, "stopping cowrie")
	glob.SERVER.COWRIE_CONTROLLER.stop()
	log(INFO, "stopping cowrie tunnels to dmz")
	glob.SERVER.TUNNELS_CONTROLLER.stop_cowrie_tunnels_dmz()
	
	# Traffic Shaper
	log(INFO, "stopping traffic shaper on controller side")
	glob.SERVER.TRAFFIC_CONTROLLER.traffic_shaper_down()
	log(INFO, "stopping traffic shaper on doors side")
	glob.SERVER.DOORS_CONTROLLER.traffic_shaper_down()
	
	# Wireguard
	log(INFO, "stopping wireguard")
	glob.SERVER.DOORS_CONTROLLER.wg_down()
	
	# VM
	log(INFO, "stopping VM")
	glob.SERVER.VM_CONTROLLER.stop()
	
	# Traffic Control and Firewalls
	log(INFO, "stopping traffic control")
	glob.SERVER.TRAFFIC_CONTROLLER.stop_control()
	log(INFO, "stopping doors firewalls")
	glob.SERVER.DOORS_CONTROLLER.firewall_down()

	return True


def restart(client, regen=False):
	# Stop
	res_stop = stop(client, None)
	if not res_stop:
		client.log(ERROR, "Failed to stop HoneyWalt")
		return False

	# Commit
	if regen:
		res_commit = commit(client, None, force=True)
		if not res_commit:
			client.log(ERROR, "Failed to commit new changes")
			return False
	
	# Start
	res_start = start(client, None)
	if not res_start:
		client.log(ERROR, "Failed to start HoneyWalt")
		return False

	return True


def status(client):
	res = {}

	# VM
	vm_pid = glob.SERVER.VM_CONTROLLER.pid()
	res["running"] = vm_pid is not None
	if vm_pid is not None:
		res["vm_pid"] = vm_pid
	
	# Cowrie
	res["cowrie_instances"] = glob.SERVER.COWRIE_CONTROLLER.running_cowries()
	
	# Configuration
	res["nb_devs"] = len(glob.CONFIG["device"])
	res["nb_doors"] = len(glob.CONFIG["door"])

	return res
