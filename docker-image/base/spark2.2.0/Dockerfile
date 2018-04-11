# Ubuntu 16.04 (Xenial)
FROM ubuntu:16.04

# set version of python required for aztk
ENV AZTK_PYTHON_VERSION=3.5.2

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
       maven \
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
    && git clone git://github.com/pyenv/pyenv.git .pyenv \
    && git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv \
    # install & setup pyenv
    && eval "$(pyenv init -)" \
    && echo 'eval "$(pyenv init -)"' >> ~/.bashrc \
    # install aztk required python version
    && env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install $AZTK_PYTHON_VERSION \
    && pyenv global $AZTK_PYTHON_VERSION \
    # download spark
    && curl -L "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=spark/spark-${SPARK_VERSION_KEY}/${SPARK_FULL_VERSION}.tgz" | tar -xvz -C /home \
    && ln -s "/home/${SPARK_FULL_VERSION}" /home/spark-current \
    # download hadoop
    && curl -fSL "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" | tar -xvz -C /opt/ \
    && ln -s /opt/hadoop-$HADOOP_VERSION/etc/hadoop /etc/hadoop \
    && cp /etc/hadoop/mapred-site.xml.template /etc/hadoop/mapred-site.xml \
    && mkdir /opt/hadoop-$HADOOP_VERSION/logs \
    && rm -rf /opt/hadoop-${HADOOP_VERSION}/share/doc \
    # azure data lake client jar
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=com.microsoft.azure:azure-data-lake-store-sdk:2.2.4:jar -Dtransitive=false \
    && cp /root/.m2/repository/com/microsoft/azure/azure-data-lake-store-sdk/2.2.4/azure-data-lake-store-sdk-2.2.4.jar /home/spark-current/jars/ \
    # azure storage client jar
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=com.microsoft.azure:azure-storage:7.0.0:jar -Dtransitive=false \
    && cp /root/.m2/repository/com/microsoft/azure/azure-storage/7.0.0/azure-storage-7.0.0.jar /home/spark-current/jars/ \
    # sql server connector jar
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=com.microsoft.sqlserver:mssql-jdbc:6.4.0.jre8:jar -Dtransitive=false \
    && cp /root/.m2/repository/com/microsoft/sqlserver/mssql-jdbc/6.4.0.jre8/mssql-jdbc-6.4.0.jre8.jar /home/spark-current/jars/ \
    # azure cosmos db connector jar
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=com.microsoft.azure:azure-cosmosdb-spark_2.2.0_2.11:1.1.1:jar -Dtransitive=false \
    && cp /root/.m2/repository/com/microsoft/azure/azure-cosmosdb-spark_2.2.0_2.11/1.1.1/azure-cosmosdb-spark_2.2.0_2.11-1.1.1.jar /home/spark-current/jars/ \
    # clean up maven
    && apt-get --purge autoremove -y maven wget curl \
    && apt-get autoremove -y \
    && rm -rf /root/.m2 \
    && rm -rf /var/lib/apt/lists/*


# set env vars
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH
ENV PATH $HADOOP_PREFIX/bin/:$PATH
RUN echo "export SPARK_DIST_CLASSPATH=$(hadoop classpath)" >> /.bashrc

CMD ["/bin/bash"]
