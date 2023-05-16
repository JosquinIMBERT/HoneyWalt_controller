#!/bin/bash

dir=$(realpath ${HONEYWALT_CONTROLLER_HOME}/var/key/ca/)

usage() {
	echo "Usage: $0: <req-file> <client/server>"
}

if [ $# -ne 2 ] || [ ! -f "$1" ] || [[ "$2" != "client" && "$2" != "server" ]]; then
	usage
	exit 1
fi

file=$1
role=$2
name=$(basename ${file} | cut -d"." -f1)

shortname=$(echo $RANDOM | md5sum | head -c 20; echo;)

cd ${dir}/

easyrsa import-req ${file} ${shortname} >/dev/null
easyrsa show-req ${shortname} >/dev/null
easyrsa sign-req ${role} ${shortname} >/dev/null
easyrsa show-cert ${shortname} >/dev/null

srcres=$(realpath ${dir}/pki/issued/${shortname}.crt)
dstres=$(realpath ${dir}/pki/issued/${name}.crt)
mv ${srcres} ${dstres}

res=$(realpath ${dir}/pki/issued/${shortname}.crt)
ca=$(realpath ${dir}/pki/ca.crt)

echo
echo "The certificate was successfully signed."
echo
echo "You can find it here: ${res}"
echo "You may also need:    ${ca}"
echo
echo "You should now copy these two files back to your machine"
echo
