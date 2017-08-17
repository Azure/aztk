#!/bin/bash
set -ev

export PATH=/anaconda/envs/py35/bin:$PATH

echo "Starting setup with the Azure DSVM"
pip install -r $(dirname $0)/requirements.txt

echo "Running main.py script"
python $(dirname $0)/main.py install

