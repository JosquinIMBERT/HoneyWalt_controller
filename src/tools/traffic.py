# External
import argparse, os, select, socket, sys, threading, time

# Internal
from common.utils.files import *
from common.utils.logs import *
import common.utils.settings as settings

class TrafficController:
	def __init__(self):
		log(INFO, "TrafficController.__init__: creating the TrafficController")
		self.traffic_shaper = TrafficShaper()
		self.traffic_shaper.tcp_host = "0.0.0.0"
		self.traffic_shaper.tcp_port = settings.get("WG_TCP_PORT")

	def __del__(self):
		pass

	def init_run(self):
		delete(to_root_path("run/traffic-shaper"), suffix=".pid")

	def traffic_shaper_up(self):
		self.traffic_shaper.start()

	def traffic_shaper_down(self):
		self.traffic_shaper.stop()

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



class TrafficShaper:
	def __init__(self):
		self.keep_running = False
		self.udp_lo_host = "127.0.0.1"
		self.udp_lo_port = 1111
		self.tcp_host = "192.168.100.1"
		self.tcp_port = 1110
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
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
			udp_sock.bind((self.udp_lo_host, self.udp_lo_port))
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
				i=0
				while i<6: # ~30sec
					try:
						tcp_sock.connect((self.tcp_host, self.tcp_port))
					except:
						time.sleep(5)
					else:
						break
					i+=1
				if i>=6:
					print("[ERROR] traffic-shaper.controller_tunnel: failed to connect to the door")
					sys.exit(1)

				sel_list = [udp_sock, tcp_sock]
				try:
					while self.keep_running:
						rready, _, _ = select.select(sel_list, [], [])
						for ready in rready:
							if ready is udp_sock:
								msg, addr = udp_sock.recvfrom(1024)
								if not msg: break
								self.udp_host, self.udp_port = addr
								msg = encode_len(msg) + msg
								tcp_sock.sendall(msg)
							else:
								msg = tcp_sock.recv(1024)
								if not msg: break
								if self.udp_host is not None and self.udp_port is not None:
									while msg:
										blen, msg = msg[0:2], msg[2:]
										length = decode_len(blen)
										to_send, msg = msg[:length], msg[length:]
										udp_sock.sendto(to_send, (self.udp_host, self.udp_port))
				except ConnectionResetError:
					print("Connection Reset")

	def start(self):
		self.keep_running = True
		self.thread = threading.Thread(target=self.controller_tunnel)
		self.thread.start()

	def stop(self):
		self.keep_running = False
		self.thread.join()
		self.udp_host = None
		self.udp_port = None