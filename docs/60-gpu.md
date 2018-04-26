# GPU

Use GPUs to accelerate your Spark applications. When using a [GPU enabled Azure VM](https://azure.microsoft.com/en-us/pricing/details/batch/), your docker image will contain CUDA-8.0 and cuDnn-6.0 by default. See [Docker Image](./12-docker-image.html) for more information about the AZTK Docker images.

[NOTE: Azure does not have GPU enabled VMs in all regions. Please use this [link](https://azure.microsoft.com/en-us/pricing/details/batch/) to make sure that your Batch account is in a region that has GPU enabled VMs]

AZTK uses Nvidia-Docker to expose the VM's GPU(s) inside the container. Nvidia drivers (ver. 384) are installed at runtime.


### Tutorial

Create a cluster specifying a GPU enabled VM
```sh
aztk spark cluster create --id gpu-cluster --vm-size standard_nc6 --size 1
```

Submit your an application to the cluster that will take advantage of the GPU
```sh
aztk spark cluster submit --id gpu-cluster --name gpu-app ./examples/src/main/python/gpu/nubma_example.py
```
### Installation Location
By default, CUDA is installed at `/usr/local/cuda-8.0`.
