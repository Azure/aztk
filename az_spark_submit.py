import redbull.sparklib as sparklib

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

if __name__ == '__main__':

    _pool_id = None
    _job_id = 'az-spark-' + _deployment_suffix
    _job_file_name = None
    _job_file_path = None
    _username = 'admin'
    _password = 'pass123!'

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
        _job_file_path = args.file
        _job_file_name = os.path.basename(_job_file_path)
    print("spark job file path:   %s" % _job_file_path)
    print("spark job file name:   %s" % _job_file_name)

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

    # submit job
    sparklib.submit_job(
        batch_client,
        blob_client,
        pool_id = _pool_id,
        job_id = _job_id,
        job_file_name = _job_file_name,
        job_file_path = os.path.join(os.path.dirname(__file__), _job_file_path),
        username = _username,
        password = _password)

