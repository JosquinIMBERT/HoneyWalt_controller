#!/bin/bash

dir=$(realpath $(dirname $0))

apt-get install -y easy-rsa
export PATH="$PATH:/usr/share/easy-rsa/"
export EASYRSA_BATCH=1

# Create CA

${dir}/create-ca.sh

# Create Controller certificate

${dir}/create-controller-cert.sh

