import sys

def init(controller_server, conf, vm_priv, vm_pub, door_priv, door_pub):
	# Ports
	global LISTEN_PORTS, BACKEND_PORTS, SOCKET_PORTS
	global WIREGUARD_PORTS, EXPOSE_PORTS, WG_TCP_PORT
	global WG_UDP_PORT

	# IP
	global VM_IP, CONTROL_IP, IP_FOR_DMZ

	# Keys
	global VM_PRIV_KEY, VM_PUB_KEY, DOOR_PRIV_KEY, DOOR_PUB_KEY

	# Socket
	global VM_SOCK

	# Config
	global CONFIG

	# Server
	global SERVER
	
	LISTEN_PORTS=2000
	BACKEND_PORTS=3000
	SOCKET_PORTS=4000
	WIREGUARD_PORTS=6000
	EXPOSE_PORTS=7000
	WG_UDP_PORT=51820
	WG_TCP_PORT=51819

	VM_IP = "10.0.0.2"
	IP_FOR_DMZ = "10.0.0.1"
	CONTROL_IP = "127.0.0.1"

	VM_PRIV_KEY=vm_priv
	VM_PUB_KEY=vm_pub
	DOOR_PRIV_KEY=door_priv
	DOOR_PUB_KEY=door_pub

	VM_SOCK = None

	CONFIG = conf

	SERVER = controller_server

