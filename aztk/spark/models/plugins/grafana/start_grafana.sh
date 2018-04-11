#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
sudo docker run -d --env-file $DIR/example.env -p 3000:3000 -v /mnt/batch/tasks/shared/grafana:/var/lib/grafana --name grafana grafana/grafana:latest

