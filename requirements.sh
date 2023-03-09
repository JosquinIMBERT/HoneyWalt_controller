#!/bin/bash

# Installing dependencies
pip3 install sshtunnel

# Adding environment variable
dir=$(dirname $0)
home=$(realpath ${dir})
echo "export HONEYWALT_CONTROLLER_HOME=${home}/" >> ~/.bash_profile

# Include ~/.bash_profile if ~/.bashrc does not exist or if it does not include it already
if [ ! -f ~/.bashrc ] || ! grep -q \.bash_profile <~/.bashrc; then
cat <<EOT >> ~/.bashrc
if [ -f ~/.bash_profile ]; then
    . ~/.bash_profile
fi
EOT
fi
