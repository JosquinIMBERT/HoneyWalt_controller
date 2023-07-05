#!/bin/bash

# Usage: stop.sh [pidfile]

HOME=$(realpath $(dirname $(dirname "$0")))
MAX_TIME=15 # seconds

if [[ $# -gt 0 ]]; then
	pidfile="$1"
else
	pidfile="${HOME}/var/honeywalt_controller.pid"
fi

if [ -f ${pidfile} ]; then
	pid=$(cat ${pidfile})
	if [[ "$pid" =~ ^[0-9]+$ ]]; then
		# Send SIGINT to the process
		kill -2 "$pid"

		# Wait for the process to be dead (at most MAX_TIME)
		cpt=0
		while kill -0 "$pid" 2>/dev/null; do
			if [[ $cpt -gt $MAX_TIME ]]; then break; fi
			sleep 1
			cpt=$((cpt+1))
		done
	else
		echo "The content of the pid file is invalid"
	fi
else
	echo "The pid file was not found"
fi