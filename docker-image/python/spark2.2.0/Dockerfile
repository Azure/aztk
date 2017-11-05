# Ubuntu 16.04 (Xenial)
FROM jiata/aztk-vanilla:0.1.0-spark2.2.0

# modify these ARGs on build time to specify your desired versions of Spark/Hadoop
ARG ANACONDA_VERSION=anaconda3-5.0.0

# install user specificed version of anaconda
RUN pyenv install -f $ANACONDA_VERSION \
    && pyenv global $ANACONDA_VERSION \
    && apt-get install unzip \
    # Fetch h2o_pysparkling 
    && pip install http://h2o-release.s3.amazonaws.com/h2o/rel-weierstrass/7/Python/h2o-3.14.0.7-py2.py3-none-any.whl \
    && pip install h2o_pysparkling_2.2 \
    # Install Sparkling water 2.2.2
    && cd /home \
    && wget http://h2o-release.s3.amazonaws.com/sparkling-water/rel-2.2/2/sparkling-water-2.2.2.zip \
    && unzip sparkling-water-2.2.2.zip 

# set env vars
ENV SPARKLING_WATER /home/sparkling-water-2.2.2/assembly/build/libs/sparkling-water-assembly_2.11-2.2.2-all.jar
ENV USER_PYTHON_VERSION $ANACONDA_VERSION

CMD ["/bin/bash"]
