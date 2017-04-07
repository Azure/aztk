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

export JAVA_HOME=/usr/lib/jvm/java-8-oracle
export PATH=$PATH:$JAVA_HOME/bin

echo "JAVA_HOME:" 
echo $JAVA_HOME

cd $AZ_BATCH_NODE_SHARED_DIR
tar xvf spark-2.1.0-bin-hadoop2.7.tgz
cp spark-2.1.0-bin-hadoop2.7/conf/slaves.template spark-2.1.0-bin-hadoop2.7/conf/slaves

# pushd $AZ_BATCH_NODE_SHARED_DIR
# tar xvf spark-2.1.0-bin-hadoop2.7.tgz
# cp spark-2.1.0-bin-hadoop2.7/conf/slaves.template spark-2.1.0-bin-hadoop2.7/conf/slaves
# popd

export SPARK_HOME=$AZ_BATCH_NODE_SHARED_DIR/spark-2.1.0-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin

echo "SPARK_HOME"
echo $SPARK_HOME

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
