# Submitting a Job
Submitting a job to your Spark cluster in Thunderbolt mimics the experience of a typical standalone cluster. A spark job will be submitted to the system and run to completion.

## Spark-Submit
The spark-submit experience is mostly the same as any regular Spark cluster with a few minor differences. You can take a look at azb spark cluster --help for more detailed information and options.

Run a Spark job:
```sh
azb spark cluster submit --id <name_of_spark_cluster> --name <name_of_spark_job> <executable> <executable_params>
```

For example, run a local pi.py file on a Spark cluster
```sh
azb spark cluster submit --id spark --name pipy example-jobs/python/pi.py 100
```

NOTE: The job name (--name) must be atleast 3 characters long, can only contain alphanumeric characters including hyphens but excluding underscores, and cannot contain uppercase letters.

## Monitoring job
If you have set up a [SSH tunnel](./10-clusters.md#SSH%20and%20Port%20Forwarding) with port fowarding, you can naviate to http://localhost:8080 and http://localhost:4040 to view the progess of the job using the Spark UI


## Getting output logs
The default setting when running a job is --wait. This will simply submit a job to the cluster and wait for the job to run. If you want to just submit the job and not wait, use the --no-wait flag and tail the logs manually:

```sh
azb spark cluster submit --id spark --name pipy --no-wait example-jobs/pi.py 1000
```

```sh
azb spark app logs --id spark --name pipy --tail
```
