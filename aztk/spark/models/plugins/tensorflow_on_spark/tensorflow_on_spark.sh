#!/bin/bash

# This plugin requires HDFS to be enabled and on the path

# setup TensorFlowOnSpark
git clone https://github.com/yahoo/TensorFlowOnSpark.git
cd TensorFlowOnSpark
export TFoS_HOME=$(pwd)
export TFoS_HOME=~/TensorFlowOnSpark >> ~/.bashrc

if  [ "$AZTK_GPU_ENABLED" = "true" ]; then
    pip install tensorflow-gpu
    pip install tensorflowonspark
else
    pip install tensorflow-cpu
    pip install tensorflowonspark
fi

# add libhdfs.so to path
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HADOOP_HOME/lib/native/libhdfs.so" >> ~/.bashrc
