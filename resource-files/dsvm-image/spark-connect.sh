#!/bin/bash

echo "Running Coordination Command"
echo "Setting up networking for spark..."
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

echo "AZ_BATCH_NODE_SHARED_DIR:"
echo $AZ_BATCH_NODE_SHARED_DIR

export SPARK_HOME=/dsvm/tools/spark/spark-2.0.2
export PATH=$PATH:$SPARK_HOME/bin

echo "SPARK_HOME"
echo $SPARK_HOME

cp $SPARK_HOME/conf/slaves.template $SPARK_HOME/conf/slaves

echo "" >> $SPARK_HOME/conf/slaves # add newline to slaves file
IFS=',' read -r -a workerips <<< $AZ_BATCH_HOST_LIST
for index in "${!workerips[@]}"
do
    echo "${workerips[index]}" >> $SPARK_HOME/conf/slaves
    echo "${workerips[index]}"
done

echo ""
echo "-------------------------------"
echo ""
