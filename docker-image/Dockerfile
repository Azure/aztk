# Ubuntu 16.04 (Xenial)
FROM ubuntu:16.04

# set version of python required for thunderbolt application
ENV AZTK_PYTHON_VERSION=3.5.4

# modify these ARGs on build time to specify your desired versions of Spark/Hadoop and Python
ARG SPARK_VERSION_KEY=spark-2.1.0-bin-hadoop2.7
ARG PYTHON_VERSION=3.5.4

# set up apt-get
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm git libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev 

# installing [software-properties-common] so that we can use [apt-add-repository] to add the repository [ppa:webupd8team/java] form which we install Java8
RUN apt-get install -y --no-install-recommends software-properties-common && \
    apt-add-repository ppa:webupd8team/java -y && \
    apt-get update -y

# installing java
RUN apt-get install -y --no-install-recommends default-jdk

# install and setup pyenv
RUN git clone git://github.com/yyuu/pyenv.git .pyenv
RUN git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
ENV HOME /
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN eval "$(pyenv init -)"
RUN echo 'export "$(pyenv init -)"' >> ~/.bashrc

# install thunderbolt required python version & the user specified version of python
RUN pyenv install -f $AZTK_PYTHON_VERSION && \
    pyenv install -s $PYTHON_VERSION
RUN pyenv global $PYTHON_VERSION

# install jupyter
RUN pip install jupyter && \
    pip install --upgrade jupyter

# install p4j
RUN curl https://pypi.python.org/packages/1f/b0/882c144fe70cc3f1e55d62b8611069ff07c2d611d99f228503606dd1aee4/py4j-0.10.0.tar.gz | tar xvz -C /home && \
    cd /home/py4j-0.10.0 && \
    python setup.py install 

# install spark
RUN curl https://d3kbcqa49mib13.cloudfront.net/$SPARK_VERSION_KEY.tgz | tar xvz -C /home

# set up symlink for SPARK HOME
RUN ln -s /home/$SPARK_VERSION_KEY /home/spark-current

# set env vars
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV USER_PYTHON_VERSION $PYTHON_VERSION
ENV PATH $SPARK_HOME/bin:$PATH

CMD ["/bin/bash"]
