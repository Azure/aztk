# Configuration Files


## Cluster Configuration

The core settings for a cluster are configured in the cluster.yaml file. Once you have set your desired values in cluster.yaml, you can create a cluster using `azb spark cluster create`. 

For example, with the default cluster configuration:

```yaml
id: my_spark_cluster
vm_size: standard_a2
size: 2
username: spark
wait: true
```

running `azb spark cluster create` will create a cluster of 4 Standard\_A2 nodes called 'my\_spark\_cluster' with a linux user named 'spark'. This is equivalent to running the command

```sh
azb spark cluster create --id spark --vm-szie standard_a2 --size 4 --username spark --wait
```


## Secrets Configuration

A template file for necessary secrets is given in config/secrets.yaml.template. Copy the file to secrets.yaml and fill in the proper values. See [Getting Started] (./00-getting-started.md) for more information.   
