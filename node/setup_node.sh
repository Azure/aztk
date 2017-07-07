#!/bin/bash
set -ev

export PATH=/anaconda/envs/py35/bin:$PATH

echo "Starting setup"
pip install -r requirements.txt
echo "Installed dependencies, picking master"
python pick_master.py