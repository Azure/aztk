import datetime
import logging
import os
import subprocess
import sys
from typing import List

import azure.batch.models as batch_models
import azure.storage.blob as blob
import yaml

from aztk.utils.command_builder import CommandBuilder
from core import config

# limit azure.storage logging
logging.getLogger("azure.storage").setLevel(logging.CRITICAL)
"""
Submit helper methods
"""


def upload_file_to_container(container_name,
                             application_name,
                             file_path,
                             blob_client=None,
                             use_full_path=False,
                             node_path=None) -> batch_models.ResourceFile:
    """
    Uploads a local file to an Azure Blob storage container.
    :param blob_client: A blob service client.
    :type blocblob_clientk_blob_client: `azure.storage.blob.BlockBlobService`
    :param str container_name: The name of the Azure Blob storage container.
    :param str file_path: The local path to the file.
    :param str node_path: Path on the local node. By default will be the same as file_path
    :rtype: `azure.batch.models.ResourceFile`
    :return: A ResourceFile initialized with a SAS URL appropriate for Batch
    tasks.
    """
    file_path = file_path
    blob_name = None
    if use_full_path:
        blob_name = file_path.strip("/")
    else:
        blob_name = os.path.basename(file_path)
        blob_path = application_name + "/" + blob_name

    if not node_path:
        node_path = blob_name

    blob_client.create_container(container_name, fail_on_exist=False)

    blob_client.create_blob_from_path(container_name, blob_path, file_path)

    sas_token = blob_client.generate_blob_shared_access_signature(
        container_name,
        blob_path,
        permission=blob.BlobPermissions.READ,
        expiry=datetime.datetime.utcnow() + datetime.timedelta(days=7),
    )

    sas_url = blob_client.make_blob_url(container_name, blob_path, sas_token=sas_token)

    return batch_models.ResourceFile(file_path=node_path, blob_source=sas_url)


def __app_submit_cmd(
        name: str,
        app: str,
        app_args: List[str],
        main_class: str,
        jars: List[str],
        py_files: List[str],
        files: List[str],
        driver_java_options: str,
        driver_library_path: str,
        driver_class_path: str,
        driver_memory: str,
        executor_memory: str,
        driver_cores: int,
        executor_cores: int,
):
    spark_home = os.environ["SPARK_HOME"]
    with open(os.path.join(spark_home, "conf", "master")) as f:
        master_ip = f.read().rstrip()

    # set file paths to correct path on container
    files_path = os.environ["AZ_BATCH_TASK_WORKING_DIR"]
    jars = [os.path.join(files_path, os.path.basename(jar)) for jar in jars]
    py_files = [os.path.join(files_path, os.path.basename(py_file)) for py_file in py_files]
    files = [os.path.join(files_path, os.path.basename(f)) for f in files]

    # 2>&1 redirect stdout and stderr to be in the same file
    spark_submit_cmd = CommandBuilder("{0}/bin/spark-submit".format(spark_home))
    spark_submit_cmd.add_option("--master", "spark://{0}:7077".format(master_ip))
    spark_submit_cmd.add_option("--name", name)
    spark_submit_cmd.add_option("--class", main_class)
    spark_submit_cmd.add_option("--jars", jars and ",".join(jars))
    spark_submit_cmd.add_option("--py-files", py_files and ",".join(py_files))
    spark_submit_cmd.add_option("--files", files and ",".join(files))
    spark_submit_cmd.add_option("--driver-java-options", driver_java_options)
    spark_submit_cmd.add_option("--driver-library-path", driver_library_path)
    spark_submit_cmd.add_option("--driver-class-path", driver_class_path)
    spark_submit_cmd.add_option("--driver-memory", driver_memory)
    spark_submit_cmd.add_option("--executor-memory", executor_memory)
    if driver_cores:
        spark_submit_cmd.add_option("--driver-cores", str(driver_cores))
    if executor_cores:
        spark_submit_cmd.add_option("--executor-cores", str(executor_cores))

    spark_submit_cmd.add_argument(
        os.path.expandvars(app) + " " + " ".join(["'" + str(app_arg) + "'" for app_arg in (app_args or [])]))

    with open("spark-submit.txt", mode="w", encoding="UTF-8") as stream:
        stream.write(spark_submit_cmd.to_str())

    return spark_submit_cmd


def load_application(application_file_path):
    """
        Read and parse the application from file
    """
    with open(application_file_path, encoding="UTF-8") as f:
        application = yaml.load(f)
    return application


def upload_log(blob_client, application):
    """
        upload output.log to storage account
    """
    log_file = os.path.join(os.environ["AZ_BATCH_TASK_WORKING_DIR"], os.environ["SPARK_SUBMIT_LOGS_FILE"])
    upload_file_to_container(
        container_name=os.environ["STORAGE_LOGS_CONTAINER"],
        application_name=application["name"],
        file_path=log_file,
        blob_client=blob_client,
        use_full_path=False,
    )


def receive_submit_request(application_file_path):
    """
        Handle the request to submit a task
    """
    blob_client = config.blob_client
    application = load_application(application_file_path)

    cmd = __app_submit_cmd(
        name=application["name"],
        app=application["application"],
        app_args=application["application_args"],
        main_class=application["main_class"],
        jars=application["jars"],
        py_files=application["py_files"],
        files=application["files"],
        driver_java_options=application["driver_java_options"],
        driver_library_path=application["driver_library_path"],
        driver_class_path=application["driver_class_path"],
        driver_memory=application["driver_memory"],
        executor_memory=application["executor_memory"],
        driver_cores=application["driver_cores"],
        executor_cores=application["executor_cores"],
    )

    return_code = subprocess.call(cmd.to_str(), shell=True)
    upload_log(blob_client, application)
    return return_code


def upload_error_log(error, application_file_path):
    application = load_application(application_file_path)
    blob_client = config.blob_client

    error_log_path = os.path.join(os.environ["AZ_BATCH_TASK_WORKING_DIR"], "error.log")
    with open(error_log_path, "w", encoding="UTF-8") as error_log:
        error_log.write(error)

    upload_file_to_container(
        container_name=os.environ["STORAGE_LOGS_CONTAINER"],
        application_name=application["name"],
        file_path=os.path.realpath(error_log.name),
        blob_client=blob_client,
        use_full_path=False,
    )
    upload_log(blob_client, application)


if __name__ == "__main__":
    return_code = 1
    try:
        return_code = receive_submit_request(os.path.join(os.environ["AZ_BATCH_TASK_WORKING_DIR"], "application.yaml"))
    except Exception as e:
        upload_error_log(str(e), os.path.join(os.environ["AZ_BATCH_TASK_WORKING_DIR"], "application.yaml"))

    # force batch task exit code to match spark exit code
    sys.exit(return_code)
