#!/bin/bash

# Entry point for the start task. It will install all dependencies and start docker.
# Usage:
# setup_host.sh [container_name] [docker_repo_name] [docker_run_options]
set -e

export AZTK_WORKING_DIR=/mnt/batch/tasks/startup/wd
export PYTHONUNBUFFERED=TRUE

container_name=$1
docker_repo_name=$2
docker_run_options=$3

install_prerequisites () {
    echo "Installing pre-reqs"

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

    packages=(
        apt-transport-https
        curl
        ca-certificates
        software-properties-common
        python3-pip
        python3-venv
        docker-ce
    )

    echo "running apt-get install -y --no-install-recommends \"${packages[@]}\""
    apt-get -y update &&
    apt-get install -y --no-install-recommends "${packages[@]}"

    if [ $AZTK_GPU_ENABLED == "true" ]; then
        apt-get install -y nvidia-384 nvidia-modprobe
        wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb
        sudo dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb
    fi
    echo "Finished installing pre-reqs"
}

install_docker_compose () {
    echo "Installing Docker-Compose"
    for i in {1..5}; do 
        sudo curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose && break || sleep 2; 
    done
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Finished installing Docker-Compose"
}

pull_docker_container () {
    echo "Pulling $docker_repo_name"

    if [ -z "$DOCKER_USERNAME" ]; then
        echo "No Credentials provided. No need to login to dockerhub"
    else
        echo "Docker credentials provided. Login in."
        docker login $DOCKER_ENDPOINT --username $DOCKER_USERNAME --password $DOCKER_PASSWORD
    fi

    docker pull $docker_repo_name
    echo "Finished pulling $docker_repo_name"
}

install_python_dependencies () {
    echo "Installing python dependencies"
    pipenv install --python /usr/bin/python3.5m
    pipenv run pip install --upgrade pip setuptools wheel
    pip --version
    echo "Finished installing python dependencies"
}

run_docker_container () {
    echo "Running docker container"

    # If the container already exists just restart. Otherwise create it
    if [ "$(docker ps -a -q -f name=$container_name)" ]; then
        echo "Docker container is already setup. Restarting it."
        docker restart $container_name
    else
        echo "Creating docker container."

        echo "Running setup python script"
        $AZTK_WORKING_DIR/.aztk-env/.venv/bin/python $(dirname $0)/main.py setup-node $docker_repo_name "$docker_run_options"

        # wait until container is running
        until [ "`/usr/bin/docker inspect -f {{.State.Running}} $container_name`"=="true" ]; do
            sleep 0.1;
        done;

        # wait until container setup is complete
        echo "Waiting for spark docker container to setup."
        docker exec spark /bin/bash -c '$AZTK_WORKING_DIR/.aztk-env/.venv/bin/python $AZTK_WORKING_DIR/aztk/node_scripts/wait_until_setup_complete.py'

        # Setup symbolic link for the docker logs
        docker_log=$(docker inspect --format='{{.LogPath}}' $container_name)
        mkdir -p $AZ_BATCH_TASK_WORKING_DIR/logs
        ln -s $docker_log $AZ_BATCH_TASK_WORKING_DIR/logs/docker.log
    fi
    echo "Finished running docker container"

}





main () {

    time(
        install_prerequisites
    ) 2>&1


    # set hostname in /etc/hosts if dns cannot resolve
    if ! host $HOSTNAME ; then
        echo $(hostname -I | awk '{print $1}') $HOSTNAME >> /etc/hosts
    fi

    time(
        install_docker_compose
    ) 2>&1

    time(
        pull_docker_container
    ) 2>&1

    # Unzip resource files and set permissions
    chmod 777 $AZTK_WORKING_DIR/aztk/node_scripts/docker_main.sh

    # Check docker is running
    docker info > /dev/null 2>&1
    if [ $? -ne 0 ]; then
    echo "UNKNOWN - Unable to talk to the docker daemon"
    exit 3
    fi

    echo "Node python version:"
    python3 --version

    # set up aztk python environment
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    python3 -m pip install pipenv
    mkdir -p $AZTK_WORKING_DIR/.aztk-env
    cp $AZTK_WORKING_DIR/aztk/node_scripts/Pipfile $AZTK_WORKING_DIR/.aztk-env
    cp $AZTK_WORKING_DIR/aztk/node_scripts/Pipfile.lock $AZTK_WORKING_DIR/.aztk-env
    cd $AZTK_WORKING_DIR/.aztk-env
    export PIPENV_VENV_IN_PROJECT=true

    time(
        install_python_dependencies
    ) 2>&1

    export PYTHONPATH=$PYTHONPATH:$AZTK_WORKING_DIR

    time(
        run_docker_container
    ) 2>&1
}

main
