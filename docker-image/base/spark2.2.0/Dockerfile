# Ubuntu 16.04 (Xenial)
FROM ubuntu:16.04

# set version of python required for thunderbolt application
ENV AZTK_PYTHON_VERSION=3.5.4

# modify these ARGs on build time to specify your desired versions of Spark/Hadoop
ENV SPARK_VERSION_KEY 2.2.0
ENV SPARK_FULL_VERSION spark-${SPARK_VERSION_KEY}-bin-without-hadoop
ENV HADOOP_VERSION 2.8.3
ENV HADOOP_PREFIX=/opt/hadoop-$HADOOP_VERSION
ENV HADOOP_CONF_DIR=/etc/hadoop

# set up env vars for pyenv
ENV HOME /
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN apt-get clean \
    && apt-get update -y \
    # install dependency packages
    && apt-get install -y --no-install-recommends \
       make \
       build-essential \
       zlib1g-dev \
       libssl-dev \
       libbz2-dev \
       libreadline-dev \
       libsqlite3-dev \
       wget \
       curl \
       llvm \
       git \
       libncurses5-dev \
       libncursesw5-dev \
       xz-utils \
       tk-dev \
    && apt-get update -y \
    # install [software-properties-common] 
    # so we can use [apt-add-repository] to add the repository [ppa:webupd8team/java] 
    # from which we install Java8
    && apt-get install -y --no-install-recommends software-properties-common \
    && apt-add-repository ppa:webupd8team/java -y \
    && apt-get update -y \
    # install java
    && apt-get install -y --no-install-recommends default-jdk \
    # download pyenv
    && git clone git://github.com/yyuu/pyenv.git .pyenv \
    && git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv \
    # install & setup pyenv
    && eval "$(pyenv init -)" \
    && echo 'eval "$(pyenv init -)"' >> ~/.bashrc \
    # install aztk required python version 
    && env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install -f $AZTK_PYTHON_VERSION \
    && pyenv global $AZTK_PYTHON_VERSION \
    # download spark
    && curl -L "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=spark/spark-${SPARK_VERSION_KEY}/${SPARK_FULL_VERSION}.tgz" | tar -xvz -C /home \
    && ln -s "/home/${SPARK_FULL_VERSION}" /home/spark-current \
    # download hadoop
    && curl -fSL "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" | tar -xvz -C /opt/ \
    && ln -s /opt/hadoop-$HADOOP_VERSION/etc/hadoop /etc/hadoop \
    && cp /etc/hadoop/mapred-site.xml.template /etc/hadoop/mapred-site.xml \
    && mkdir /opt/hadoop-$HADOOP_VERSION/logs

# set env vars
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH
ENV PATH $HADOOP_PREFIX/bin/:$PATH
ENV SPARK_DIST_CLASSPATH $(hadoop classpath)

CMD ["/bin/bash"]
