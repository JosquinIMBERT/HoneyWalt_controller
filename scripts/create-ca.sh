#!/bin/bash

dir=$(realpath ${HONEYWALT_CONTROLLER_HOME}/var/key/)

export PATH="$PATH:/usr/share/easy-rsa/"
export EASYRSA_BATCH=1

if [ ! -d "${dir}" ]; then
	echo "Error: HoneyWalt_controller does not seem to be installed on this machine."
	exit 1
fi

mkdir -p ${dir}/ca
cd ${dir}/ca/
echo -n "Initializing CA's PKI..." && easyrsa init-pki >/dev/null 2>&1 && echo "done" || echo "failed"
echo -n "Building CA..." && easyrsa build-ca nopass >/dev/null 2>&1 && echo "done" || echo "failed"
