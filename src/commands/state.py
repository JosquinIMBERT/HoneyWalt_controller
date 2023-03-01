# External
import os, sys, time

# Internal
from config import *
import glob
import tools.cowrie as cowrie
import tools.traffic as traffic
import tools.tunnel as tunnel
import tools.wireguard as wg
from utils.logs import *
from utils.misc import *
from control_socket import ControlSocket


# Start HoneyWalt
def start():
	res={"success":True}


	#####################
	#		CHECKS		#
	#####################

	if glob.SERVER.VM_CONTROLLER.pid() is not None:
		res["success"] = False
		res["msg"] = "please stop HoneyWalt before to start"
		return res


	#####################
	#  LOAD RUN CONFIG  #
	#####################

	glob.RUN_CONFIG = get_conf()

	if glob.CONFIG["need_commit"] == "True":
		res["msg"] = "warning: you have uncommited changes. Running with the previous commited configuration"


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
		res["success"] = False
		res["msg"] = "failed to get devices IPs"
		return res

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

	log(INFO, "starting vm wireguard")
	glob.SERVER.VM_CONTROLLER.wg_up()
	log(INFO, "starting doors wireguard")
	glob.SERVER.DOORS_CONTROLLER.wg_up()
	log(INFO, "adding doors wireguard peers")
	glob.SERVER.DOORS_CONTROLLER.wg_add_peer()#TODO
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

	return res


# Commit some persistent information on the VM so it is taken
# into acount on the next boot
def commit(regen=True, force=False):
	res={"success":True}

	if glob.SERVER.VM_CONTROLLER.pid() is not None:
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
		glob.SERVER.COWRIE_CONTROLLER.generate_configurations()

	log(INFO, "generating doors wireguard keys")
	doors_keys = glob.SERVER.DOORS_CONTROLLER.wg_keygen()

	# Format door data for VM
	doors = []
	for door_key in doors_keys:
		door = find(glob.CONFIG["door"], door_key["host"], "host")
		doors += [{
			"ip":settings.get("IP_FOR_DMZ"),
			"door":settings.get("WIREGUARD_PORTS")+int(door["id"]),
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
		glob.SERVER.DOORS_CONTROLLER.wg_add_peer(vm_keys) # <door_id,dev_id,pubkey>

	log(INFO, "updating configuration file")
	set_conf(glob.CONFIG, need_commit=False)

	log(INFO, "stopping VM")
	glob.SERVER.VM_CONTROLLER.stop()

	return res


def stop():
	res={"success":True}

	log(INFO, "stopping exposed ports tunnels")
	tunnel.stop_exposure_tunnels()
	log(INFO, "stopping cowrie tunnels to doors")
	tunnel.stop_cowrie_tunnels_out()
	log(INFO, "stopping cowrie")
	cowrie.stop()
	log(INFO, "stopping cowrie tunnels to dmz")
	tunnel.stop_cowrie_tunnels_dmz()
	log(INFO, "stopping udp tcp adapter")
	wg.stop_tcp_tunnels()
	log(INFO, "stopping wireguard")
	wg.stop_tunnels()
	log(INFO, "stopping VM")
	glob.SERVER.VM_CONTROLLER.stop()
	log(INFO, "stopping traffic control")
	traffic.stop_control()
	log(INFO, "stopping doors firewalls")
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
