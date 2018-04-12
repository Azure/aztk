#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install pip requirements
echo "Install pip requirements  "
pip3 install -r requirements.txt

if  [ "$AZTK_IS_MASTER" = "1" ]; then
    echo "Create the database and grafana containers"
    sudo docker-compose up --no-start
    echo "Run the containers"
    sudo docker-compose start
fi

echo "Run nodestats in background"
sudo touch nodestats.out
sudo chmod 777 nodestats.out
sudo python3 $DIR/nodestats.py > nodestats.out 2>&1 $AZTK_MASTER_IP &
