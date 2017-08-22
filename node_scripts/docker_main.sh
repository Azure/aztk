#!/bin/bash

# This file is the entry point of the docker container.
# It will run the custom scripts if present and start spark.

set -e
export PATH=/usr/bin/python3:$PATH

custom_script_dir=$DOCKER_WORKING_DIR/custom-scripts

if [ -d "$custom_script_dir" ]; then
    echo "Custom script dir '$custom_script_dir' exists. Running all script there."
    for script in  $custom_script_dir/*.sh; do
        echo "Running custom script $script"
        bash $script
    done
else
    echo "Custom script dir '$custom_script_dir' doesn't exists. Will not run any custom scripts."
fi

storage_account_name=$STORAGE_ACCOUNT_NAME
storage_account_key=$STORAGE_ACCOUNT_KEY
storage_account_suffix=$STORAGE_ACCOUNT_SUFFIX

if [ -n "$STORAGE_ACCOUNT_NAME" ] && [ -n "$STORAGE_ACCOUNT_KEY" ] && [ -n "$STORAGE_ACCOUNT_SUFFIX" ]; then
    echo "Setting up WASB connection"
    bash $(dirname $0)/setup_wasb.sh $storage_account_name $storage_account_key $storage_account_suffix
else
    echo "Storage credentials not set"
fi

echo "Starting setup using Docker"
pip3 install -r $(dirname $0)/requirements.txt

echo "Running main.py script"
python3 $(dirname $0)/main.py install

# sleep to keep container running
while true; do sleep 1; done

