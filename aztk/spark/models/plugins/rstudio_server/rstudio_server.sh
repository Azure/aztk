#!/bin/bash

# This custom script only works on images where rstudio server is pre-installed on the Docker image
#
# This custom script has been tested to work on the following docker images:
#  - jiata/aztk-r:0.1.0-spark2.2.0-r3.4.1
#  - jiata/aztk-r:0.1.0-spark2.1.0-r3.4.1
#  - jiata/aztk-r:0.1.0-spark1.6.3-r3.4.1

if  [ "$AZTK_IS_MASTER" = "true" ]; then

    ## Download and install Rstudio Server
    wget https://download2.rstudio.org/rstudio-server-$RSTUDIO_SERVER_VERSION-amd64.deb
    apt-get install -y --no-install-recommends gdebi-core
    gdebi rstudio-server-$RSTUDIO_SERVER_VERSION-amd64.deb --non-interactive
    echo "server-app-armor-enabled=0" | tee -a /etc/rstudio/rserver.conf
    rm rstudio-server-$RSTUDIO_SERVER_VERSION-amd64.deb

    ## Preparing default user for Rstudio Server
    set -e
    useradd -m -d /home/rstudio rstudio -g staff
    echo rstudio:rstudio | chpasswd

    rstudio-server start

fi
