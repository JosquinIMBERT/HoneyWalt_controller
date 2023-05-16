# External
import os, re, sys

# Internal
import glob


def match_value(val, unit):
	regex = re.compile("\A\d+(\.\d*)?"+str(unit)+"\Z")
	return regex.match(val) is not None


def set(client, throughput=None, latency=None):
	if throughput is None and latency is None:
		client.log(ERROR, "no new value was given")
		return None

	if throughput is not None:
		rate_unit = "[kmgt]?(bps|bit)"
		if match_value(throughput, rate_unit):
			glob.CONFIG["controller"]["throughput"] = throughput
		else:
			client.log(ERROR, "invalid throughput")
			return None

	if latency is not None:
		time_unit = "[mu]?(s|sec|secs)"
		if match_value(latency, time_unit):
			glob.CONFIG["controller"]["latency"] = latency
		else:
			client.log(ERROR, "invalid latency")
			return None

	glob.CONFIG["need_commit"] = "True"

	return True


def show(client):
	return glob.CONFIG["controller"]