# Device

## Description

The devices are the machines actually exposed to the attackers.
They usually have weak security with default usernames and passwords, ssh with password allowed for root, etc.

They are all connected to the same LAN: the Walt network. For this reason, HoneyWalt is not only a honeypot but also a honeynet: it is a network of honeypots that can attack each other.

## Configuration

A device is configured with:

- A name,
- A mac address,
- An image name.

When a new device is plugged to the honeypot, it should also be added to the configuration.
The image needs to be already added to the configuration.

A commit is needed so the newly plugged device is renamed and actually used.