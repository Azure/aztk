#!/bin/bash

# This file is the entry point of the docker container.

set -e
source ~/.bashrc
echo "Initializing spark container"

aztk_dir=$AZTK_WORKING_DIR/aztk

# -----------------------
# Preload jupyter samples
# -----------------------
mkdir -p /mnt/samples

# add all files from 'jupyter-samples' to container folder '/pyspark/samples'
for file in $(dirname $0)/jupyter-samples/*; do
    cp $file /mnt/samples
done

# ----------------------------
# Run aztk setup python scripts
# ----------------------------
# setup docker container
echo "Starting setup using Docker"

export PYTHONPATH=$PYTHONPATH:$AZTK_WORKING_DIR
echo 'export PYTHONPATH=$PYTHONPATH:$AZTK_WORKING_DIR' >> ~/.bashrc

echo "Running main.py script"
$AZTK_WORKING_DIR/.aztk-env/.venv/bin/python $(dirname $0)/main.py setup-spark-container

# sleep to keep container running
while true; do sleep 1; done
