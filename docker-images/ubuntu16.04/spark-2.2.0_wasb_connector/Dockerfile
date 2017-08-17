FROM jiata/spark:latest

ARG STORAGE_ACCOUNT_NAME
ARG STORAGE_ACCOUNT_KEY
ENV STORAGE_ACCOUNT_NAME $STORAGE_ACCOUNT_NAME
ENV STORAGE_ACCOUNT_KEY $STORAGE_ACCOUNT_KEY

ENV SPARK_HOME /home/spark-2.2.0-bin-hadoop2.7

RUN cp $SPARK_HOME/conf/spark-defaults.conf.template $SPARK_HOME/conf/spark-defaults.conf

RUN echo 'spark.jars                 /home/spark-2.2.0-bin-hadoop2.7/jars/azure-storage-2.0.0.jar,/home/spark-2.2.0-bin-hadoop2.7/jars/hadoop-azure-2.7.3.jar' >> $SPARK_HOME/conf/spark-defaults.conf

RUN echo '<?xml version="1.0" encoding="UTF-8"?>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<configuration>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<property>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<name>fs.AbstractFileSystem.wasb.Impl</name>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<value>org.apache.hadoop.fs.azure.Wasb</value>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '</property>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<property>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<name>fs.azure.account.key.'$STORAGE_ACCOUNT_NAME'.blob.core.windows.net</name>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '<value>'$STORAGE_ACCOUNT_KEY'</value>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '</property>' >> $SPARK_HOME/conf/core-site.xml && \
    echo '</configuration>' >> $SPARK_HOME/conf/core-site.xml

RUN apt-get install wget

RUN cd $SPARK_HOME/jars && \
    wget http://repo1.maven.org/maven2/com/microsoft/azure/azure-storage/2.0.0/azure-storage-2.0.0.jar && \
    wget http://central.maven.org/maven2/org/apache/hadoop/hadoop-azure/2.7.3/hadoop-azure-2.7.3.jar

CMD ["bin/bash"]
