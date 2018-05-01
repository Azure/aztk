#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

mkdir /etc/telegraf
cp ./etc/telegraf.conf /etc/telegraf/telegraf.conf

echo "Install telegraf"
curl -sL https://repos.influxdata.com/influxdb.key | apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | tee /etc/apt/sources.list.d/influxdb.list
apt-get update && apt-get install telegraf

if  [ "$AZTK_IS_MASTER" = "true" ]; then
    echo "Create docker containers"
    sudo docker-compose up --no-start
    echo "Run the containers"
    sudo docker-compose start
fi

echo "Run telegraf"
telegraf --config ./etc/telegraf.conf &
