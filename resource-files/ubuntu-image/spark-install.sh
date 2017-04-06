#!/bin/bash

echo "Running Spark Install Script"

echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections

# installation of Oracle Java JDK.
sudo apt-get -y update
sudo apt-get -y install python-software-properties
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get -y update
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
sudo apt-get -y install oracle-java8-installer 

# Install pip(3) for package management
sudo apt-get -y install python-pip
pip install --upgrade pip

# Installation of commonly used python scipy tools
sudo apt-get -y install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose 

# Installation of scala
wget http://www.scala-lang.org/files/archive/scala-2.11.1.deb
sudo dpkg -i scala-2.11.1.deb
sudo apt-get -y update
sudo apt-get -y install scala

# Installation of sbt
# http://www.scala-sbt.org/0.13/docs/Installing-sbt-on-Linux.html
echo "deb http://dl.bintray.com/sbt/debian /" | sudo tee -a /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt-get update
sudo apt-get install sbt

# Downloading spark
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
cp spark-2.1.0-bin-hadoop2.7.tgz $AZ_BATCH_NODE_SHARED_DIR
sudo chmod -R 777 $AZ_BATCH_NODE_SHARED_DIR/spark-2.1.0-bin-hadoop2.7

# tar xvf spark-2.1.0-bin-hadoop2.7.tgz
# cp spark-2.1.0-bin-hadoop2.7/conf/slaves.template spark-2.1.0-bin-hadoop2.7/conf/slaves
# cp -r spark-2.1.0-bin-hadoop2.7 $AZ_BATCH_NODE_SHARED_DIR

exit 0
