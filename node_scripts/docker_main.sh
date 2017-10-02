#!/bin/bash

# This file is the entry point of the docker container.
# It will setup WASB and start Spark.
# This script uses the storage account configured in .thunderbolt/secrets.yaml
# This script uses the specificied user python version ($USER_PYTHON_VERSION)

set -e
aztk_python_version=3.5.4

# --------------------
# Setup custom scripts
# --------------------
custom_script_dir=$DOCKER_WORKING_DIR/custom-scripts

# -----------------------
# Preload jupyter samples 
# -----------------------
mkdir /jupyter
mkdir /jupyter/samples

# add all files from 'jupyter-samples' to container folder '/pyspark/samples'
for file in $(dirname $0)/jupyter-samples/*; do
    cp $file /jupyter/samples
done

# --------------------
# Setup WASB connector 
# --------------------
storage_account_name=$STORAGE_ACCOUNT_NAME
storage_account_key=$STORAGE_ACCOUNT_KEY
storage_account_suffix=$STORAGE_ACCOUNT_SUFFIX

if [ -n "$STORAGE_ACCOUNT_NAME" ] && [ -n "$STORAGE_ACCOUNT_KEY" ] && [ -n "$STORAGE_ACCOUNT_SUFFIX" ]; then
    echo "Setting up WASB connection"
    bash $(dirname $0)/setup_wasb.sh $storage_account_name $storage_account_key $storage_account_suffix
else
    echo "Storage credentials not set"
fi

# ----------------------------
# Run aztk setup python scripts 
# ----------------------------
# use python v3.5.4 to run aztk software
echo "Starting setup using Docker"
$(pyenv root)/versions/$aztk_python_version/bin/pip install -r $(dirname $0)/requirements.txt

echo "Running main.py script"
$(pyenv root)/versions/$aztk_python_version/bin/python $(dirname $0)/main.py install

# sleep to keep container running
while true; do sleep 1; done

