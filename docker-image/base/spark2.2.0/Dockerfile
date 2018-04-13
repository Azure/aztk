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
    # set up python
    && ln -s /usr/bin/python3.5 /usr/bin/python \
    && python -m pip install --upgrade pip setuptools wheel \
    && apt-get remove -y python3-pip \
    # download spark
    && curl -L "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=spark/spark-${SPARK_VERSION_KEY}/${SPARK_FULL_VERSION}.tgz" | tar -xvz -C /home \
    && ln -s "/home/${SPARK_FULL_VERSION}" /home/spark-current \
    # download hadoop
    && curl -fSL "https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" | tar -xvz -C /opt/ \
    # copy necessary jars and remove hadoop
    && find /opt/hadoop-2.8.3/share/hadoop/common/lib/* -name '*.jar' -print0 | xargs -0 cp -t  /home/spark-current/jars/ \
    && find /opt/hadoop-2.8.3/share/hadoop/common/* -name '*.jar' -print0 | xargs -0 cp -t  /home/spark-current/jars/ \
    && find /opt/hadoop-2.8.3/share/hadoop/mapreduce/lib/* -name '*.jar' -print0 | xargs -0 cp -t  /home/spark-current/jars/ \
    && find /opt/hadoop-2.8.3/share/hadoop/mapreduce/* -name '*.jar' -print0 | xargs -0 cp -t  /home/spark-current/jars/ \
    && rm -rf /opt/hadoop-${HADOOP_VERSION} \
    # hive and thrift dependencies
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.spark-project.hive:hive-cli:1.2.1.spark:jar -Dtransitive=false \
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.spark-project.hive:hive-exec:1.2.1.spark2:jar -Dtransitive=false \
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.spark-project.hive:hive-jdbc:1.2.1.spark2:jar -Dtransitive=false \
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.spark-project.hive:hive-metastore:1.2.1.spark2:jar -Dtransitive=false \
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.spark-project.hive:hive-beeline:1.2.1.spark2:jar -Dtransitive=false \
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.apache.spark:spark-hive-thriftserver_2.11:2.2.0:jar -Dtransitive=false \
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.apache.spark:spark-hive_2.11:2.2.0:jar -Dtransitive=false \
    && mvn org.apache.maven.plugins:maven-dependency-plugin:3.1.0:get -Dartifact=org.apache.thrift:libthrift:0.9.3:jar -Dtransitive=false \
    && cp /root/.m2/repository/org/spark-project/hive/hive-cli/1.2.1.spark/hive-cli-1.2.1.spark.jar /home/spark-current/jars/ \
    && cp /root/.m2/repository/org/spark-project/hive/hive-exec/1.2.1.spark2/hive-exec-1.2.1.spark2.jar /home/spark-current/jars/ \
    && cp /root/.m2/repository/org/spark-project/hive/hive-jdbc/1.2.1.spark2/hive-jdbc-1.2.1.spark2.jar /home/spark-current/jars/ \
    && cp /root/.m2/repository/org/spark-project/hive/hive-metastore/1.2.1.spark2/hive-metastore-1.2.1.spark2.jar /home/spark-current/jars/ \
    && cp /root/.m2/repository/org/spark-project/hive/hive-beeline/1.2.1.spark2/hive-beeline-1.2.1.spark2.jar /home/spark-current/jars/ \
    && cp /root/.m2/repository/org/apache/spark/spark-hive-thriftserver_2.11/2.2.0/spark-hive-thriftserver_2.11-2.2.0.jar /home/spark-current/jars/ \
    && cp /root/.m2/repository/org/apache/thrift/libthrift/0.9.3/libthrift-0.9.3.jar /home/spark-current/jars/ \

RUN cp /root/.m2/repository/org/apache/thrift/apache/libthrift_0.9.3.0.0.3/libthrift-0.9.3.jar /home/spark-current/jars/ \
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
    && apt-get --purge autoremove -y maven \
    && apt-get autoremove -y \
    && rm -rf /root/.m2 \
    && rm -rf /var/lib/apt/lists/*


# set env vars
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH

CMD ["/bin/bash"]
