# External
import argparse, os, select, socket, sys, threading, time

# Internal
from common.utils.logs import *
from common.utils.shaper import Shaper
import glob

# The Traffic Shaper is used to transorm wireguard UDP traffic into TCP traffic to bypass internet firewalls.
# For the sake of simplicity and since we don't care about performance (bad performance on the attacker's
# traffic is actually a good feature for us), we don't create a new TCP connection.
# Instead, we use the existing RPyC connection and forward the UDP packets with an exposed method.

class ControllerShaper(Shaper):
	def __init__(self, udp_listen_port, timeout=60):
		super().__init__(name="CTRL", timeout=timeout)

		# Local UDP host and port
		self.udp_listen_host = "0.0.0.0"
		self.udp_listen_port = udp_listen_port

	def prepare(self):
		self.sock.bind((self.udp_listen_host, self.udp_listen_port))
