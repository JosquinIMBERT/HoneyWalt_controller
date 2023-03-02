# External
import os, re, sys

# Internal
import glob


def match_value(val, unit):
	regex = re.compile("\A\d+(\.\d*)?"+str(unit)+"\Z")
	return regex.match(val) is not None


def set(throughput=None, latency=None):
	res={"success":True}

	if throughput is None and latency is None:
		res["success"] = False
		res["error"] = ["no new value was given"]
		return res

	if throughput is not None:
		rate_unit = "[kmgt]?(bps|bit)"
		if match_value(throughput, rate_unit):
			glob.CONFIG["controller"]["throughput"] = throughput
		else:
			res["success"] = False
			res["error"] = ["invalid throughput"]
			return res

	if latency is not None:
		time_unit = "[mu]?(s|sec|secs)"
		if match_value(latency, time_unit):
			glob.CONFIG["controller"]["latency"] = latency
		else:
			res["success"] = False
			res["error"] = ["invalid latency"]
			return res

	return res


def show():
	res={"success":True}
	res["answer"] = glob.CONFIG["controller"]
	return res