#!/bin/bash

#######################
###      INPUT      ###
#######################

if [[ $# != 1 ]]; then
	echo "Usage: $0 <dev>"
	echo -e "\tdev: the device (network interface)"
	exit 1
fi



#######################
###    VARIABLES    ###
#######################

dev=$1


#######################
###  Factory state  ###
#######################

iptables -F
iptables -F -t nat
iptables -F -t mangle
iptables -X

# FILTER
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# NAT
iptables -t nat -P PREROUTING ACCEPT
iptables -t nat -P INPUT ACCEPT
iptables -t nat -P OUTPUT ACCEPT
iptables -t nat -P POSTROUTING ACCEPT

# MANGLE
iptables -t mangle -P PREROUTING ACCEPT
iptables -t mangle -P INPUT ACCEPT
iptables -t mangle -P FORWARD ACCEPT
iptables -t mangle -P OUTPUT ACCEPT
iptables -t mangle -P POSTROUTING ACCEPT

# TC
if [ "$(tc qdisc show dev $dev root | grep pfifo_fast)" = "" ]; then
	tc qdisc delete dev $dev root
fi