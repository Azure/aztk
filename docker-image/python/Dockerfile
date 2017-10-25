# Ubuntu 16.04 (Xenial)
FROM ubuntu:16.04

# modify these ARGs on build time to specify your desired versions of Spark/Hadoop
ARG SPARK_VERSION_KEY=spark-2.2.0-bin-hadoop2.7
ARG ANACONDA_VERSION=anaconda3-5.0.0

# since aztk requires python version > v3.4.0, 
# just use the python version provided by anaconda3-5.0.0 (which is v3.6.2)
ENV AZTK_PYTHON_VERSION=ANACONDA_VERSION

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
    && echo "$(pyenv init -)" >> ~/.bashrc \
    # install thunderbolt required python version & the user specified version of python
    && pyenv install -f $ANACONDA_VERSION \
    && pyenv global $ANACONDA_VERSION \
    # install spark & setup symlink to SPARK_HOME
    && curl https://d3kbcqa49mib13.cloudfront.net/$SPARK_VERSION_KEY.tgz | tar xvz -C /home \
    && ln -s /home/$SPARK_VERSION_KEY /home/spark-current


# set env vars
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV SPARK_HOME /home/spark-current
ENV PATH $SPARK_HOME/bin:$PATH
ENV USER_PYTHON_VERSION $ANACONDA_VERSION

CMD ["/bin/bash"]
