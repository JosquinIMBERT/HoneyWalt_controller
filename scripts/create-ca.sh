#!/bin/bash

dir=$(realpath ${HONEYWALT_CONTROLLER_HOME}/var/key/)

if [ ! -d "${dir}" ]; then
	echo "Error: HoneyWalt_controller does not seem to be installed on this machine."
	exit 1
fi

mkdir ${dir}/ca
cd ${dir}/ca/
easyrsa init-pki
easyrsa build-ca
