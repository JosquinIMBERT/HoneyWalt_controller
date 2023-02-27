# External
import os, re, sys, time

# Internal
import tools.vm as vm
from utils.logs import *
import glob

def shell():
	# if vm.state():
	# 	if vm.phase()!=1:
	# 		log(WARNING, "The VM seems to be exposed.\nBe careful with what you run, the attacker could have infected it.")
	# 	i=0
	# 	while i<24:
	# 		i+=1
	# 		try:
	# 			run("ssh root@"+settings.get("VM_IP")+" -i "+settings.get("VM_PRIV_KEY")+" 2>/dev/null", "")
	# 		except Exception:
	# 			if i==1:
	# 				print("Waiting for the VM to boot...")
	# 			time.sleep(5)
	# 		else:
	# 			break
	# 	if i>=24:
	# 		eprint("failed to connect to the vm")
	# else:
	# 	eprint("the VM is not running")
	pass

def start(phase):
	res={"success":True}

	if glob.SERVER.VM_CONTROLLER.pid() is not None:
		res["success"] = False
		res["msg"] = "the VM is already running"
		return res
	glob.SERVER.VM_CONTROLLER.start(phase)

	return res

def stop():
	res={"success":True}

	if glob.SERVER.VM_CONTROLLER.pid() is None:
		res["success"] = False
		res["msg"] = "the VM is already stopped"
		return res
	glob.SERVER.VM_CONTROLLER.stop()

	return res