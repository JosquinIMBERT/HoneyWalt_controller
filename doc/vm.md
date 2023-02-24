# Virtual Machine

## Description

The virtual machine (VM) hosts the Walt server software that manages the devices.
It is considered to be in the demilitarized zone (DMZ - zone where any machine could potentially be infected).

## Phases

The VM can be started in two different phases:

1) The phase 1 is the commit phase. The VM is booted without the snapshot mode. Consequently, the modifications to the file system are persistent. During this phase, we don't expose the honeypot to the attackers (all tunnels are off). The commit phase will clone the images, add the users to the images (TBD), and rename the devices.

2) The phase 2 is the production (run) phase. The VM is booted with the snapshot mode which means that the modifications are volatile. This phase corresponds to when the honeypot is running. Consequently, the VM is exposed and unsafe (an attacker could enter from the WalT network).