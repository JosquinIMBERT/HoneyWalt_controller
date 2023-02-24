# HoneyWalt

## Description

HoneyWalt is a scalable, manageable, reproducible and realistic honeypot.
It is based on real devices that can be plugged directly to the honeypot.

HoneyWalt was built with [Walt][2]: a plateform for network experiments that allows us to get quickly rid of the attackers modifications from the devices.

## Configuration

The architecture of HoneyWalt is mainly based on four elements:

- Doors: the entry points of the honeypot.
The doors are servers with public IPs.
They redirect their port 22 (ssh) to the controller's [cowrie][1] processes.
Run **`python3 honeywalt.py door help`** for more information.
- Controller: the central point of the honeypot.
It is in charge of controlling the attacker's traffic (limit throughput/latency), accepting and redirecting the connections (cowrie) and gathering some logs.
Run **`python3 honeywalt.py controller help`** for more information.
- Virtual Machine (VM): the entry point of the demilitarized zone (the zone that can be attacked).
It runs the Walt server software, it redirects the connections from cowrie (on the controller) to the devices and it redirects the outgoing connections to the door with [wireguard][3] tunnels.
- Devices: the machines that are actually exposed.
They have a weak security (default usernames and passwords, ssh with password allowed for root) and are all connected to the same LAN (the Walt network).
Run **`python3 honeywalt.py device help`** for more information.

When using HoneyWalt, you also need to know about the OS images - called Walt images - deployed by the Walt server on the devices.
You can choose which image you want to deploy on each device.
Run **`python3 honeywalt.py image help`** for more information.

## State

HoneyWalt can be managed with the following commands:

- **`python3 honeywalt.py start`**: start the honeypot
- **`python3 honeywalt.py commit`**: commit the new configuration of the honeypot
- **`python3 honeywalt.py stop`**: stop the honeypot
- **`python3 honeywalt.py status`**: get some information about the honeypot status

## References

- Cowrie: https://github.com/cowrie/cowrie
- Walt: https://github.com/drakkar-lig/walt-python-packages
- Wireguard: https://www.wireguard.com/

[1]: https://github.com/cowrie/cowrie
[2]: https://github.com/drakkar-lig/walt-python-packages
[3]: https://www.wireguard.com/