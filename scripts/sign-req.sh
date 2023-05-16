#!/bin/bash

dir=$(realpath ${HONEYWALT_CONTROLLER_HOME}/var/key/ca/)

export PATH="$PATH:/usr/share/easy-rsa/"
export EASYRSA_BATCH=1

usage() {
	echo "Usage: $0: <req-file> <client/server> [-s/--silent]"
}

if [ $# -lt 2 ] || [ ! -f "$1" ] || [[ "$2" != "client" && "$2" != "server" ]]; then
	usage
	exit 1
fi

silent=0
if [ $# -ge 3 ] && [[ "$3" == "-s" || "$3" == "--silent" ]]; then
        silent=1
fi

file=$(realpath $1)
role=$2
name=$(basename ${file} | cut -d"." -f1)

shortname=$(echo $RANDOM | md5sum | head -c 20; echo;)

cd ${dir}/

echo -n "Importing request ${file}..." && easyrsa import-req ${file} ${shortname} >/dev/null 2>&1 && echo "done" || echo "failed"
echo -n "Signing ${role} cert request..." && easyrsa sign-req ${role} ${shortname} >/dev/null 2>&1 && echo "done" || echo "failed"

srcres=$(realpath ${dir}/pki/issued/${shortname}.crt)
dstres=$(realpath ${dir}/pki/issued/${name}.crt)
mv ${srcres} ${dstres}

res=${dstres}
ca=$(realpath ${dir}/pki/ca.crt)

if [ $silent -eq 0 ]; then
	echo
	echo "The certificate was successfully signed."
	echo
	echo "You can find it here: ${res}"
	echo "You may also need:    ${ca}"
	echo
	echo "You should now copy these two files back to your machine"
	echo
fi
