#!/bin/bash

tap=$1
host_addr="10.0.0.1/30"
wan="enp1s0"

echo -n "Stopping NAT... " && \
	iptables -t nat -D POSTROUTING -o $wan -j MASQUERADE && \
	echo "done." || \
	echo "failed."

echo -n "Setting tap down... " && \
	ip link set down dev $tap && \
	echo "done." || \
	echo "failed."
echo -n "Deleting tap interface... " && \
	ip link delete $tap && \
	echo "done." || \
	echo "failed."
