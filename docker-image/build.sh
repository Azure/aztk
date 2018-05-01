#/bin/bash

# setup docker to build on /mnt instead of /var/lib/docker
echo '{
    "graph": "/mnt",
    "storage-driver": "overlay"
}' > /etc/docker/daemon.json

service docker restart

mkdir -p out

# base 1.6.3
docker build base/spark1.6.3/ --tag aztk/spark:v0.1.0-spark1.6.3-base > out/base-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-base

# base 2.1.0
docker build base/spark2.1.0/ --tag aztk/spark:v0.1.0-spark2.1.0-base > out/base-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-base

# base 2.2.0
docker build base/spark2.2.0/ --tag aztk/spark:v0.1.0-spark2.2.0-base > out/base-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-base

# base 2.3.0
docker build base/spark2.3.0/ --tag aztk/spark:v0.1.0-spark2.3.0-base > out/base-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-base

# miniconda-base 1.6.3
docker build miniconda/spark1.6.3/base/ --tag aztk/spark:v0.1.0-spark1.6.3-miniconda-base > out/miniconda-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-miniconda-base

# miniconda-base 2.1.0
docker build miniconda/spark2.1.0/base/ --tag aztk/spark:v0.1.0-spark2.1.0-miniconda-base > out/miniconda-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-miniconda-base

# miniconda-base 2.2.0
docker build miniconda/spark2.2.0/base --tag aztk/spark:v0.1.0-spark2.2.0-miniconda-base > out/miniconda-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-miniconda-base

# miniconda-base 2.3.0
docker build miniconda/spark2.3.0/base/ --tag aztk/spark:v0.1.0-spark2.3.0-miniconda-base > out/miniconda-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-miniconda-base

# anaconda-base 1.6.3
docker build anaconda/spark1.6.3/base/ --tag aztk/spark:v0.1.0-spark1.6.3-anaconda-base > out/anaconda-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-anaconda-base

# anaconda-base 2.1.0
docker build anaconda/spark2.1.0/base/ --tag aztk/spark:v0.1.0-spark2.1.0-anaconda-base > out/anaconda-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-anaconda-base

# anaconda-base 2.2.0
docker build anaconda/spark2.2.0/base/ --tag aztk/spark:v0.1.0-spark2.2.0-anaconda-base > out/anaconda-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-anaconda-base

# anaconda-base 2.3.0
docker build anaconda/spark2.3.0/base/ --tag aztk/spark:v0.1.0-spark2.3.0-anaconda-base > out/anaconda-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-anaconda-base

# r-base 1.6.3
docker build r/spark1.6.3/base/ --tag aztk/spark:v0.1.0-spark1.6.3-r-base > out/r-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-r-base

# r-base 2.1.0
docker build r/spark2.1.0/base/ --tag aztk/spark:v0.1.0-spark2.1.0-r-base > out/r-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-r-base

# r-base 2.2.0
docker build r/spark2.2.0/base/ --tag aztk/spark:v0.1.0-spark2.2.0-r-base > out/r-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-r-base

# r-base 2.3.0
docker build r/spark2.3.0/base/ --tag aztk/spark:v0.1.0-spark2.3.0-r-base > out/r-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-r-base

##################
#      GPU       #
##################

# gpu 1.6.3
docker build gpu/spark1.6.3/ --tag aztk/spark:v0.1.0-spark1.6.3-gpu > out/gpu-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-gpu

# gpu 2.1.0
docker build gpu/spark2.1.0/ --tag aztk/spark:v0.1.0-spark2.1.0-gpu > out/gpu-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-gpu

# gpu 2.2.0
docker build gpu/spark2.2.0/ --tag aztk/spark:v0.1.0-spark2.2.0-gpu > out/gpu-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-gpu

# gpu 2.3.0
docker build gpu/spark2.3.0/ --tag aztk/spark:v0.1.0-spark2.3.0-gpu > out/gpu-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-gpu

# miniconda-gpu 1.6.3
docker build miniconda/spark1.6.3/gpu/ --tag aztk/spark:v0.1.0-spark1.6.3-miniconda-gpu > out/miniconda-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-miniconda-gpu

# miniconda-gpu 2.1.0
docker build miniconda/spark2.1.0/gpu/ --tag aztk/spark:v0.1.0-spark2.1.0-miniconda-gpu > out/miniconda-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-miniconda-gpu

# miniconda-gpu 2.2.0
docker build miniconda/spark2.2.0/gpu --tag aztk/spark:v0.1.0-spark2.2.0-miniconda-gpu > out/miniconda-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-miniconda-gpu

# miniconda-gpu 2.3.0
docker build miniconda/spark2.3.0/gpu/ --tag aztk/spark:v0.1.0-spark2.3.0-miniconda-gpu > out/miniconda-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-miniconda-gpu

# anaconda-gpu 1.6.3
docker build anaconda/spark1.6.3/gpu/ --tag aztk/spark:v0.1.0-spark1.6.3-anaconda-gpu > out/anaconda-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-anaconda-gpu

# anaconda-gpu 2.1.0
docker build anaconda/spark2.1.0/gpu/ --tag aztk/spark:v0.1.0-spark2.1.0-anaconda-gpu > out/anaconda-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-anaconda-gpu

# anaconda-gpu 2.2.0
docker build anaconda/spark2.2.0/gpu/ --tag aztk/spark:v0.1.0-spark2.2.0-anaconda-gpu > out/anaconda-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-anaconda-gpu

# anaconda-gpu 2.3.0
docker build anaconda/spark2.3.0/gpu/ --tag aztk/spark:v0.1.0-spark2.3.0-anaconda-gpu > out/anaconda-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-anaconda-gpu

# r-gpu 1.6.3
docker build r/spark1.6.3/gpu/ --tag aztk/spark:v0.1.0-spark1.6.3-r-gpu > out/r-spark1.6.3.out &&
docker push aztk/spark:v0.1.0-spark1.6.3-r-gpu

# r-gpu 2.1.0
docker build r/spark2.1.0/gpu/ --tag aztk/spark:v0.1.0-spark2.1.0-r-gpu > out/r-spark2.1.0.out &&
docker push aztk/spark:v0.1.0-spark2.1.0-r-gpu

# r-gpu 2.2.0
docker build r/spark2.2.0/gpu/ --tag aztk/spark:v0.1.0-spark2.2.0-r-gpu > out/r-spark2.2.0.out &&
docker push aztk/spark:v0.1.0-spark2.2.0-r-gpu

# r-gpu 2.3.0
docker build r/spark2.3.0/gpu/ --tag aztk/spark:v0.1.0-spark2.3.0-r-gpu > out/r-spark2.3.0.out &&
docker push aztk/spark:v0.1.0-spark2.3.0-r-gpu
