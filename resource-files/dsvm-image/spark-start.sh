#!/bin/bash

echo "Running Application Command"
echo ""

echo "CPP_NODES:" 
echo $CCP_NODES

echo "AZ_BATCH_NODE_LIST:"
echo $AZ_BATCH_NODE_LIST

echo "AZ_BATCH_HOST_LIST:"
echo $AZ_BATCH_HOST_LIST

echo "AZ_BATCH_MASTER_NODE:"
echo $AZ_BATCH_MASTER_NODE

echo "AZ_BATCH_TASK_SHARED_DIR:"
echo $AZ_BATCH_TASK_SHARED_DIR

echo "AZ_BATCH_IS_CURRENT_NODE_MASTER:"
echo $AZ_BATCH_IS_CURRENT_NODE_MASTER

export SPARK_HOME=/dsvm/tools/spark/spark-2.0.2
export PATH=$PATH:$SPARK_HOME/bin

echo "SPARK_HOME:"
echo $SPARK_HOME

cp $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh

# split $AZ_BATCH_MASTER_NODE (10.0.0.X:PORT) to only IP portion
m=${AZ_BATCH_MASTER_NODE%:*}

# add IP of master-node to $SPARK_HOME/conf/spark-env.sh
echo $m >> $SPARK_HOME/conf/spark-env.sh

echo ""
echo "----------------------------"
echo ""

echo "Running start-all.sh to start the spark cluster:"
# start spark cluster - run in background process 
bash $SPARK_HOME/sbin/start-all.sh &

# install and setup jupyter 
# TODO this needs to run with root user (but running the multi-instance task on run_elavated will cause the start-all.sh script to fail)
<< INSTALL_JUPYTER
pip install jupyter
pip install toree
jupyter toree install --spark_home=$SPARK_HOME --interpreters=PySpark
jupyter notebook --no-browser
INSTALL_JUPYTER

# command to start spark with pyspark once ssh'ed into master node: 
<< START_PYSPARK 
path/to/spark_home/bin/pyspark --master spark://localhost:7077
START_PYSPARK

# command to run spark job with submit-job once ssh'ed into master node:
<< SUBMIT_SPARK_SCRIPT
path/to/spark_home/bin/spark-submit \
   --master spark://localhost:7077 \ 
   path/to/spark_home/examples/src/main/python/pi.py \
   1000
SUBMIT_SPARK_SCRIPT


