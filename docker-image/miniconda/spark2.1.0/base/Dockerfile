FROM aztk/spark:v0.1.0-spark2.1.0-base

ARG MINICONDA_VERISON=Miniconda3-4.4.10

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing \
    && apt-get install -y wget bzip2 ca-certificates curl git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.continuum.io/miniconda/${MINICONDA_VERISON}-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && /opt/conda/bin/conda clean -tipsy \
    && ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
    # install extras
    # && conda install numba pandas scikit-learn

CMD ["/bin/bash"]
