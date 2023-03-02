# External
import os, re, sys, time

# Internal
from common.utils.logs import *
import glob

def shell():
	if not glob.SERVER.VM_CONTROLLER.pid():
		return {"success": False, "error": ["the VM seems to be stopped"]}
	else:
		res = {"success": True, "answer": {}}
		if glob.SERVER.VM_CONTROLLER.phase != 1:
			res["warning"] = ["the VM is in run mode. Your modifications will be lost after reboot and an attacker could infect the VM"]
		res["answer"]["ip"] = settings.get("VM_IP")
		with open(glob.VM_PRIV_KEY, "r") as keyfile:
			res["answer"]["key"] = keyfile.read()
		return res

def start(phase):
	res={"success":True}

	if glob.SERVER.VM_CONTROLLER.pid() is not None:
		res["success"] = False
		res["error"] = ["the VM is already running"]
		return res
	glob.SERVER.VM_CONTROLLER.start(phase)

	return res

def stop():
	res={"success":True}

	if glob.SERVER.VM_CONTROLLER.pid() is None:
		res["success"] = False
		res["error"] = ["the VM is already stopped"]
		return res
	glob.SERVER.VM_CONTROLLER.stop()

	return res