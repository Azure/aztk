FROM aztk/spark:v0.1.0-spark1.6.3-base

ARG ANACONDA_VERSION=Anaconda3-5.1.0

ENV PATH /opt/conda/bin:$PATH
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.continuum.io/archive/${ANACONDA_VERSION}-Linux-x86_64.sh -O ~/anaconda.sh \
    && /bin/bash ~/anaconda.sh -b -p /opt/conda \
    && rm ~/anaconda.sh \
    && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc \
    # reset default python to 3.5
    && rm /usr/bin/python \
    && ln -s /usr/bin/python3.5 /usr/bin/python

CMD ["/bin/bash"]
