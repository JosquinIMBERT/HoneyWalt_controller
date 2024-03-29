# External
import json, os, sys, time

# Internal
from config import *
from common.utils.logs import *
from common.utils.misc import *
from common.utils.rpc import FakeClient


class StateManager:
	def __init__(self, server):
		self.server = server

	def __del__(self):
		pass



	# Start HoneyWalt
	def start(self, client=FakeClient()):
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
		# CHECK KNOWN HOSTS #
		#####################

		fail = False
		for honeypot in self.server.run_config["honeypots"]:
			if not self.server.tunnels.verify_known_host(honeypot["door"]["host"]):
				client.log(ERROR, "please add "+str(honeypot["door"]["host"])+" to controller's ssh known hosts before to start")
				fail = True
		if fail: return None


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
				self.server.run_config["honeypots"][ident]["device"]["ip"] = ip["ip"]


		#####################
		# START SSH TUNNELS #
		#####################
		
		# Start SSH tunnels for cowrie traffic
		log(INFO, "starting tunnels for attackers connections")
		self.server.tunnels.start_ssh()


		#####################
		#	  FIREWALL		#
		#####################

		# Start doors firewalls
		log(INFO, "starting doors firewalls")
		self.server.doors.firewall_up()

		# Start VM Firewall
		log(INFO, "starting VM firewall")
		self.server.vm.firewall_up()

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
		self.server.doors.shaper_up()


		#####################
		#  TRAFFIC CONTROL  #
		#####################

		# Start traffic control
		log(INFO, "starting traffic control")
		self.server.traffic.start_control()


		#####################
		#		EXPOSE		#
		#####################

		# Start cowrie
		log(INFO, "starting cowrie")
		self.server.doors.cowrie_start()

		# Start to expose other ports
		log(INFO, "starting exposed ports tunnels")
		self.server.tunnels.start_other()

		return True



	# Commit some persistent information on the VM so it is taken
	# into acount on the next boot
	def commit(self, regen=True, force=False, client=FakeClient()):
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
		self.server.doors.reload(self.server.edit_config, set_config=True)

		if regen:
			log(INFO, "generating cowrie configurations")
			self.server.doors.cowrie_configure()

		log(INFO, "generating doors wireguard keys")
		self.server.doors.wg_keygen()

		# Format door and device data for VM
		honeypots = []
		for honeypot in self.server.edit_config["honeypots"]:
			honeypots += [{
				"id" : honeypot["id"],
				"door" : {
					"pubkey" : honeypot["door"]["pubkey"]
				},
				"device" : {
					"name" : honeypot["device"]["name"],
					"mac"  : honeypot["device"]["mac"]
				},
				"image" : {
					"name"       : honeypot["image"]["name"],
					"short_name" : honeypot["image"]["short_name"]
				},
				"credentials" : {
					"user" : honeypot["credentials"]["user"],
					"pass" : honeypot["credentials"]["pass"],
				}
			}]

		log(INFO, "starting VM")
		self.server.vm.start(1)
		log(INFO, "sending phase to VM")
		self.server.vm.send_phase()
		log(INFO, "sending honeypots to VM")
		self.server.vm.send_honeypots(json.dumps(honeypots))
		log(INFO, "generating VM wireguard keys")
		vm_keys = self.server.vm.wg_keygen()

		# Adding wireguard public keys to devices in config
		if vm_keys and len(vm_keys)==len(self.server.edit_config["honeypots"]):
			for data in vm_keys: #<id,pubkey>
				if data["id"] < len(self.server.edit_config["honeypots"]):
					self.server.edit_config["honeypots"][data["id"]]["device"]["pubkey"] = data["pubkey"]
		else:
			log(ERROR, "the VM did not send any wireguard keys")
			return False

		log(INFO, "commit on VM")
		self.server.vm.commit()
		log(INFO, "commit on doors")
		self.server.doors.commit()

		log(INFO, "updating local configuration file")
		set_conf(self.server.edit_config)
		self.server.need_commit = False

		log(INFO, "stopping VM")
		self.server.vm.stop()

		return True



	def stop(self, client=FakeClient()):
		# Tunnels and Cowrie
		log(INFO, "stopping tunnels for other exposed ports")
		self.server.tunnels.stop_other()
		log(INFO, "stopping cowrie")
		self.server.doors.cowrie_stop()
		log(INFO, "stopping tunnels for attackers connections")
		self.server.tunnels.stop_ssh()
		
		# Traffic Shaper
		log(INFO, "stopping traffic shapers")
		self.server.doors.shaper_down()
		
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
		log(INFO, "stopping VM firewall")
		self.server.vm.firewall_down()

		return True



	def restart(self, regen=False, client=FakeClient()):
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



	def status(self, client=FakeClient()):
		res = {}

		# VM
		vm_pid = self.server.vm.pid()
		res["running"] = vm_pid is not None
		if vm_pid is not None:
			res["vm_pid"] = vm_pid
		
		# Cowrie
		res["cowrie_instances"] = self.server.doors.cowrie_running()
		
		# Configuration
		res["nb_honeypots"] = len(self.server.edit_config["honeypots"])

		return res
