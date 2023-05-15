#!/bin/bash

dir=$(realpath ${HONEYWALT_CONTROLLER_HOME}/var/key/)

if [ ! -d "${dir}" ]; then
        echo "Error: HoneyWalt_controller does not seem to be installed on this machine."
        exit 1
fi

cd ${dir}/
easyrsa init-pki
easyrsa gen-req controller-client nopass
easyrsa gen-req controller-server nopass

${HONEYWALT_CONTROLLER_HOME}/scripts/sign-req.sh "${dir}/pki/reqs/controller-client.req" "client"
${HONEYWALT_CONTROLLER_HOME}/scripts/sign-req.sh "${dir}/pki/reqs/controller-server.req" "server"

cp "${dir}/ca/pki/issued/controller-client.crt" "${dir}/pki/"
cp "${dir}/ca/pki/issued/controller-server.crt" "${dir}/pki/"
cp "${dir}/ca/pki/ca.crt" "${dir}/pki/"
