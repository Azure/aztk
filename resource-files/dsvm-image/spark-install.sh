#!/bin/bash

echo "Running Spark Install Script"

export SPARK_HOME=/dsvm/tools/spark/spark-2.0.2
export PATH=$PATH:$SPARK_HOME/bin
chmod -R 777 $SPARK_HOME

exit 0
