# R
This Dockerfile is used to build the __aztk-r__ Docker image used by this toolkit. This image uses R and RStudio Server, providing access to a wide range of popular R packages.

You can modify these Dockerfiles to build your own image. However, in mose cases, building on top of the __aztk-vanilla__ image is recommended.

## How to build this image
This Dockerfile takes in two variables at build time that allow you to specify your desired Rstudio server versions and R versions: **RSTUDIO_SERVER_VERSION** and **R_VERSION**

By default, we set **R_VERSION=3.4.2** and **RSTUDIO_SERVER_VERSION=1.1.383**.

For example, if I wanted to use Rstudio Server v1.1.383 and R 3.2.1 with Spark v2.1.0, I would select the appropriate Dockerfile and build the image as follows:
```sh
# spark2.1.0/Dockerfile
docker build \
    --build-arg RSTUDIO_SERVER_VERSION=1.1.383 \
    --build-arg R_VERSION=3.2.1 \
    -t <my_image_tag> .
```

**R_VERSION** is used to set the version of R version for your cluster. 
**RSTUDIO_SERVER_VERSION** is used to set the version of rstudio server for your cluster. 