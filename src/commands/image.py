# External
import os, re, sys

# Internal
import glob
from common.utils.logs import *
from common.utils.misc import *


def add(name, username="root", password="root"):
	res={"success":True}

	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if not regex.match(name):
		res["success"] = False
		res["msg"] = name+" is not a Walt image clonable link"
		return res
	short_name = extract_short_name(name)

	if find(glob.CONFIG["image"], name, "name") is not None:
		res["success"] = False
		res["msg"] = "image already exists"
		return res

	if username is None:
		log(INFO, "No username was given. Using username: root, password: root")
		username = "root"
		password = "root"
	elif password is None:
		log(INFO, "No password was given. Using password: "+username)
		password = username

	new_img = {
		"name":name,
		"short_name":short_name,
		"user":username,
		"pass":password
	}
	glob.CONFIG["image"] += [ new_img ]

	return res

def chg(name, username=None, password=None):
	res={"success":True}

	if username is None and password is None:
		res["success"] = False
		res["msg"] = "no new value was given"
		return res

	# Find image name type (cloneable or short)
	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if not regex.match(name):
		regex = re.compile(r'^[a-z0-9\-]+$')
		if not regex.match(name):
			res["success"] = False
			res["msg"] = name+" is not a Walt image name nor a clonable link"
			return res
		else:
			field="short_name"
	else:
		field="name"

	# Find image
	image = find(glob.CONFIG["image"], name, field)
	if image is None:
		res["success"] = False
		res["msg"] = "image not found"
		return res

	# Edit
	if username is not None:
		image["user"] = username
	if password is not None:
		image["pass"] = password

	return res


def delete(name):
	res={"success":True}

	# Find image name type (cloneable or short)
	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if not regex.match(name):
		regex = re.compile(r'[a-z0-9\-]+')
		if not regex.match(name):
			res["success"] = False
			res["msg"] = name+" is not a Walt image name nor a clonable link"
			return res
		else:
			field="short_name"
	else:
		field="name"

	# Find image
	img_id = find_id(glob.CONFIG["image"], name, field)
	if img_id == -1:
		res["success"] = False
		res["msg"] = "unable to find image "+name
		return res

	if field == "name":
		short_name = extract_short_name(name)
	else:
		short_name = name
	dev = find(glob.CONFIG["device"], short_name, "image")
	if dev is not None:
		res["success"] = False
		res["msg"] = "device "+dev["node"]+" uses image "+name
		return res

	del glob.CONFIG["image"][img_id]

	return res


def show():
	res={"success":True}
	res["answer"] = glob.CONFIG["image"]
	return res