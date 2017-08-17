FROM ubuntu:16.04

# set up apt-get
RUN apt-get -y update 

# install base
RUN apt-get -y install software-properties-common

# install java
RUN apt-add-repository ppa:webupd8team/java && \
    apt-get -y update && \
    apt-get -y install default-jdk 

# install common tools
RUN apt-get -y install git

# install curl
RUN apt-get -y install curl 
# install pip
RUN apt-get -y install python3-pip && \
    pip3 install --upgrade pip

# install jupyter
RUN pip3 install jupyter && \
    pip3 install --upgrade jupyter

# install p4j
RUN curl https://pypi.python.org/packages/1f/b0/882c144fe70cc3f1e55d62b8611069ff07c2d611d99f228503606dd1aee4/py4j-0.10.0.tar.gz | tar xvz -C /home && \
    cd /home/py4j-0.10.0 && \
    python3 setup.py install 

# install spark
RUN curl https://d3kbcqa49mib13.cloudfront.net/spark-2.2.0-bin-hadoop2.7.tgz | tar xvz -C /home

# set env vars
RUN export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64 && \
    export SPARK_HOME=/home/spark-2.2.0-bin-hadoop2.7 && \
    export PYSPARK_PYTHON=python3 && \
    export PATH=$PATH:$SPARK_HOME/bin

# set env vars in .bashrc
RUN echo 'export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64' >> ~/.bashrc && \
    echo 'export SPARK_HOME=/home/spark-2.2.0-bin-hadoop2.7' >> ~/.bashrc && \
    echo 'export PYSPARK_PYTHON=python3' >> ~/.bashrc && \
    echo 'export PATH=$PATH:$SPARK_HOME/bin' >> ~/.bashrc

CMD ["/bin/bash"]
