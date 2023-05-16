# External
import os, re, sys, time

# Internal
from common.utils.logs import *
import common.utils.settings as settings
import glob

def shell(client):
	if not glob.SERVER.VM_CONTROLLER.pid():
		client.log(ERROR, "the VM seems to be stopped")
		return None
	else:
		res = {}
		if glob.SERVER.VM_CONTROLLER.phase != 1:
			client.log(WARNING, "the VM is in run mode. Your modifications will be lost after reboot and an attacker could infect the VM")
		res["ip"] = settings.get("VM_IP")
		with open(glob.VM_PRIV_KEY, "r") as keyfile:
			res["key"] = keyfile.read()
		return res

def start(client, phase):
	if glob.SERVER.VM_CONTROLLER.pid() is not None:
		client.log(ERROR, "the VM is already running")
		return None
	glob.SERVER.VM_CONTROLLER.start(phase)

	return True

def stop(client):
	if glob.SERVER.VM_CONTROLLER.pid() is None:
		client.log(ERROR, "the VM is already stopped")
		return None
	glob.SERVER.VM_CONTROLLER.stop()

	return True