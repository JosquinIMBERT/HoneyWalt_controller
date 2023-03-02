# External
import os, sys

# Internal
import glob
from common.utils.misc import *


def add(ip, dev):
	res={"success":True}

	# Check device (the device should be registered first)
	device = find(glob.CONFIG["device"], dev, "node")
	if device is None:
		res["success"] = False
		res["error"] = ["device not found"]
		return res

	# Check door doesn't exist
	door = find(glob.CONFIG["door"], ip, "host")
	if door is not None:
		res["success"] = False
		res["error"] = ["door already exists"]
		return res

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

	with open(glob.DOOR_PUB_KEY) as file:
		key = file.read()
		res["answer"] = {"key":key}
	return res


def chg(ip, new_ip=None, new_dev=None):
	res={"success":True}

	if new_ip is None and new_dev is None:
		res["success"] = False
		res["error"] = ["no new value was given"]
		return res

	# Find the door
	door = find(glob.CONFIG["door"], ip, "host")
	if door is None:
		res["success"] = False
		res["error"] = ["door not found"]
		return res

	# Update the fields
	if new_ip is not None:
		door["host"] = new_ip
	if new_dev is not None:
		door["dev"] = new_dev

	# Show instructions
	if new_ip is not None:
		with open(glob.DOOR_PUB_KEY) as file:
			key = file.read()
			res["answer"] = {"key":key}
		return res

	return res


def delete(ip):
	res={"success":True}

	# Find the door
	door = find_id(glob.CONFIG["door"], ip, "host")
	if door == -1:
		res["success"] = False
		res["error"] = ["door not found"]
		return res

	del glob.CONFIG["door"][door]

	return res


def show():
	res={"success":True}
	res["answer"] = glob.CONFIG["door"]
	return res