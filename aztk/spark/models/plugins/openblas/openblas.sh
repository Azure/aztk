#!/bin/bash
apt-get update &&
apt-get install -y libopenblas-base &&
update-alternatives --config libblas.so.3
