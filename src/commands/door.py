# External
import os, sys

# Internal
import glob
from common.utils.logs import *
from common.utils.misc import *


def add(client, ip, dev):
	# Check device (the device should be registered first)
	device = find(glob.CONFIG["device"], dev, "node")
	if device is None:
		client.log(ERROR, "device not found")
		return None

	# Check door doesn't exist
	door = find(glob.CONFIG["door"], ip, "host")
	if door is not None:
		client.log(ERROR, "door already exists")
		return None

	# Compute door ID
	if len(glob.CONFIG["door"]) == 0:
		door_id = 0
	else:
		ids = [d["id"] for d in glob.CONFIG["door"]]
		door_id = min(set(range(0, max(ids)+1)) - set(ids))

	# Add the door
	new_door = {
		"host":ip,
		"realssh":1312,
		"dev":dev,
		"id":door_id
	}
	glob.CONFIG["door"] += [ new_door ]
	glob.CONFIG["need_commit"] = "True"

	with open(glob.DOOR_PUB_KEY) as file:
		key = file.read()
		return key
	
	return True


def chg(client, ip, new_ip=None, new_dev=None):
	if new_ip is None and new_dev is None:
		client.log(ERROR, "no new value was given")
		return None

	# Find the door
	door = find(glob.CONFIG["door"], ip, "host")
	if door is None:
		client.log(ERROR, "door not found")
		return None

	# Update the fields
	if new_ip is not None:
		door["host"] = new_ip
	if new_dev is not None:
		door["dev"] = new_dev

	if new_ip is not None or new_dev is not None:
		glob.CONFIG["need_commit"] = "True"

	# Show instructions
	if new_ip is not None:
		with open(glob.DOOR_PUB_KEY) as file:
			key = file.read()
			return key

	return True


def delete(client, ip):
	# Find the door
	door = find_id(glob.CONFIG["door"], ip, "host")
	if door == -1:
		client.log(ERROR, "door not found")
		return None

	del glob.CONFIG["door"][door]
	glob.CONFIG["need_commit"] = "True"

	return True


def show(client):
	return glob.CONFIG["door"]