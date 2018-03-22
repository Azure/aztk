#!/bin/bash

# Entry point for the start task. It will install all dependencies and start docker.
# Usage:
# setup_node.sh [container_name] [gpu_enabled] [docker_repo] [docker_cmd]


container_name=$1
gpu_enabled=$2
repo_name=$3
docker_run_cmd=$4

apt-get -y install linux-image-extra-$(uname -r) linux-image-extra-virtual
apt-get -y install apt-transport-https
apt-get -y install curl
apt-get -y install ca-certificates
apt-get -y install software-properties-common

# Install docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get -y update
apt-get -y install docker-ce

if [ $gpu_enabled == "True" ]; then
    echo "running nvidia install"
    sudo apt-get -y install nvidia-384
    sudo apt-get -y install nvidia-modprobe

    wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb
    sudo dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb
    echo "nvidia install complete"
fi

if [ -z "$DOCKER_USERNAME" ]; then
    echo "No Credentials provided. No need to login to dockerhub"
else
    echo "Docker credentials provided. Login in."
    docker login $DOCKER_ENDPOINT --username $DOCKER_USERNAME --password $DOCKER_PASSWORD
fi

echo "Pulling $repo_name"
(time docker pull $repo_name) 2>&1

# Unzip resource files and set permissions
apt-get -y install unzip
chmod 777 $AZ_BATCH_TASK_WORKING_DIR/aztk/node_scripts/docker_main.sh

# Check docker is running
docker info > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "UNKNOWN - Unable to talk to the docker daemon"
  exit 3
fi

# If the container already exists just restart. Otherwise create it
if [ "$(docker ps -a -q -f name=$container_name)" ]; then
    echo "Docker container is already setup. Restarting it."
    docker restart $container_name
else
    echo "Creating docker container."
    # Start docker
    eval $docker_run_cmd

    # wait until container is running
    until [ "`/usr/bin/docker inspect -f {{.State.Running}} $container_name`"=="true" ]; do
        sleep 0.1;
    done;

    # wait until container setup is complete
    docker exec spark /bin/bash -c 'python $DOCKER_WORKING_DIR/aztk/node_scripts/wait_until_setup_complete.py'

    # Setup symbolic link for the docker logs
    docker_log=$(docker inspect --format='{{.LogPath}}' $container_name)
    mkdir -p $AZ_BATCH_TASK_WORKING_DIR/logs
    ln -s $docker_log $AZ_BATCH_TASK_WORKING_DIR/logs/docker.log
fi
