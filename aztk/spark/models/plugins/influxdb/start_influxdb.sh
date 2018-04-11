#!/bin/bash
sudo docker run -d --env-file example.env --env INFLUXDB_ADMIN_ENABLED=true -p 8086:8086 -p 8090:8090 -p 8083:8083 -v /mnt/batch/tasks/shared:/var/lib/influxdb --name influxdb influxdb:latest

