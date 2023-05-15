#!/bin/bash

dir=$(realpath ${PWD})

usage() {
	echo "Usage: $0: <req-file> <client/server>"
}

if [ $# -ne 2 ] || [ ! -f "$1" ] || [[ "$2" != "client" && "$2" != "server" ]]; then
	usage
	exit 1
fi

file=$1
role=$2

shortname=$(echo $RANDOM | md5sum | head -c 20; echo;)

easyrsa import-req ${file} ${shortname}
easyrsa show-req ${shortname}
easyrsa sign-req ${role} ${shortname}
easyrsa show-cert ${shortname}

res=$(realpath ${dir}/pki/issued/${shortname}.crt)
ca=$(realpath ${dir}/pki/ca.crt)

echo
echo "The certificate was successfully signed."
echo
echo "You can find it here: ${res}"
echo "You may also need:    ${ca}"
echo
echo "You should now copy these two files back to your machine"
