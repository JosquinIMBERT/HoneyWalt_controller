import json, shutil, sys
from os.path import exists

from utils.files import *
from utils.logs import *

def open_conf(file, write=False):
	if file is None:
		conf_file = to_root_path("etc/honeywalt.cfg")
	else:
		conf_file = file

	if not exists(conf_file):
		conf_dist_file = to_root_path("etc/honeywalt.cfg.dist")
		if not exists(conf_dist_file):
			eprint("The configuration file was not found.")
		shutil.copyfile(conf_dist_file, conf_file)
	if write:
		return open(conf_file, "w")
	else:
		return open(conf_file)

def get_conf(file=None):
	conf_file = open_conf(file)
	conf = json.load(conf_file)
	conf_file.close()
	return conf

def set_conf(conf, file=None, need_commit=True):
	conf["need_commit"] = str(need_commit)
	conf_file = open_conf(file, write=True)
	conf_file.write(json.dumps(conf, indent=4))
	conf_file.close()