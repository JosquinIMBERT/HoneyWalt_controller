#!/bin/bash

dir=$(realpath ${HONEYWALT_CONTROLLER_HOME}/var/key/)

export PATH="$PATH:/usr/share/easy-rsa/"
export EASYRSA_BATCH=1

if [ ! -d "${dir}" ]; then
        echo "Error: HoneyWalt_controller does not seem to be installed on this machine."
        exit 1
fi

cd ${dir}/
echo -n "Initializing controller's PKI..." && easyrsa init-pki >/dev/null 2>&1 && echo "done" || echo "failed"
echo -n "Generating controller's client cert request..." && easyrsa gen-req controller-client nopass >/dev/null 2>&1 && echo "done" || echo "failed"
echo -n "Generating controller's server cert request..." && easyrsa gen-req controller-server nopass >/dev/null 2>&1 && echo "done" || echo "failed"

${HONEYWALT_CONTROLLER_HOME}/scripts/sign-req.sh "${dir}/pki/reqs/controller-client.req" "client" "--silent"
${HONEYWALT_CONTROLLER_HOME}/scripts/sign-req.sh "${dir}/pki/reqs/controller-server.req" "server" "--silent"

cp "${dir}/ca/pki/issued/controller-client.crt" "${dir}/pki/"
cp "${dir}/ca/pki/issued/controller-server.crt" "${dir}/pki/"
cp "${dir}/ca/pki/ca.crt" "${dir}/pki/"
