# External
import os, re, sys, time

# Internal
sys.path[0] = os.path.join(os.environ["HONEYWALT_CONTROLLER_HOME"],"src/")
import tools.vm as vm
from utils import *
import glob

def shell():
	if vm.state():
		if vm.phase()!=1:
			log(glob.WARNING, "The VM seems to be exposed.\nBe careful with what you run, the attacker could have infected it.")
		i=0
		while i<24:
			i+=1
			try:
				run("ssh root@"+glob.VM_IP+" -i "+glob.VM_PRIV_KEY+" 2>/dev/null", "")
			except Exception:
				if i==1:
					print("Waiting for the VM to boot...")
				time.sleep(5)
			else:
				break
		if i>=24:
			eprint("failed to connect to the vm")
	else:
		eprint("the VM is not running")

def start(phase):
	if vm.state():
		eprint("the VM is already running")
	vm.start(phase)

def stop():
	if not vm.state():
		log(glob.WARNING, "the VM is already stopped")
	else:
		vm.stop()
