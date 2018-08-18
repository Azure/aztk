# Jobs
In the Azure Distributed Data Engineering Toolkit,a Job is an entity that runs against an automatically provisioned and managed cluster. Jobs run a collection of Spark applications and and persist the outputs.

------------------------------------------------------


## Creating a Job

Creating a Job starts with defining the necessary properties in your `.aztk/job.yaml` file. Jobs have one or more applications to run as well as values that define the Cluster the applications will run on.

### Job.yaml

Each Job has one or more applications given as a List in Job.yaml. Applications are defined using the following properties:
```yaml
  applications:
    - name:
      application:
      application_args:
        -
      main_class:
      jars:
        -
      py_files:
        -
      files:
        -
      driver_java_options:
        -
      driver_library_path:
      driver_class_path:
      driver_memory:
      executor_memory:
      driver_cores:
      executor_cores:
```
_Please note: the only required fields are name and application. All other fields may be removed or left blank._

NOTE: The Application name can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters. Each application **must** have a unique name.

Jobs also require a definition of the cluster on which the Applications will run. The following properties define a cluster:
```yaml
  cluster_configuration:
    vm_size: <the Azure VM size>
    size: <the number of nodes in the Cluster>
    toolkit:
      software: spark
      version: 2.2
    subnet_id: <resource ID of a subnet to use (optional)>
```
_Please Note: For more information about Azure VM sizes, see [Azure Batch Pricing](https://azure.microsoft.com/en-us/pricing/details/batch/). And for more information about Docker repositories see [Docker](./12-docker-image.html)._

_The only required fields are vm_size and either size or size_low_priority, all other fields can be left blank or removed._

A Job definition may also include a default Spark Configuration. The following are the properties to define a Spark Configuration:
```yaml
  spark_configuration:
    spark_defaults_conf: </path/to/your/spark-defaults.conf>
    spark_env_sh: </path/to/your/spark-env.sh>
    core_site_xml: </path/to/your/core-site.xml>
```
_Please note: including a Spark Configuration is optional. Spark Configuration values defined as part of an application will take precedence over the values specified in these files._


Below we will define a simple, functioning job definition.
```yaml
# Job Configuration

job:
  id: test-job
  cluster_configuration:
    vm_size: standard_f2
    size: 3

  applications:
    - name: pipy100
      application: /path/to/pi.py
      application_args:
        - 100
    - name: pipy200
      application: /path/to/pi.py
      application_args:
        - 200
```
Once submitted, this Job will run two applications, pipy100 and pipy200, on an automatically provisioned Cluster with 3 dedicated Standard_f2 size Azure VMs. Immediately after both pipy100 and pipy200 have completed the Cluster will be destroyed. Application logs will be persisted and available.

### Commands
Submit a Spark Job:

```sh
aztk spark job submit --id <your_job_id> --configuration </path/to/job.yaml>
```

NOTE: The Job id (`--id`) can only contain alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters. Each Job **must** have a unique id.

#### Low priority nodes
You can create your Job with [low-priority](https://docs.microsoft.com/en-us/azure/batch/batch-low-pri-vms) VMs at an 80% discount by using `--size-low-pri` instead of `--size`. Note that these are great for experimental use, but can be taken away at any time. We recommend against this option when doing long running jobs or for critical workloads.


### Listing Jobs
You can list all Jobs currently running in your account by running

```sh
aztk spark job list
```


### Viewing a Job
To view details about a particular Job, run:

```sh
aztk spark job get --id <your_job_id>
```

For example here Job 'pipy' has 2 applications which have already completed.

```sh
Job             pipy
------------------------------------------
State:                              | completed
Transition Time:                    | 21:29PM 11/12/17

Applications                        | State          | Transition Time
------------------------------------|----------------|-----------------
pipy100                             | completed      | 21:25PM 11/12/17
pipy200                             | completed      | 21:24PM 11/12/17
```


### Deleting a Job
To delete a Job run:

```sh
aztk spark job delete --id <your_job_id>
```
Deleting a Job also permanently deletes any data or logs associated with that cluster. If you wish to persist this data, use the `--keep-logs` flag.

__You are only charged for the job while it is active, Jobs handle provisioning and destroying infrastructure, so you are only charged for the time that your applications are running.__


### Stopping a Job
To stop a Job run:

```sh
aztk spark job stop --id <your_job_id>
```
Stopping a Job will end any currently running Applications and will prevent any new Applications from running.


### Get information about a Job's Application
To get information about a Job's Application:

```sh
aztk spark job get-app --id <your_job_id> --name <your_application_name>
```


### Getting a Job's Application's log
To get a job's application logs:

```sh
aztk spark job get-app-logs --id <your_job_id> --name <your_application_name>
```


### Stopping a Job's Application
To stop an application that is running or going to run on a Job:

```sh
aztk spark job stop-app --id <your_job_id> --name <your_application_name>
```
