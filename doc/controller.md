# Controller

## Description

The controller is the central point of HoneyWalt.
It controls the traffic of the attackers, accepts the ssh connections and redirect them to the devices.
It is also in charge of hosting a Virtual Machine (VM) that runs the Walt server.

## Parameters

Two parameters can be defined on the controller:

- The throughput: alterates the throughput of the attacker's outgoing connections
- The latency: change the latency of the outgoing connections

## Units

The units are the same as in the tc linux utility.

For the throughput, the following rate units are accepted:

- bit: Bits per second
- kbit: Kilobits per second
- mbit: Megabits per second
- gbit: Gigabits per second
- tbit: Terabits per second
- bps: Bytes per second
- kbps: Kilobytes per second
- mbps: Megabytes per second
- gbps: Gigabytes per second
- tbps: Terabytes per second

For example, set the throughput to 10 Megabits per seconds:

```bash
python3 honeywalt.py controller set --throughput 10mbit
```

For the latency, the following time units are accepted:

- s/sec/secs: Seconds
- ms/msec/msecs: Milliseconds
- us/usec/usecs: Microseconds

For example, set the latency to 50 milliseconds:

```bash
python3 honeywalt.py controller set --latency 50msec
```