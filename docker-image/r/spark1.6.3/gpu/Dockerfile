# Ubuntu 16.04 (Xenial)
FROM aztk/gpu:spark1.6.3

# modify these ARGs on build time to specify your desired versions of Spark/Hadoop
ARG R_VERSION=3.4.1
ARG RSTUDIO_SERVER_VERSION=1.1.383
ARG TENSORFLOW_VERSION=tensorflow-gpu
ARG CNTK_VERSION=https://cntk.ai/PythonWheel/GPU/cntk-2.3.1-cp35-cp35m-linux_x86_64.whl
ARG BUILD_DATE

# set env vars
ENV DEBIAN_FRONTEND noninteractive
ENV BUILD_DATE ${BUILD_DATE:-}
ENV RSTUDIO_SERVER_VERSION $RSTUDIO_SERVER_VERSION
ENV R_VERSION $R_VERSION

RUN  useradd -m -d /home/rstudio rstudio -G sudo,staff \
  && echo rstudio:rstudio | chpasswd \
  && chmod -R 777 /home/rstudio \
  && chmod -R 777 //.pyenv/

# Setting up rstudio user with Tensorflow and CNTK
USER rstudio
RUN  echo "PATH='"$PATH"'" > /home/rstudio/.Renviron \
  && pip3 install \
    $CNTK_VERSION \
    $TENSORFLOW_VERSION \
    keras

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash-completion \
    ca-certificates \
    file \
    fonts-texgyre \
    g++ \
    gfortran \
    gsfonts \
    libcurl3 \
    libopenblas-dev \
    libpangocairo-1.0-0 \
    libpng16-16 \
    locales \
    make \
    unzip \
    zip \
    libcurl4-openssl-dev \
    libxml2-dev \
    libapparmor1 \
    gdebi-core \
    lsb-release \
    psmisc \
    sudo \
    openmpi-bin \
  && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
  && locale-gen en_US.utf8 \
  && /usr/sbin/update-locale LANG=en_US.UTF-8 \
  && BUILDDEPS="libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    libicu-dev \
    libpcre3-dev \
    libpng-dev \
    libtiff5-dev \
    liblzma-dev \
    libx11-dev \
    libxt-dev \
    perl \
    tcl8.6-dev \
    tk8.6-dev \
    texinfo \
    texlive-extra-utils \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-recommended \
    x11proto-core-dev \
    xauth \
    xfonts-base \
    xvfb" \
  && apt-get install -y --no-install-recommends $BUILDDEPS \
  ## Download source code
  && cd /tmp/ \
  && majorVersion=$(echo $R_VERSION | cut -f1 -d.) \
  && curl -O https://cran.r-project.org/src/base/R-${majorVersion}/R-${R_VERSION}.tar.gz \
  ## Extract source code
  && tar -xf R-${R_VERSION}.tar.gz \
  && cd R-${R_VERSION} \
  ## Set compiler flags
  && R_PAPERSIZE=letter \
    R_BATCHSAVE="--no-save --no-restore" \
    R_BROWSER=xdg-open \
    PAGER=/usr/bin/pager \
    PERL=/usr/bin/perl \
    R_UNZIPCMD=/usr/bin/unzip \
    R_ZIPCMD=/usr/bin/zip \
    R_PRINTCMD=/usr/bin/lpr \
    LIBnn=lib \
    AWK=/usr/bin/awk \
    CFLAGS="-g -O2 -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2 -g" \
    CXXFLAGS="-g -O2 -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2 -g" \
  ## Configure options
  ./configure --enable-R-shlib \
               --enable-memory-profiling \
               --with-readline \
               --with-blas="-lopenblas" \
               --disable-nls \
               --without-recommended-packages \
  ## Build and install
  && make \
  && make install \
  ## Add a default CRAN mirror
  && echo "options(repos = c(CRAN = 'https://cran.rstudio.com/'), download.file.method = 'libcurl')" >> /usr/local/lib/R/etc/Rprofile.site \
  ## Add a library directory (for user-installed packages)
  && mkdir -p /usr/local/lib/R/site-library \
  && chown root:staff /usr/local/lib/R/site-library \
  && chmod g+wx /usr/local/lib/R/site-library \
  ## Fix library path
  && echo "R_LIBS_USER='/usr/local/lib/R/site-library'" >> /usr/local/lib/R/etc/Renviron \
  && echo "R_LIBS=\${R_LIBS-'/usr/local/lib/R/site-library:/usr/local/lib/R/library:/usr/lib/R/library'}" >> /usr/local/lib/R/etc/Renviron \
  ## install packages from date-locked MRAN snapshot of CRAN
  && [ -z "$BUILD_DATE" ] && BUILD_DATE=$(TZ="America/Los_Angeles" date -I) || true \
  && MRAN=https://mran.microsoft.com/snapshot/${BUILD_DATE} \
  && echo MRAN=$MRAN >> /etc/environment \
  && export MRAN=$MRAN \
  && echo "options(repos = c(CRAN='$MRAN'), download.file.method = 'libcurl');" >> /usr/local/lib/R/etc/Rprofile.site \
  && echo "Sys.setenv(SPARK_HOME ='"$SPARK_HOME"');" >> /usr/local/lib/R/etc/Rprofile.site \
  && Rscript -e "install.packages(c('littler', 'docopt', 'tidyverse', 'sparklyr', 'keras', 'tensorflow'), repo = '$MRAN')" \
  && ln -s /usr/local/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
  && ln -s /usr/local/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
  && ln -s /usr/local/lib/R/site-library/littler/bin/r /usr/local/bin/r \
  ## TEMPORARY WORKAROUND to get more robust error handling for install2.r prior to littler update
  && curl -O /usr/local/bin/install2.r https://github.com/eddelbuettel/littler/raw/master/inst/examples/install2.r \
  && chmod +x /usr/local/bin/install2.r \
  ## Clean up from R source install
  && cd / \
  && rm -rf /tmp/* \
  && apt-get autoremove -y \
  && apt-get autoclean -y \
  && rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
