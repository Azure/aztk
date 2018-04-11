#!/bin/bash
sudo docker run -d --env-file example.env -p 3000:3000 -v /mnt/batch/tasks/shared/grafana:/var/lib/grafana --name grafana grafana:latest

