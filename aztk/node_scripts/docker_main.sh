#!/bin/bash

# This file is the entry point of the docker container.

set -e
source ~/.bashrc

# --------------------
# Setup custom scripts
# --------------------
custom_script_dir=$DOCKER_WORKING_DIR/custom-scripts
aztk_dir=$DOCKER_WORKING_DIR/aztk

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
# activate virtualenv and setup docker container
echo "Starting setup using Docker"

source /root/.env/bin/activate

pip install -r $(dirname $0)/requirements.txt
export PYTHONPATH=$PYTHONPATH:$DOCKER_WORKING_DIR
echo 'export PYTHONPATH=$PYTHONPATH:$DOCKER_WORKING_DIR' >> ~/.bashrc

echo "Running main.py script"
python $(dirname $0)/main.py install

# sleep to keep container running
while true; do sleep 1; done
