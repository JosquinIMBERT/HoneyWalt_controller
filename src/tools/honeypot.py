# External
import re

# Internal


# Common
from common.utils.logs import *
from common.utils.misc import *
from common.utils.rpc import FakeClient

class HoneypotManager:
	def __init__(self, server):
		self.server = server

	def __del__(self):
		pass



	def add(self, door, device_name, device_mac,
		image, username=None, password=None,
		ports=None, client=FakeClient()):
		
		# Checking Image
		regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
		if not regex.match(image):
			client.log(ERROR, image+" is not a Walt image clonable link")
			return None
		image_short = extract_short_name(image)

		# Checking device
		if find(self.server.edit_config, device_name, ["device", "name"]) is not None:
			client.log(ERROR, "another honeypot is already using this device name")
			return None
		if find(self.server.edit_config, device_mac,  ["device", "mac"] ) is not None:
			client.log(ERROR, "the device with this mac address is already in use for another honeypot")
			return None

		# Checking door
		if find(self.server.edit_config, door, ["door", "host"]) is not None:
			client.log(ERROR, "this door is already in use for an other honeypot")

		# Processing username and password
		if username is None:
			log(INFO, "No username was given. Using username: root, password: root")
			username = "root"
			password = "root"
		elif password is None:
			log(INFO, "No password was given. Using password: "+username)
			password = username
		
		new_honeypot = {
			"id": 0, # We will set the honetid right after
			"door": {"host": door},
			"device": {
				"name": device_name,
				"mac": device_mac
			},
			"image": {
				"name": image,
				"short_name": image_short
			},
			"credentials": {
				"user": username,
				"pass": password
			},
			"ports": [] if ports is None else ports
		}

		self.server.edit_config["honeypot"] += [new_honeypot]

		cpt = 0
		for honeypot in self.server.edit_config:
			honeypot["id"] = cpt
			cpt += 1

		self.server.need_commit = True

		return cpt



	def change(self, ident, door=None, device_name=None,
		device_mac=None, image=None, username=None,
		password=None, ports=None, client=FakeClient()):

		honeypot = find(self.server.edit_config, ident, "id")
		if honeypot is None:
			client.log(ERROR, "the selected honeypot was not found")
			return None

		# Image
		if image is not None:
			regex = re.compile(r'^(walt|docker|hub):[a-z0-9\-]+/[a-z0-9\-]+(:[a-z0-9\-]+)?$')
			if not regex.match(image):
				client.log(ERROR, image+" is not a Walt image clonable link")
			else:
				image_short = extract_short_name(image)
				honeypot["image"]["name"] = image
				honeypot["image"]["short_name"] = image_short

		# Device
		if device_name is not None:
			name_ok = True
			for h in self.server.edit_config:
				if h["id"] != ident and h["device"]["name"] == device_name:
					client.log(ERROR, "another honeypot is already using this device name")
					name_ok = False
					break
			if name_ok: honeypot["device"]["name"] = device_name
		if device_mac is not None:
			mac_ok = True
			for h in self.server.edit_config:
				if h["id"] != ident and h["device"]["mac"] == device_mac:
					client.log(ERROR, "the device with this mac address is already in use for another honeypot")
					mac_ok = False
					break
			if mac_ok: honeypot["device"]["mac"] = device_mac

		# Door
		if door is not None:
			door_ok = True
			for h in self.server.edit_config:
				if h["id"] != ident and h["door"]["host"] == door:
					client.log(ERROR, "the door is already in use for another honeypot")
					door_ok = False
					break
			if door_ok: honeypot["door"]["host"] = door

		# Credentials
		if username is not None: honeypot["credentials"]["user"] = username
		if password is not None: honeypot["credentials"]["pass"] = password

		# Ports
		if ports is not None: honeypot["ports"] = ports

		self.server.need_commit = True



	def delete(self, ident, client=FakeClient()):
		if len(self.server.edit_config["honeypots"]) <= ident:
			client.log(ERROR, "invalid honeypoy identifier")
			return None
		
		del self.server.edit_config["honeypots"][ident]
		
		self.server.need_commit = True



	def show(self, client=FakeClient()):
		return self.server.edit_config["honeypots"]
