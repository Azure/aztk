import common.util as util

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import datetime
import random
import argparse

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth 
import azure.batch.models as batch_models
import azure.storage.blob as blob

# config file path
_config_path = os.path.join(os.path.dirname(__file__), 'configuration.cfg')

# generate random number for deployment suffix
_deployment_suffix = str(random.randint(0,1000000))

# ssh user variables
_username = 'admin'
_password = 'pass123!'

# pool configs
_pool_id = '' # required
_job_id = 'az-spark-' + _deployment_suffix
_multiinstance_task_id= 'az-spark-' + _deployment_suffix

# storage container name
_container_name = 'azsparksetup'

# tasks variables
_application_task_name = 'spark-start.sh'
_application_task_path = os.path.join(os.path.dirname(__file__), 'common/resource-files/dsvm-image/spark-start.sh')
_coordination_task_name = 'spark-connect.sh'
_coordination_task_path = os.path.join(os.path.dirname(__file__), 'common/resource-files/dsvm-image/spark-connect.sh')
_user_task_name = ''
_user_task_path = ''

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(prog="az_spark")

    parser.add_argument("--cluster-id", required=True,
                        help="the unique name of your spark cluster")
    parser.add_argument("--job-id", 
                        help="the unique name of your spark job")
    parser.add_argument("--file", required=True, 
                        help="the relative path to your spark job in your directory")
    parser.add_argument("-u", "--user", 
                        help="the relative path to your spark job in your directory")
    parser.add_argument("-p", "--password", 
                        help="the relative path to your spark job in your directory")

    args = parser.parse_args()
    
    print()
    if args.cluster_id is not None:
        _pool_id = args.cluster_id
    print("spark cluster id:      %s" % _pool_id)

    if args.job_id is not None:
        _job_id  = args.job_id
    print("spark job id:          %s" % _job_id)

    if args.file is not None:
        _user_task_path = args.file
        _user_task_name = os.path.basename(_user_task_path)
    print("spark job file path:   %s" % _user_task_path)
    print("spark job file name:   %s" % _user_task_name)

    if args.user is not None:
        _username = args.user
    print("az_spark username:     %s" % _username)

    if args.password is not None:
        _password = args.password
    print("az_spark password:     %s" % _password)
        
    # Read config file
    global_config = configparser.ConfigParser()
    global_config.read(_config_path)

    # Set up the configuration
    batch_account_key = global_config.get('Batch', 'batchaccountkey')
    batch_account_name = global_config.get('Batch', 'batchaccountname')
    batch_service_url = global_config.get('Batch', 'batchserviceurl')
    storage_account_key = global_config.get('Storage', 'storageaccountkey')
    storage_account_name = global_config.get('Storage', 'storageaccountname')
    storage_account_suffix = global_config.get('Storage', 'storageaccountsuffix')

    # Set up SharedKeyCredentials
    credentials = batch_auth.SharedKeyCredentials(
        batch_account_name,
        batch_account_key)

    # Set up Batch Client
    batch_client = batch.BatchServiceClient(
        credentials,
        base_url=batch_service_url)

    # Set retry policy
    batch_client.config.retry_policy.retries = 5

    # Set up BlockBlobStorage
    blob_client = blob.BlockBlobService(
        account_name = storage_account_name,
        account_key = storage_account_key,
        endpoint_suffix = storage_account_suffix)

    # Upload User job resource files to blob storage
    user_job_resource_file = \
        util.upload_file_to_container(
            blob_client, container_name = _job_id, file_path = _user_task_path)
 
    #create job
    job = batch_models.JobAddParameter(
        id = _job_id,
        pool_info=batch_models.PoolInformation(pool_id = _pool_id))

    # add job to batch
    batch_client.job.add(job)

    # configure multi-instance task commands
    coordination_commands = [
        'echo CCP_NODES:',
        'echo $CCP_NODES',
        'echo AZ_BATCH_NODE_LIST:',
        'echo $AZ_BATCH_NODE_LIST',
        'echo AZ_BATCH_HOST_LIST:',
        'echo $AZ_BATCH_HOST_LIST',
        'echo AZ_BATCH_MASTER_NODE:',
        'echo $AZ_BATCH_MASTER_NODE',
        'echo AZ_BATCH_IS_CURRENT_NODE_MASTER:',
        'echo $AZ_BATCH_IS_CURRENT_NODE_MASTER',
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',
        # create a 'slaves' file from the slaves.template in $SPARK_HOME/conf
        'cp $SPARK_HOME/conf/slaves.template $SPARK_HOME/conf/slaves'
        # create a new line in the slaves file
        'echo >> $SPARK_HOME/conf/slaves',
        # add batch pool ips to newly created slaves files
        'IFS="," read -r -a workerips <<< $AZ_BATCH_HOST_LIST',
        'for index in "${!workerips[@]}"',
        'do echo "${workerips[index]}" >> $SPARK_HOME/conf/slaves',
        'echo "${workerips[index]}"',
        'done'
    ]
    application_commands = [
        # set SPARK_HOME environment vars
        'export SPARK_HOME=/dsvm/tools/spark/current',
        'export PATH=$PATH:$SPARK_HOME/bin',
        # kick off start-all spark command as a bg process 
        '($SPARK_HOME/sbin/start-all.sh &)',
        # execute spark-submit on the specified job 
        '$SPARK_HOME/bin/spark-submit ' +
            '--master spark://${AZ_BATCH_MASTER_NODE%:*}:7077 ' +
            '$AZ_BATCH_TASK_WORKING_DIR/' + _user_task_name
    ]

    # get pool target dedicated 
    pool = batch_client.pool.get(_pool_id)
    pool_size = pool.target_dedicated

    # create multi-instance task
    task = batch_models.TaskAddParameter(
        id = _multiinstance_task_id,
        command_line = util.wrap_commands_in_shell(application_commands),
        resource_files = [user_job_resource_file],
        run_elevated = False,
        multi_instance_settings = batch_models.MultiInstanceSettings(
            number_of_instances = pool_size,
            coordination_command_line = util.wrap_commands_in_shell(coordination_commands),
            common_resource_files = []))

    # add task to job
    batch_client.task.add(job_id = _job_id, task = task)

    # wait for the job to finish
    util.wait_for_tasks_to_complete(
        batch_client,
        _job_id,
        datetime.timedelta(minutes=60))

    # get master node id from task
    master_node_id = batch_client.task.get(_job_id, _multiinstance_task_id).node_info.node_id

    # create new ssh user for the master node
    batch_client.compute_node.add_user(
        _pool_id,
        master_node_id,
        batch_models.ComputeNodeUser(
            _username,
            is_admin = True,
            password = _password))

    print('\nuser "{}" added to node "{}"in pool "{}"'.format(_username, master_node_id, _pool_id))

    # get remote login settings for the user
    remote_login_settings = batch_client.compute_node.get_remote_login_settings(
        _pool_id, master_node_id)

    master_node_ip = remote_login_settings.remote_login_ip_address
    master_node_port = remote_login_settings.remote_login_port

    # build ssh tunnel command
    ssh_tunnel_command = "ssh -L 8080:localhost:8080 " + \
        _username + "@" + str(master_node_ip) + " -p " + str(master_node_port)
    print('\nuse the following command to connect to your spark head node:')
    print()
    print('\t%s' % ssh_tunnel_command)
    print()


