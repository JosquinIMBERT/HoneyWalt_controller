# Image

## Description

The devices will boot a Walt OS image.
You need to provide a cloneable Walt image link with the following format:

> (walt|docker|hub):<user>/<image_name>[:<tag>]

The image is also associated with a username and password.
These allow cowrie to connect to the device and to proxy the attacker's connection their.

The commit operation will clone the images on the VM.

For now, we don't automatically add the user with his password to the image so you need to add him yourself.