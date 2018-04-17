# Ubuntu 16.04 (Xenial)
FROM aztk/staging:spark2.2.0-hadoop2.8.3-nopyenv

# modify these ARGs on build time to specify your desired versions of Spark/Hadoop
ARG R_VERSION=3.4.1
ARG RSTUDIO_SERVER_VERSION=1.1.383
ARG BUILD_DATE

# set env vars
ENV DEBIAN_FRONTEND noninteractive
ENV BUILD_DATE ${BUILD_DATE:-}
ENV RSTUDIO_SERVER_VERSION $RSTUDIO_SERVER_VERSION
ENV R_VERSION $R_VERSION

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
  && cd tmp/ \
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
  && touch /usr/local/lib/R/etc/Rprofile.site \
  && echo "options(repos = c(CRAN = 'https://cran.rstudio.com/'), download.file.method = 'libcurl')" >> /usr/local/lib/R/etc/Rprofile.site \
  ## Add a library directory (for user-installed packages)
  && mkdir -p /usr/local/lib/R/site-library \
  ## Fix library path
  && echo "R_LIBS_USER='/usr/local/lib/R/site-library'" >> /usr/local/lib/R/etc/Renviron \
  && echo "R_LIBS=\${R_LIBS-'/usr/local/lib/R/site-library:/usr/local/lib/R/library:/usr/lib/R/library'}" >> /usr/local/lib/R/etc/Renviron \
  ## install packages from date-locked MRAN snapshot of CRAN
  && [ -z "$BUILD_DATE" ] && BUILD_DATE=$(TZ="America/Los_Angeles" date -I) || true \
  && MRAN=https://mran.microsoft.com/snapshot/${BUILD_DATE} \
  && echo MRAN=$MRAN >> /etc/environment \
  && export MRAN=$MRAN \
  && echo "options(repos = c(CRAN='$MRAN'), download.file.method = 'libcurl'); Sys.setenv(SPARK_HOME ='"$SPARK_HOME"')" >> /usr/local/lib/R/etc/Rprofile.site \
  ## Use littler installation scripts
  && Rscript -e "install.packages(c('littler', 'docopt', 'tidyverse', 'sparklyr'), repo = '$MRAN')" \
  && chown -R root:staff /usr/local/lib/R/site-library \
  && chmod -R g+wx /usr/local/lib/R/site-library \
  && ln -s /usr/local/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
  && ln -s /usr/local/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
  && ln -s /usr/local/lib/R/site-library/littler/bin/r /usr/local/bin/r \
  ## TEMPORARY WORKAROUND to get more robust error handling for install2.r prior to littler update
  && curl -O /usr/local/bin/install2.r https://github.com/eddelbuettel/littler/raw/master/inst/examples/install2.r \
  && chmod +x /usr/local/bin/install2.r \
  ## Clean up from R source install
  && cd / \
  && rm -rf /tmp/* \
  # reset default python
  && rm /usr/bin/python \
  && ln -s /usr/bin/python3.5 /usr/bin/python \
  && apt-get autoremove -y \
  && apt-get autoclean -y \
  && rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]


## REFACTOR ##
FROM aztk/staging:spark2.2.0-hadoop2.8.3-nopyenv

ARG R_VERSION=3.4.4
ARG R_BASE_VERSION=${R_VERSION}-1xenial0
ARG BUILD_DATE

RUN apt-get update \
  && apt-get install -y --no-install-recommends apt-transport-https \
        libxml2-dev \
        libcairo2-dev \
        libsqlite-dev \
        libmariadbd-dev \
        libmariadb-client-lgpl-dev \
        libpq-dev \
        libssh2-1-dev \
        libcurl4-openssl-dev \
        locales \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 \
  && add-apt-repository 'deb [arch=amd64,i386] https://cran.rstudio.com/bin/linux/ubuntu xenial/' \
  && apt-get update \
  && apt-get install -y --no-install-recommends r-base=${R_BASE_VERSION} r-base-dev=${R_BASE_VERSION}

RUN  mkdir /usr/local/lib/R/etc/ \
  && touch /usr/local/lib/R/etc/Rprofile.site \
  && echo "options(repos = c(CRAN = 'https://cran.rstudio.com/'), download.file.method = 'libcurl')" >> /usr/local/lib/R/etc/Rprofile.site \
  ## Add a library directory (for user-installed packages)
  && mkdir -p /usr/local/lib/R/site-library \
  ## Fix library path
  && echo "R_LIBS_USER='/usr/local/lib/R/site-library'" >> /usr/local/lib/R/etc/Renviron \
  && echo "R_LIBS=\${R_LIBS-'/usr/local/lib/R/site-library:/usr/local/lib/R/library:/usr/lib/R/library'}" >> /usr/local/lib/R/etc/Renviron \
  ## install packages from date-locked MRAN snapshot of CRAN
  && [ -z "$BUILD_DATE" ] && BUILD_DATE=$(TZ="America/Los_Angeles" date -I) || true \
  && MRAN=https://mran.microsoft.com/snapshot/${BUILD_DATE} \
  && echo MRAN=$MRAN >> /etc/environment \
  && export MRAN=$MRAN \
  && echo "options(repos = c(CRAN='$MRAN'), download.file.method = 'libcurl'); Sys.setenv(SPARK_HOME ='"$SPARK_HOME"')" >> /usr/local/lib/R/etc/Rprofile.site \
  ## Use littler installation scripts
  && Rscript -e "install.packages(c('dplyr', 'docopt', 'tidyverse', 'sparklyr'), repo = '$MRAN', dependencies=TRUE)" \
  && chown -R root:staff /usr/local/lib/R/site-library \
  && chmod -R g+wx /usr/local/lib/R/site-library \
  && ln -s /usr/local/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
  && ln -s /usr/local/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
  && ln -s /usr/local/lib/R/site-library/littler/bin/r /usr/local/bin/r \
  ## Clean up from R source install
  && cd / \
  && rm -rf /tmp/* \
  && apt-get autoremove -y \
  && apt-get autoclean -y

RUN rm /usr/bin/python \
  && ln -s /usr/bin/python3.5 /usr/bin/python


CMD ["/bin/bash"]
