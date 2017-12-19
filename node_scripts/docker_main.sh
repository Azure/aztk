#!/bin/bash

# This file is the entry point of the docker container.

set -e

# --------------------
# Setup custom scripts
# --------------------
custom_script_dir=$DOCKER_WORKING_DIR/custom-scripts

# -----------------------
# Preload jupyter samples
# TODO: remove when we support uploading random (non-executable) files as part custom-scripts
# -----------------------
mkdir -p /mnt/samples

# add all files from 'jupyter-samples' to container folder '/pyspark/samples'
for file in $(dirname $0)/jupyter-samples/*; do
    cp $file /mnt/samples
done

# ----------------------------
# Run aztk setup python scripts
# ----------------------------
# use python v3.5.4 to run aztk software
echo "Starting setup using Docker"
$(pyenv root)/versions/$AZTK_PYTHON_VERSION/bin/pip install -r $(dirname $0)/requirements.txt

echo "Running main.py script"
$(pyenv root)/versions/$AZTK_PYTHON_VERSION/bin/python $(dirname $0)/main.py install

# sleep to keep container running
while true; do sleep 1; done

