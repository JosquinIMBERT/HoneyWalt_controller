# External
import os, sys, time

# Internal
from config import *
from common.utils.logs import *
from common.utils.misc import *
import common.utils.settings as settings


class StateManager:
	def __init__(self, server):
		self.server = server

	def __del__(self):
		pass



	# Start HoneyWalt
	def start(self, client):
		#####################
		#		CHECKS		#
		#####################

		if self.server.vm.pid() is not None:
			client.log(ERROR, "please stop HoneyWalt before to start")
			return None
		elif self.server.need_commit:
			client.log(ERROR, "please commit your modifications before to start")
			return None
		elif len(self.server.edit_config["honeypots"]) <= 0:
			client.log(ERROR, "please add at least one honeypot before to start")
			return None


		#####################
		#  LOAD RUN CONFIG  #
		#####################

		self.server.run_config = get_conf()

		self.server.doors.reload(self.server.run_config)


		#####################
		#	   CLEAN UP 	#
		#####################

		self.server.tunnels.init_run()
		self.server.cowrie.init_run()


		#####################
		#		VM BOOT		#
		#####################

		log(INFO, "starting VM")
		self.server.vm.start(2)
		log(INFO, "sending phase to VM")
		self.server.vm.send_phase()
		log(INFO, "getting devices IPs")
		ips = self.server.vm.get_ips()

		if not ips:
			client.log(ERROR, "failed to get devices IPs")
			self.server.vm.stop()
			return None

		for ip in ips:
			ident = ip["id"]
			if ident < len(self.server.run_config["honeypots"]):
				self.server.run_config["honeypots"][ident] = ip["ip"]


		#####################
		#	 START COWRIE	#
		#####################
		
		# Start tunnels between cowrie and devices
		log(INFO, "starting tunnels between cowrie and Walt nodes")
		self.server.tunnels.start_cowrie_dmz()

		# Start cowrie
		log(INFO, "starting cowrie")
		self.server.doors.cowrie_start()


		#####################
		#	  FIREWALL		#
		#####################

		# Start doors firewalls
		log(INFO, "starting doors firewalls")
		self.server.doors.firewall_up()


		#####################
		#	  WIREGUARD 	#
		#####################

		log(INFO, "removing doors wireguard peers")
		self.server.doors.wg_reset()
		log(INFO, "adding doors wireguard peers")
		self.server.doors.wg_set_peer()
		log(INFO, "starting vm wireguard")
		self.server.vm.wg_up()
		log(INFO, "starting doors wireguard")
		self.server.doors.wg_up()
		log(INFO, "starting doors shaper")
		self.server.doors.traffic_shaper_up()


		#####################
		#  TRAFFIC CONTROL  #
		#####################

		# Start traffic control
		log(INFO, "starting traffic control")
		self.server.traffic.start_control()


		#####################
		#		EXPOSE		#
		#####################

		# Start tunnels between cowrie and doors
		log(INFO, "starting tunnels between doors and cowrie")
		self.server.tunnels.start_door_cowrie()

		# Start to expose other ports
		log(INFO, "starting exposed ports tunnels")
		self.server.tunnels.start_expose_ports()

		return True



	# Commit some persistent information on the VM so it is taken
	# into acount on the next boot
	def commit(self, client, regen=True, force=False):
		if self.server.vm.pid() is not None:
			client.log(ERROR, "please stop HoneyWalt before to commit")
			return None

		if len(self.server.edit_config["honeypots"]) <= 0:
			client.log(ERROR, "Your configuration is empty")
			return None
		elif not self.server.need_commit and not force:
			client.log(ERROR, "Nothing new to commit")
			return None

		log(INFO, "reloading doors controller")
		self.server.doors.reload(self.server.edit_config)

		if regen:
			log(INFO, "generating cowrie configurations")
			self.server.doors.cowrie_configure()

		log(INFO, "generating doors wireguard keys")
		self.server.doors.wg_keygen()

		# Format door and device data for VM
		doors = []
		devices = []
		for honeypot in self.server.edit_config["honeypots"]:
			doors += [{
				"id"     : honeypot["id"],
				"pubkey" : honeypot["door"]["pubkey"]
			}]
			devices += [{
				"id"       : honeypot["id"],
				"name"     : honeypot["device"]["name"],
				"mac"      : honeypot["device"]["mac"],
				"image"    : honeypot["image"]["name"],
				"username" : honeypot["credentials"]["user"],
				"password" : honeypot["credentials"]["pass"]
			}]

		log(INFO, "starting VM")
		self.server.vm.start(1)
		log(INFO, "sending phase to VM")
		self.server.vm.send_phase()
		log(INFO, "sending devices to VM")
		self.server.vm.send_devices(devices)
		log(INFO, "sending doors to VM")
		self.server.vm.send_doors(doors)
		log(INFO, "generating VM wireguard keys")
		vm_keys = self.server.vm.wg_keygen()
		log(INFO, "commit on VM")
		self.server.vm.commit()

		# Adding wireguard public keys to devices in config
		for data in vm_keys: #<id,pubkey>
			if data["id"] < len(self.server.edit_config["honeypots"]):
				self.server.edit_config["honeypots"][data["id"]]["device"]["pubkey"] = data["pubkey"]

		self.server.doors.commit()

		log(INFO, "updating local configuration file")
		set_conf(self.server.edit_config)
		self.server.need_commit = False

		log(INFO, "stopping VM")
		self.server.vm.stop()

		return True



	def stop(self, client):
		# Tunnels and Cowrie
		log(INFO, "stopping exposed ports tunnels")
		self.server.tunnels.stop_expose_ports()
		log(INFO, "stopping cowrie tunnels to doors")
		self.server.tunnels.stop_cowrie_tunnels_out()
		log(INFO, "stopping cowrie")
		self.server.cowrie.stop()
		log(INFO, "stopping cowrie tunnels to dmz")
		self.server.tunnels.stop_cowrie_tunnels_dmz()
		
		# Traffic Shaper
		log(INFO, "stopping traffic shaper on doors side")
		self.server.doors.traffic_shaper_down()
		
		# Wireguard
		log(INFO, "stopping wireguard")
		self.server.doors.wg_down()
		
		# VM
		log(INFO, "stopping VM")
		self.server.vm.stop()
		
		# Traffic Control and Firewalls
		log(INFO, "stopping traffic control")
		self.server.traffic.stop_control()
		log(INFO, "stopping doors firewalls")
		self.server.doors.firewall_down()

		return True



	def restart(self, client, regen=False):
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



	def status(self, client):
		res = {}

		# VM
		vm_pid = self.server.vm.pid()
		res["running"] = vm_pid is not None
		if vm_pid is not None:
			res["vm_pid"] = vm_pid
		
		# Cowrie
		res["cowrie_instances"] = self.server.cowrie.running_cowries()
		
		# Configuration
		res["nb_devs"] = len(self.server.edit_config["device"])
		res["nb_doors"] = len(self.server.edit_config["door"])

		return res
