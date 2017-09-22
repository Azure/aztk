#!/bin/bash

# script to install blob storage connection on each node
# Usage:
# setup_wasb.sh [storage_account_name] [storage_account_key]

storage_account_name=$1 
storage_account_key=$2 
storage_account_suffix=$3

spark_home=/home/spark-current
cd $spark_home/conf

cp spark-defaults.conf.template spark-defaults.conf

cat >> spark-defaults.conf <<EOF
spark.jars                 $spark_home/jars/azure-storage-2.0.0.jar,$spark_home/jars/hadoop-azure-2.7.3.jar
EOF

cat >> core-site.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
<name>fs.AbstractFileSystem.wasb.Impl</name>
<value>org.apache.hadoop.fs.azure.Wasb</value>
</property>
<property>
<name>fs.azure.account.key.$storage_account_name.blob.$storage_account_suffix</name>
<value>$storage_account_key</value>
</property>
</configuration>
EOF

cd $spark_home/jars

# install the appropriate jars
apt install wget
wget http://repo1.maven.org/maven2/com/microsoft/azure/azure-storage/2.0.0/azure-storage-2.0.0.jar
wget http://repo1.maven.org/maven2/org/apache/hadoop/hadoop-azure/2.7.3/hadoop-azure-2.7.3.jar
