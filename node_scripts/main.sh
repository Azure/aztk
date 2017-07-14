#!/bin/bash
set -ev

export PATH=/anaconda/envs/py35/bin:$PATH

echo "Starting setup"
pip install -r $(dirname $0)/requirements.txt
echo "Installed dependencies, picking master"
python $(dirname $0)/main.py install