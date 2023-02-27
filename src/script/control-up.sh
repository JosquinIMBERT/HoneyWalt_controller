#!/bin/bash

#######################
###      INPUT      ###
#######################

if [[ $# != 5 ]]; then
	echo "Usage: $0 <dev> <addr> <latency> <throughput> <ports>"
	echo -e "\tdev: the device (network interface)"
	echo -e "\taddr: the address of the controller on the DMZ side"
	echo -e "\tlatency: latency to which the traffic should be limited on the given ports"
	echo -e "\tthroughput: throughput to which the traffic should be limited on the given ports"
	echo -e "\tports: the ports on which the traffic should be limited"
	exit 1
fi



#######################
###    Variables    ###
#######################

					#Examples of values
dev=$1				#"tap-out"
addr_dmz_side=$2	#"10.0.0.1"
latency=$3			#"3000ms"
throughput=$4		#"5kbit"
ports=$5			#"6000,6001"

port_min=$(echo $ports | cut -d"," -f1)
port_max=$(echo $ports | rev | cut -d"," -f1 | rev)

if [ "$port_min" = "$port_max" ]; then
	port_range=$port_min
else
	port_range="$port_min:$port_max"
fi



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



######################
###    FIREWALL    ###
######################

iptables -A PREROUTING -t mangle -p udp -d $addr_dmz_side --dport $port_range -j ACCEPT
iptables -A PREROUTING -t mangle -p tcp	-m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A PREROUTING -t mangle -d 127.0.0.1 -i lo -j ACCEPT
iptables -t mangle -P PREROUTING DROP



#######################
### TRAFFIC CONTROL ###
#######################

# Source: https://stackoverflow.com/questions/40196730/simulate-network-latency-on-specific-port-using-tc

if [ "$(tc qdisc show dev $dev root | grep pfifo_fast)" = "" ]; then
	echo -n "There is already a qdisc. Deleting it ... " && \
		tc qdisc delete dev $dev root && \
		echo "done." || echo "failed."
fi
echo -n "Adding new root qdisc ... " && \
	tc qdisc add dev $dev root handle 1:0 prio priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 && \
	echo "done." || echo "failed."

# METRICS:
# delay = latency (latence)
# rate = throughput (débit)
echo -n "Adding netem qdisc ... " && \
	tc qdisc add dev $dev parent 1:2 handle 20: netem delay $latency rate $throughput && \
	echo "done." || echo "failed."

echo -n "Adding filters ..."
for port in $(echo $ports | tr "," " "); do
	tc filter add dev $dev parent 1:0 protocol ip u32 match ip sport $port 0xffff flowid 1:2
done
echo "done."