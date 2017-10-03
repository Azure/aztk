#!/bin/bash

# Entry point for the start task. It will install all dependencies and start docker.
# Usage:
# setup_node.sh [container_name] [docker_repo] [docker_cmd]


container_name=$1
repo_name=$2
docker_run_cmd=$3

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

if [ -z "$DOCKER_USERNAME" ]; then
    echo "No Credentials provided. No need to login to dockerhub $DOCKER_USERNAME $DOCKER_PASSWORD"
else
    echo "Docker credentials provided. Login in."
    docker login $docker_endpoint --username $DOCKER_USERNAME --password $DOCKER_PASSWORD
fi

if [ -z "$DOCKER_ENDPOINT" ]; then
    echo "Pulling $repo_name from dockerhub"
    docker pull $repo_name
else
    echo "Pulling $container_name from $DOCKER_ENDPOINT"
    docker pull $DOCKER_ENDPOINT/$repo_name
fi

# Unzip resource files and set permissions
apt-get -y install unzip
chmod 777 $AZ_BATCH_TASK_WORKING_DIR/docker_main.sh
chmod -R 777 $AZ_BATCH_TASK_WORKING_DIR/custom-scripts

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

    # Setup symbolic link for the docker logs
    docker_log=$(docker inspect --format='{{.LogPath}}' $container_name)
    mkdir -p $AZ_BATCH_TASK_WORKING_DIR/logs
    ln -s $docker_log $AZ_BATCH_TASK_WORKING_DIR/logs/docker.log
fi
