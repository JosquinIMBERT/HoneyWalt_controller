# External
import argparse, os, select, socket, sys, threading, time

# TODO: Use python-iptables and shapy (pip3 install --upgrade python-iptables && pip3 install shapy)

# Internal
from common.utils.files import *
from common.utils.logs import *
from common.utils.system import *

class Traffic:

	LATENCY = "50usec"
	THROUGHPUT = "10mbit"
	WIREGUARD_PORTS = 6000
	INTERNAL_IP = "10.0.0.1"

	def __init__(self, server, ip_white_list=[]):
		self.server = server
		self.ip_white_list = ip_white_list

	def __del__(self):
		pass

	def start_control(self):
		dev = "tap-out"
		latency = Traffic.LATENCY
		throughput = Traffic.THROUGHPUT
		ports = ",".join([str(Traffic.WIREGUARD_PORTS+honeypot["id"]) for honeypot in self.server.run_config["honeypots"]])
		white_list = ",".join(self.ip_white_list)

		prog = to_root_path("src/script/control-up.sh")
		args = dev+" "+Traffic.INTERNAL_IP+" "+latency+" "+throughput+" "+ports+" "+white_list
		command = prog+" "+args
		if not run(command):
			log(ERROR, "Traffic.start_control: failed to start traffic control")

	def stop_control(self):
		prog = to_root_path("src/script/control-down.sh")
		command = prog+" tap-out"
		if not run(command):
			log(ERROR,"Traffic.stop_control: failed to stop traffic control")
