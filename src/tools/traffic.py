# External
import argparse, os, select, socket, sys, threading, time

# TODO: Use python-iptables and shapy (pip3 install --upgrade python-iptables && pip3 install shapy)

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *
import common.utils.settings as settings
import glob

class TrafficController:
	def __init__(self):
		log(INFO, "TrafficController.__init__: creating the TrafficController")

	def __del__(self):
		pass

	def start_control(self):
		WIREGUARD_PORTS = settings.get("WIREGUARD_PORTS")
		IP_FOR_DMZ = settings.get("IP_FOR_DMZ")

		dev = "tap-out"
		latency = glob.RUN_CONFIG["controller"]["latency"]
		throughput = glob.RUN_CONFIG["controller"]["throughput"]
		ports = ",".join([str(WIREGUARD_PORTS+dev["id"]) for dev in glob.RUN_CONFIG["device"]])

		prog = to_root_path("src/script/control-up.sh")
		args = dev+" "+IP_FOR_DMZ+" "+latency+" "+throughput+" "+ports
		command = prog+" "+args
		if not run(command):
			log(ERROR, "TrafficController.start_control: failed to start traffic control")

	def stop_control(self):
		prog = to_root_path("src/script/control-down.sh")
		command = prog+" tap-out"
		if not run(command):
			log(ERROR,"TrafficController.stop_control: failed to stop traffic control")
