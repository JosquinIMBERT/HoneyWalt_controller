#!/bin/bash

dir=$(realpath $(dirname $0))

sudo apt-get install easy-rsa
export PATH="$PATH:/usr/share/easy-rsa/"

# Create CA

${dir}/create-ca.sh

# Create Controller certificate

${dir}/create-controller-cert.sh

