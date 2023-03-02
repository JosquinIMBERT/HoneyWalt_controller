import sys

def init(controller_server, conf, vm_priv, vm_pub, door_priv, door_pub):
	# Keys
	global VM_PRIV_KEY, VM_PUB_KEY, DOOR_PRIV_KEY, DOOR_PUB_KEY

	# Config
	global CONFIG, RUN_CONFIG

	# Server
	global SERVER

	VM_PRIV_KEY=vm_priv
	VM_PUB_KEY=vm_pub
	DOOR_PRIV_KEY=door_priv
	DOOR_PUB_KEY=door_pub

	CONFIG = conf
	RUN_CONFIG = conf

	SERVER = controller_server
