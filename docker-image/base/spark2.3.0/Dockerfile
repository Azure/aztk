# Ubuntu 16.04 (Xenial)
FROM ubuntu:16.04

# set AZTK version compatibility
ENV AZTK_DOCKER_IMAGE_VERSION 0.1.0

# set version of python required for aztk
ENV AZTK_PYTHON_VERSION=3.5.2

# modify these ARGs on build time to specify your desired versions of Spark/Hadoop
ENV SPARK_VERSION_KEY 2.3.0
ENV SPARK_FULL_VERSION spark-${SPARK_VERSION_KEY}-bin-without-hadoop
ENV HADOOP_VERSION 2.8.3
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# set env vars
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH

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
    # set up user python and aztk python
    && ln -s /usr/bin/python3.5 /usr/bin/python \
    && /usr/bin/python -m pip install --upgrade pip setuptools wheel \
    && apt-get remove -y python3-pip \
    # build and install spark
    && git clone https://github.com/apache/spark.git \
    && cd spark \
    && git checkout tags/v${SPARK_VERSION_KEY} \
    && export MAVEN_OPTS="-Xmx3g -XX:ReservedCodeCacheSize=1024m" \
    && ./dev/make-distribution.sh --name custom-spark --pip --tgz -Pnetlib-lgpl -Phive -Phive-thriftserver -Dhadoop.version=${HADOOP_VERSION} -DskipTests \
    && tar -xvzf /spark/spark-${SPARK_VERSION_KEY}-bin-custom-spark.tgz --directory=/home \
    && ln -s "/home/spark-${SPARK_VERSION_KEY}-bin-custom-spark" /home/spark-current \
    && rm -rf /spark \ 
    # copy azure storage jars and dependencies to $SPARK_HOME/jars
    && echo "<project>" \
                    "<modelVersion>4.0.0</modelVersion>" \
                    "<groupId>groupId</groupId>" \
                    "<artifactId>artifactId</artifactId>" \
                    "<version>1.0</version>" \
                "<dependencies>" \
                    "<dependency>" \
                        "<groupId>org.apache.hadoop</groupId>" \
                        "<artifactId>hadoop-azure-datalake</artifactId>" \
                        "<version>${HADOOP_VERSION}</version>" \
                    "<exclusions>" \
                        "<exclusion>" \
                            "<groupId>org.apache.hadoop</groupId>" \
                            "<artifactId>hadoop-common</artifactId>" \
                        "</exclusion>" \
                    "</exclusions> " \
                    "</dependency>" \
                    "<dependency>" \
                        "<groupId>org.apache.hadoop</groupId>" \
                        "<artifactId>hadoop-azure</artifactId>" \
                        "<version>${HADOOP_VERSION}</version>" \
                    "<exclusions>" \
                        "<exclusion>" \
                            "<groupId>org.apache.hadoop</groupId>" \
                            "<artifactId>hadoop-common</artifactId>" \
                        "</exclusion>" \
                        "<exclusion>" \
                            "<groupId>com.fasterxml.jackson.core</groupId>" \
                            "<artifactId>jackson-core</artifactId>" \
                        "</exclusion>" \
                    "</exclusions> " \
                    "</dependency>" \
                    "<dependency>" \
                        "<groupId>com.microsoft.sqlserver</groupId>" \
                        "<artifactId>mssql-jdbc</artifactId>" \
                        "<version>6.4.0.jre8</version>" \
                    "</dependency>" \
                    "<dependency>" \
                        "<groupId>com.microsoft.azure</groupId>" \
                        "<artifactId>azure-storage</artifactId>" \
                        "<version>2.2.0</version>" \
                        "<exclusions>" \
                            "<exclusion>" \
                                "<groupId>com.fasterxml.jackson.core</groupId>" \
                                "<artifactId>jackson-core</artifactId>" \
                            "</exclusion>" \
                            "<exclusion>" \
                                "<groupId>org.apache.commons</groupId>" \
                                "<artifactId>commons-lang3</artifactId>" \
                            "</exclusion>" \
                            "<exclusion>" \
                                "<groupId>org.slf4j</groupId>" \
                                "<artifactId>slf4j-api</artifactId>" \
                            "</exclusion>" \
                        "</exclusions>" \
                    "</dependency>" \
                    "<dependency>" \
                        "<groupId>com.microsoft.azure</groupId>" \
                        "<artifactId>azure-cosmosdb-spark_2.2.0_2.11</artifactId>" \
                        "<version>1.1.1</version>" \
                        "<exclusions>" \
                            "<exclusion>" \
                                "<groupId>org.apache.tinkerpop</groupId>" \
                                "<artifactId>tinkergraph-gremlin</artifactId>" \
                            "</exclusion>" \
                            "<exclusion>" \
                                "<groupId>org.apache.tinkerpop</groupId>" \
                                "<artifactId>spark-gremlin</artifactId>" \
                            "</exclusion>" \
                            "<exclusion>" \
                                "<groupId>io.netty</groupId>" \
                                "<artifactId>*</artifactId>" \
                            "</exclusion>" \
                            "<exclusion>" \
                                "<groupId>com.fasterxml.jackson.core</groupId>" \
                                "<artifactId>jackson-annotations</artifactId>" \
                            "</exclusion>" \
                        "</exclusions> " \
                    "</dependency>" \
                "</dependencies>" \
            "</project>" > /tmp/pom.xml \
    && cd /tmp \
    && mvn dependency:copy-dependencies -DoutputDirectory="${SPARK_HOME}/jars/" \
    # cleanup
    && apt-get --purge autoremove -y maven python3-pip \
    && apt-get autoremove -y \
    && apt-get autoclean -y \
    && rm -rf /tmp/* \
    && rm -rf /root/.cache \
    && rm -rf /root/.m2 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
