# External
import os, re, sys

# Internal
import glob
from common.utils.logs import *
from common.utils.misc import *


def add(client, name, username="root", password="root"):
	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if not regex.match(name):
		client.log(ERROR, name+" is not a Walt image clonable link")
		return None
	short_name = extract_short_name(name)

	if find(glob.CONFIG["image"], name, "name") is not None:
		client.log(ERROR, "image already exists")
		return None

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
	glob.CONFIG["need_commit"] = "True"

	return True

def chg(client, name, username=None, password=None):
	if username is None and password is None:
		client.log(ERROR, "no new value was given")
		return None

	# Find image name type (cloneable or short)
	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if not regex.match(name):
		regex = re.compile(r'^[a-z0-9\-]+$')
		if not regex.match(name):
			client.log(ERROR, name+" is not a Walt image name nor a clonable link")
			return None
		else:
			field="short_name"
	else:
		field="name"

	# Find image
	image = find(glob.CONFIG["image"], name, field)
	if image is None:
		client.log(ERROR, "image not found")
		return None

	# Edit
	if username is not None:
		image["user"] = username
	if password is not None:
		image["pass"] = password

	glob.CONFIG["need_commit"] = "True"

	return True


def delete(client, name):
	# Find image name type (cloneable or short)
	regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
	if not regex.match(name):
		regex = re.compile(r'[a-z0-9\-]+')
		if not regex.match(name):
			client.log(ERROR, name+" is not a Walt image name nor a clonable link")
			return None
		else:
			field="short_name"
	else:
		field="name"

	# Find image
	img_id = find_id(glob.CONFIG["image"], name, field)
	if img_id == -1:
		client.log(ERROR, "unable to find image "+name)
		return None

	if field == "name":
		short_name = extract_short_name(name)
	else:
		short_name = name
	dev = find(glob.CONFIG["device"], short_name, "image")
	if dev is not None:
		client.log(ERROR, "device "+dev["node"]+" uses image "+name)
		return None

	del glob.CONFIG["image"][img_id]
	glob.CONFIG["need_commit"] = "True"

	return True


def show(client):
	return glob.CONFIG["image"]
