# Submitting an Application
Submitting a job to your Spark cluster in this package mimics the experience of a typical standalone cluster. A spark job will be submitted to the system and run to completion.

## Spark-Submit
The spark-submit experience is mostly the same as any regular Spark cluster with a few minor differences. You can take a look at `aztk spark cluster --help` for more detailed information and options.

Run a Spark job:
```sh
aztk spark cluster submit --id <name_of_spark_cluster> --name <name_of_spark_job> <executable> <executable_params>
```

For example, to run a local pi.py file on a Spark cluster, simply specify the local path of the file:
```sh
aztk spark cluster submit --id spark --name pipy examples/src/main/python/pi.py 100
```

To run a remotely hosted pi.py file on a Spark cluster, specify the remote path of the file and use the '--remote' flag:
```sh
aztk spark cluster submit --id spark --name pipy --remote wasbs://path@remote/pi.py 100
```

NOTE: The job name (--name) must be at least 3 characters long, can only contain alphanumeric characters including hyphens but excluding underscores, and cannot contain uppercase letters. Each job you submit **must** have a unique name.

## Monitoring job
If you have set up a [SSH tunnel](./10-clusters.html#ssh-and-port-forwarding) with port forwarding, you can navigate to http://localhost:8080 and http://localhost:4040 to view the progress of the job using the Spark UI


## Getting output logs
The default setting when running a job is --wait. This will simply submit a job to the cluster and wait for the job to run. If you want to just submit the job and not wait, use the --no-wait flag and tail the logs manually:

```sh
aztk spark cluster submit --id spark --name pipy --no-wait examples/src/main/python/pi.py 1000
```

```sh
aztk spark cluster app-logs --id spark --name pipy --tail
```
