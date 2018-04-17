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
       python3-pip \
       python3-venv \
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
    && ln -s /usr/bin/python3.5 /usr/bin/python \
    && python -m pip install --upgrade pip setuptools wheel \
    && apt-get remove -y python3-pip \
    # build and install spark
    && git clone https://github.com/apache/spark.git \
    && cd spark \
    && git checkout tags/v2.2.0 \
    && export MAVEN_OPTS="-Xmx3g -XX:ReservedCodeCacheSize=1024m" \
    && ./dev/make-distribution.sh --name custom-spark --pip --tgz -Phive -Phive-thriftserver -Dhadoop.version=2.8.3 \
    && tar -xvzf /spark/spark-2.2.0-bin-custom-spark.tgz --directory=/home \
    && ln -s "/home/spark-2.2.0-bin-custom-spark" /home/spark-current \
    && rm -rf /spark \ 
    # cleanup
    && apt-get --purge autoremove -y maven \
    && apt-get autoremove -y \
    && rm -rf /root/.m2 \
    && rm -rf /var/lib/apt/lists/*

# TODO: use dependency:copy-dependencies to move jars and deps to $SPARK_HOME/jars
RUN apt-get update \
    && apt-get install -y --no-install-recommends maven \
    # azure data lake client jar
    && mvn dependency:copy -Dartifact=com.microsoft.azure:azure-data-lake-store-sdk:2.2.4:jar -DoutputDirectory=/home/spark-current/jars/ \
    # azure storage client jar
    && mvn dependency:copy -Dartifact=com.microsoft.azure:azure-storage:7.0.0:jar -DoutputDirectory=/home/spark-current/jars/ \
    # sql server connector jar
    && mvn dependency:copy -Dartifact=com.microsoft.sqlserver:mssql-jdbc:6.4.0.jre8:jar -DoutputDirectory=/home/spark-current/jars/ \
    # azure cosmos db connector jar
    && mvn dependency:copy -Dartifact=com.microsoft.azure:azure-cosmosdb-spark_2.2.0_2.11:1.1.1:jar -DoutputDirectory=/home/spark-current/jars/ \
    # move jars to spark-current/jars
    # && find /root/.m2/* -name '*.jar' -print0 | xargs -0 cp -t  /home/spark-current/jars/ \
    && apt-get --purge autoremove -y maven \
    && apt-get autoremove -y \
    && rm -rf /root/.m2 \
    && rm -rf /var/lib/apt/lists/*


# set env vars
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH

CMD ["/bin/bash"]
