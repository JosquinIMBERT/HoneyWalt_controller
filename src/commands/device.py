# External
import os, re, sys

# Internal
import glob
from utils.logs import *


def add(name, mac, image, ports=[]):
	res={"success":True}

	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if regex.match(image):
		log(WARNING, image+" seem to be a cloneable image link. Extracting short name")
		image = extract_short_name(image)

	if find(glob.CONFIG["device"], name, "node") is not None or \
	   find(glob.CONFIG["device"], mac_addr, "mac") is not None:
		res["success"] = False
		res["msg"] = "device already exists"
		return res
	
	if find(glob.CONFIG["image"], image, "short_name") is None:
		res["success"] = False
		res["msg"] = "image not found"
		return res

	# Compute door ID
	if len(glob.CONFIG["device"]) == 0:
		dev_id = 0
	else:
		ids = [d["id"] for d in glob.CONFIG["device"]]
		dev_id = min(set(range(0, max(ids)+1)) - set(ids))

	new_dev = {
		"node":name,
		"image":image,
		"mac":mac_addr,
		"ports":ports,
		"id": dev_id
	}
	glob.CONFIG["device"] += [ new_dev ]

	return res


def chg(name, new_name=None, new_image=None, new_ports=None):
	res={"success":True}

	if new_image:
		regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
		if regex.match(new_image):
			log(WARNING, new_image+" seem to be a cloneable image link. Extracting short name")
			new_image = extract_short_name(new_image)

	device = find(glob.CONFIG["device"], name, "node")
	if device is None:
		res["success"] = False
		res["msg"] = "device not found"
		return res

	if new_name is not None:
		if find(glob.CONFIG["device"], new_name, "node") is not None:
			res["success"] = False
			res["msg"] = "the new name for the device is already taken"
			return res
		device["node"] = new_name

	if new_image is not None:
		if find(glob.CONFIG["image"], new_image, "name") is None:
			res["success"] = False
			res["msg"] = "image not found"
			return res
		device["image"] = new_image

	if new_ports is not None:
		device["ports"] = new_ports

	return res


def delete(name):
	res={"success":True}

	dev_id = find_id(glob.CONFIG["device"], name, "node")
	if dev_id == -1:
		res["success"] = False
		res["msg"] = "unable to find device "+name
		return res

	door = find(glob.CONFIG["door"], glob.CONFIG["device"][dev_id]["node"], "dev")
	if door is not None:
		res["success"] = False
		res["msg"] = "door "+door["host"]+" uses device "+name
		return res

	del glob.CONFIG["device"][dev_id]

	return res


def show():
	res={"success":True}
	res["answer"] = glob.CONFIG["device"]
	return res
