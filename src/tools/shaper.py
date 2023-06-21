# External
import argparse, os, select, socket, sys, threading, time

# TODO: Use python-iptables and shapy (pip3 install --upgrade python-iptables && pip3 install shapy)

if __name__ == "__main__":
	sys.path[0] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Internal
from common.utils.logs import *
from common.utils.shaper import Shaper
import glob

# The TrafficShaper is used to transorm wireguard UDP traffic into TCP traffic to bypass internet firewalls
# Messages sent over the TCP channel take the following shape:
#	- Datagram *length* encoded on two bytes
#	- Datagram content on *length* bytes
# The Wireguard Traffic comes from a given port (udp_listen_port)
# The TCP channel is opened with the door at (tcp_host:tcp_port)

class TrafficShaper:
	def __init__(self, tcp_host, tcp_port, udp_listen_port):
		self.keep_running = False
		self.udp_listen_host = "0.0.0.0"
		self.udp_listen_port = udp_listen_port
		self.tcp_host = tcp_host
		self.tcp_port = tcp_port
		self.udp_host = None
		self.udp_port = None

	def __del__(self):
		pass

	def encode_len(self, bytes_obj):
		return len(bytes_obj).to_bytes(2, "big")

	def decode_len(self, length):
		return int.from_bytes(length, "big")

	def controller_tunnel(self):
		# UDP Server + TCP client
		while self.keep_running:
			with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
				udp_sock.bind((self.udp_listen_host, self.udp_listen_port))
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
					try:
						tcp_sock.connect((self.tcp_host, self.tcp_port))
					except:
						log(DEBUG, "TrafficShaper.controller_tunnel: failed to connect to the door")
						time.sleep(5) # We wait 5 seconds before to retry
						continue

					sel_list = [udp_sock, tcp_sock]
					try:
						connected = True
						while self.keep_running and connected:
							rready, _, _ = select.select(sel_list, [], [], 5)
							for ready in rready:
								if ready is udp_sock:
									msg, addr = udp_sock.recvfrom(1024)
									if not msg:
										connected = False
										break
									self.udp_host, self.udp_port = addr
									msg = self.encode_len(msg) + msg
									tcp_sock.sendall(msg)
								elif ready is tcp_sock:
									msg = tcp_sock.recv(1024)
									if not msg:
										connected = False
										break
									if self.udp_host is not None and self.udp_port is not None:
										while msg:
											blen, msg = msg[0:2], msg[2:]
											length = self.decode_len(blen)
											to_send, msg = msg[:length], msg[length:]
											if self.udp_host is None or self.udp_port is None:
												log(ERROR, "TrafficShaper.controller_tunnel: Receiving external traffic before any outgoing wireguard traffic was observed")
												connected = False
												break
											udp_sock.sendto(to_send, (self.udp_host, self.udp_port))
								else:
									connected = False
									break
					except ConnectionResetError:
						log(WARNING, "TrafficShaper.controller_tunnel: Connection Reset")

	def start(self):
		self.keep_running = True
		self.thread = threading.Thread(target=self.controller_tunnel)
		self.thread.start()

	def stop(self):
		self.keep_running = False
		self.thread.join()
		self.udp_host = None
		self.udp_port = None

	def wait(self):
		self.thread.join()

class ControllerShaper(Shaper):
	def __init__(self, udp_listen_port, timeout=60):
		super().__init__(name="CTRL", timeout=timeout)

		# Local UDP host and port
		self.udp_listen_host = "0.0.0.0"
		self.udp_listen_port = udp_listen_port

	def prepare(self):
		self.sock.bind((self.udp_listen_host, self.udp_listen_port))

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Run the controller's TrafficShaper")
	parser.add_argument("-up", "--udp-port", nargs=1, help="UDP Port to listen on", default=[6000])
	parser.add_argument("-th", "--tcp-host", nargs=1, help="TCP Host to connect to",  default=["1.2.3.4"])
	parser.add_argument("-tp", "--tcp-port", nargs=1, help="TCP Port to connect to",  default=[51819])

	options = parser.parse_args()
	tcp_host = options.tcp_host[0]
	tcp_port = options.tcp_port[0]
	udp_listen_port = options.udp_port[0]

	ts = TrafficShaper(tcp_host, tcp_port, udp_listen_port)
	ts.start()
	ts.wait()
	del ts