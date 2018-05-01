FROM aztk/spark:v0.1.0-spark1.6.3-base

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

RUN  mkdir -p /usr/lib/R/etc/ \
  && echo "options(repos = c(CRAN = 'https://cran.rstudio.com/'), download.file.method = 'libcurl')" >> /usr/lib/R/etc/Rprofile.site \
  ## Add a library directory (for user-installed packages)
  && mkdir -p /usr/lib/R/site-library \
  ## Fix library path
  && echo "R_LIBS_USER='/usr/lib/R/site-library'" >> /usr/lib/R/etc/Renviron \
  && echo "R_LIBS=\${R_LIBS-'/usr/lib/R/site-library:/usr/lib/R/library:/usr/lib/R/library'}" >> /usr/lib/R/etc/Renviron \
  ## install packages from date-locked MRAN snapshot of CRAN
  && [ -z "$BUILD_DATE" ] && BUILD_DATE=$(TZ="America/Los_Angeles" date -I) || true \
  && MRAN=https://mran.microsoft.com/snapshot/${BUILD_DATE} \
  && echo MRAN=$MRAN >> /etc/environment \
  && export MRAN=$MRAN \
  && echo "options(repos = c(CRAN='$MRAN'), download.file.method = 'libcurl'); Sys.setenv(SPARK_HOME ='"$SPARK_HOME"')" >> /usr/lib/R/etc/Rprofile.site \
  ## Use littler installation scripts
  && Rscript -e "install.packages(c('dplyr', 'docopt', 'tidyverse', 'sparklyr'), repo = '$MRAN', dependencies=TRUE)" \
  && chown -R root:staff /usr/lib/R/site-library \
  && chmod -R g+wx /usr/lib/R/site-library \
  && ln -s /usr/lib/R/site-library/littler/examples/install2.r /usr/local/bin/install2.r \
  && ln -s /usr/lib/R/site-library/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
  && ln -s /usr/lib/R/site-library/littler/bin/r /usr/local/bin/r \
  ## Clean up from R source install
  && cd / \
  && rm -rf /tmp/* \
  && apt-get autoremove -y \
  && apt-get autoclean -y

RUN rm /usr/bin/python \
  && ln -s /usr/bin/python3.5 /usr/bin/python

RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
  && locale-gen en_US.utf8 \
  && /usr/sbin/update-locale LANG=en_US.UTF-8

CMD ["/bin/bash"]
