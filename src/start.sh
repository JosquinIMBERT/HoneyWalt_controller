#!/bin/bash

# This script should be called at boot by the controller

# Update HoneyWalt
#git -C ${HONEYWALT_CONTROLLER_HOME} reset --hard
#git -C ${HONEYWALT_CONTROLLER_HOME} pull

# Start HoneyWalt
python3 ${HONEYWALT_CONTROLLER_HOME}/src/honeywalt_controller.py