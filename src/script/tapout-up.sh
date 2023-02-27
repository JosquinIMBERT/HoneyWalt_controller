#!/bin/bash

tap=$1
host_addr="10.0.0.1/30"
wan="enp1s0"

if [ "$(ip link show | grep "$tap")" = "" ]; then
	echo -n "Adding tap interface... " && \
		ip tuntap add $tap mode tap && \
		echo "done." || \
		echo "failed."
fi
echo -n "Setting tap address... " && \
	ip addr add dev $tap $host_addr && \
	echo "done." || \
	echo "failed."
echo -n "Setting tap up... " && \
	ip link set up dev $tap && \
	echo "done." || \
	echo "failed."

echo -n "Setting NAT rule... " && \
	iptables -t nat -A POSTROUTING -o $wan -j MASQUERADE && \
	echo "done." || \
	echo "failed."
