# Python
This Dockerfile is used to build the __aztk-python__ Docker image used by this toolkit. This image uses Anaconda, providing access to a wide range of popular python packages.

You can modify these Dockerfiles to build your own image. However, in mose cases, building on top of the __aztk-base__ image is recommended.

NOTE: If you plan to use Jupyter Notebooks with your Spark cluster, we recommend using this image as Jupyter Notebook comes pre-installed with Anaconda. 

## How to build this image
This Dockerfile takes in a variable at build time that allow you to specify your desired Anaconda versions: **ANACONDA_VERSION** 

By default, we set **ANACONDA_VERSION=anaconda3-5.0.0**.

For example, if I wanted to use Anaconda3 v5.0.0 with Spark v2.1.0, I would select the appropriate Dockerfile and build the image as follows:
```sh
# spark2.1.0/Dockerfile
docker build \
    --build-arg ANACONDA_VERSION=anaconda3-5.0.0 \
    -t <my_image_tag> .
```

**ANACONDA_VERSION** is used to set the version of Anaconda for your cluster. 

NOTE: Most versions of Python will work. However, when selecting your Python version, please make sure that the it is compatible with your selected version of Spark. 
