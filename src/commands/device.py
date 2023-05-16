# External
import os, re, sys

# Internal
import glob
from common.utils.logs import *
from common.utils.misc import *


def add(client, name, mac, image, ports=[]):
	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if regex.match(image):
		log(WARNING, image+" seem to be a cloneable image link. Extracting short name")
		image = extract_short_name(image)

	if find(glob.CONFIG["device"], name, "node") is not None or \
	   find(glob.CONFIG["device"], mac, "mac") is not None:
		client.log(ERROR, "device already exists")
		return None
	
	if find(glob.CONFIG["image"], image, "short_name") is None:
		client.log(ERROR, "image not found")
		return None

	# Compute door ID
	if len(glob.CONFIG["device"]) == 0:
		dev_id = 0
	else:
		ids = [d["id"] for d in glob.CONFIG["device"]]
		dev_id = min(set(range(0, max(ids)+1)) - set(ids))

	new_dev = {
		"node":name,
		"image":image,
		"mac":mac,
		"ports":ports,
		"id": dev_id
	}
	glob.CONFIG["device"] += [ new_dev ]
	glob.CONFIG["need_commit"] = "True"

	return True


def chg(client, name, new_name=None, new_image=None, new_ports=None):
	if new_image:
		regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
		if regex.match(new_image):
			log(WARNING, new_image+" seem to be a cloneable image link. Extracting short name")
			new_image = extract_short_name(new_image)

	device = find(glob.CONFIG["device"], name, "node")
	if device is None:
		client.log(ERROR, "device not found")
		return None

	if new_name is not None:
		if find(glob.CONFIG["device"], new_name, "node") is not None:
			client.log(ERROR, "the new name for the device is already taken")
			return None
		device["node"] = new_name

	if new_image is not None:
		if find(glob.CONFIG["image"], new_image, "name") is None:
			client.log(ERROR, "image not found")
			return None
		device["image"] = new_image

	if new_ports is not None:
		device["ports"] = new_ports

	glob.CONFIG["need_commit"] = "True"

	return True


def delete(client, name):
	dev_id = find_id(glob.CONFIG["device"], name, "node")
	if dev_id == -1:
		client.log(ERROR, "unable to find device "+name)
		return None

	door = find(glob.CONFIG["door"], glob.CONFIG["device"][dev_id]["node"], "dev")
	if door is not None:
		client.log(ERROR, "door "+door["host"]+" uses device "+name)
		return None

	del glob.CONFIG["device"][dev_id]
	glob.CONFIG["need_commit"] = "True"

	return True


def show(client):
	return glob.CONFIG["device"]
