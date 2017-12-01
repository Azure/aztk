# SDK


Operationalize AZTK with the provided Python SDK.

Find some samples and getting stated tutorial in the `examples/sdk/` directory of the repository.

## Public Interface

### Client

- `create_cluster(self, cluster_conf: aztk.spark.models.ClusterConfiguration, wait=False)`
    
    Create an AZTK cluster with the given cluster configuration

    Parameters:
        
        - cluster_conf: models.ClusterConfiguration
            - the definition of the cluster to create
        - wait: bool = False
            - If true, block until the cluster is running, else return immediately

    Returns:

        - aztk.spark.models.Cluster
        
- `create_clusters_in_parallel(self, cluster_confs: List[aztk.models.ClusterConfiguration])`

    Create an AZTK clusters with the given list of cluster configurations
    
    Parameters:
        
        - cluster_confs: List[aztk.models.ClusterConfiguration]

    Returns:

        - None

- `delete_cluster(self, cluster_id: str)`

    Delete an AZTK cluster with the given ID
    
    Parameters:
        
        - cluster_id: str
            - The ID of the cluster to delete

    Returns:

        - None

- `get_cluster(self, cluster_id: str)`
    Retrieve detailed information about the cluster with the given ID

    Parameters:
        
        - cluster_id
            - the ID of the cluster to get

    Returns:
        
        - aztk.models.Cluster()


- `list_clusters(self)`
    Retrieve a list of existing AZTK clusters.

    Returns:
        
        - List[aztk.models.Cluster]

- `get_remote_login_settings(self, cluster_id: str, node_id: str)`

    Return the settings required to login to a node

    Parameters:
        
        - cluster_id: str
            The cluster to login to
        - node_id: str
            The node to login to
    Returns:
        
        - aztk.spark.models.RemoteLogin

- `submit(self, cluster_id: str, application: aztk.spark.models.Application)`

    Parameters:

        - cluster_id: str
            The cluster that the application is submitted to
        - application: aztk.spark.models.Application
            The application to submit
        
    Returns:

        - None

- `submit_all_applications(self, cluster_id: str, applications: List[aztk.spark.models.Application])`

    Submit a list of applications to be exected on a cluster

    Parameters:

        - cluster_id: str
            The cluster that the applications are submitted to
        - applications: List[aztk.spark.models.Application]    
            List of applications to submit
    Returns:
        
        - None

- `wait_until_application_done(self, cluster_id: str, task_id: str)`

    Block until the given application has completed on the given cluster

    Parameters:
        
        - cluster_id: str
            The cluster on which the application is running
        - task_id
            The application to wait for
    Returns:

        - None

- `wait_until_applications_done(self, cluster_id: str)`

    Block until all applications on the given cluster are completed

    Parameters:
        
        - cluster_id: str
            The cluster on which the application is running

    Returns:

        - None

- `wait_until_cluster_is_ready(self, cluster_id: str)`


    Block until the given cluster is running

    Parameters:
        
        - cluster_id: str
            The ID of the cluster to wait for

    Returns:

        - aztk.spark.models.Cluster

    
- `wait_until_all_clusters_are_ready(self, clusters: List[str])`

    Wait until all clusters in the given list are ready

    Parameters:

        - clusters: List[str]
            A list of the IDs of all the clusters to wait for
    
    Returns:
        
        - None

 - `create_user(self, cluster_id: str, username: str, password: str = None, ssh_key: str = None)`

    Create a user on the given cluster

    Parameters:

        - cluster_id: List[str]
            The cluster on which to create the user

        - password: str
            The password to create the user with (mutually exclusive with ssh_key)
        
        - ssh_key: str
            The ssh_key to create the user with (mutually exclusive with password)
    
    Returns:
        
        - None


- `get_application_log(self, cluster_id: str, application_name: str, tail=False, current_bytes: int = 0)`

    Get the logs of a completed or currently running application

    Parameters:

        - cluster_id: str
            The id of the cluster on which the application ran or is running.

        - application_name: str
            The name of the application to retrieve logs for

        - tail: bool
            Set to true if you want to get only the newly added data after current_bytes.

        - current_bytes: int
            The amount of bytes already retrieved. To get the entire log, leave this at 0. If you are streaming, set this to the current number of bytes you have already retrieved, so you only retrieve the newly added bytes.

    Returns:

        - aztk.spark.models.ApplicationLog

- `get_application_status(self, cluster_id: str, app_name: str)`

    Get the status of an application

    Parameters:
        - cluster_id: str
            The id of the cluster to which the app was submitted

        - app_name
            the name of the application in question
    
    Returns:
        
        - str


### Models

- `Application`
    
    Define a Spark application to run on a cluster.

    Fields:

        - name: str
            Unique identifier for the application. 
    
        - application: str
            Path to the application that will be executed. Can be jar or python file.
     
        - application_args: [str] 
            List of arguments for the application

        - main_class: str
            The application's main class. (Only applies to Java/Scala)
    
        - jars: [str]
            Additional jars to supply for the application.

        - py_files: [str] 
            Additional Python files to supply for the application. Can be .zip, .egg, or .py files.
        - files: [str] 
            Additional files to supply for the application.

        - driver_java_options: str
            Extra Java options to pass to the driver.

        - driver_library_path: str 
            Extra library path entries to pass to the driver.

        - driver_class_path: str 
            Extra class path entries to pass to the driver. Note that jars added with --jars are automatically included in the classpath.

        - driver_memory: str 
            Memory for driver (e.g. 1000M, 2G) (Default: 1024M).

        - executor_memory: str 
            Memory per executor (e.g. 1000M, 2G) (Default: 1G).
            
        - driver_cores: str 
            Cores for driver (Default: 1).

        - executor_cores: str 
            Number of cores per executor. (Default: All available cores on the worker


- `ApplicationLog`
    
    Holds the logged data from a spark application and metadataq about the application and log.

    Fields:
        
        - name: str
        - cluster_id: str
        - log: str
        - total_bytes: int 
        - application_state: str 


- `Cluster`
    
    An AZTK cluster. Note that this model is not used to create a cluster, for that see `ClusterConfiguration`. 

    Fields:
        
        - id: str

            The unique id of the cluster         
        
        - pool: azure.batch.models.CloudPool
        
            A pool in the Azure Batch service.
        
        - nodes: azure.batch.models.ComputeNodePaged
        
            A paging container for iterating over a list of ComputeNode objects
        
        - vm_size: str
        
            The size of virtual machines in the cluster. All virtual machines in a cluster are the same size. For information about available sizes of virtual machines, see Sizes for Virtual Machines (Linux) (https://azure.microsoft.com/documentation/articles/virtual-machines-linux-sizes/). AZTK supports all Azure VM sizes except STANDARD_A0 and those with premium storage (STANDARD_GS, STANDARD_DS, and STANDARD_DSV2 series).
        
        - visible_state
            
            The current state of the cluster. Possible values are: 
            resizing = 'resizing'
            steady = 'steady'
            stopping = 'stopping'
            active = 'active'
            deleting = 'deleting'
            upgrading = 'upgrading'

        - total_current_nodes
            The total number of nodes currently allocated to the cluster.
        
        - total_target_nodes
            The desired number of nodes in the cluster. Sum of target_dedicated_nodes and target_low_pri_nodes.

        - current_dedicated_nodes
            The number of dedicated nodes currently in the cluster.

        - current_low_pri_nodes
            The number of low-priority nodes currently in the cluster. Low-priority nodes which have been preempted are included in this count.
        
        - target_dedicated_nodes 
            The desired number of dedicated nodes in the cluster.
        
        - target_low_pri_nodes
            The desired number of low-priority nodes in the cluster.


- `ClusterConfiguration`
    Define a Spark cluster to be created.

    Fields:

        - custom_scripts: [CustomScript]
            A list of custom scripts to execute in the Spark Docker container.

        - cluster_id: str 
            A unique ID of the cluster to be created. The ID can contain any combination of alphanumeric characters including hyphens and underscores, and cannot contain more than 64 characters. The ID is case-preserving and case-insensitive (that is, you may not have two IDs within an account that differ only by case).

        - vm_count: int
            The number of dedicated VMs (nodes) to be allocated to the cluster. Mutually exclusive with vm_low_pri_count.
        
        - vm_size: str
            The size of virtual machines in the cluster. All virtual machines in a cluster are the same size. For information about available sizes of virtual machines, see Sizes for Virtual Machines (Linux) (https://azure.microsoft.com/documentation/articles/virtual-machines-linux-sizes/). AZTK supports all Azure VM sizes except STANDARD_A0 and those with premium storage (STANDARD_GS, STANDARD_DS, and STANDARD_DSV2 series).

        - vm_low_pri_count: int 
            The number of VMs (nodes) to be allocated to the cluster. Mutually exclusive with vm_count.
        
        - docker_repo: str
            The docker repository and image to use. For more information, see [Docker Image](./12-docker-image.md).
        
        - spark_configuration: aztk.spark.models.SparkConfiguration
            Configuration object for spark-specific values. 


 - `Custom Script`
    A script that executed in the Docker container of specified nodes in the cluster.

        - name: str
            A unique name for the script
        - script: str
            Path to the script to be run
        - run_on: str 
            Set which nodes the script should execute on. Possible values:

                all-nodes
                master
                worker

            Please note that by default, the Master node is also a worker node.


- `SecretsConfiguration`

    The Batch, Storage, Docker and SSH secrets used to create AZTK clusters. For more help with setting these values see [Getting Started](./00-getting-started.md).

    Fields:

        batch_account_name: str 
        batch_account_key: str
        batch_service_url: str

        storage_account_name: str
        storage_account_key: str 
        storage_account_suffix: str

        docker_endpoint: str 
        docker_username: str 
        docker_password: str 

        ssh_pub_key: str 
        ssh_priv_key: str 


- `SparkConfiguration`
    Define cluster-wide Spark specific parameters.

    Fields:

        - spark_defaults_conf: str 
            Path to spark_defaults.conf configuration file to be used.
        
        - spark_env_sh: str
            Path to spark_env.sh configuration file to be used.
        
        - core_site_xml: str
            Path to core-site.xml configuration file to be used.
        
        - jars: [str]
            Additional Jars to be uploaded
 