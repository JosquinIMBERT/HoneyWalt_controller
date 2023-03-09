#!/bin/bash

pip3 install sshtunnel

dir=$(dirname $0)
home=$(realpath ${dir})
echo "export HONEYWALT_CONTROLLER_HOME=${home}/" >> ~/.bash_profile
