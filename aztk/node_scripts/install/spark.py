"""
    Code that handle spark configuration
"""
import datetime
import os
import shutil
import time
from subprocess import call
from typing import List

import azure.batch.models as batchmodels

from core import config
from install import pick_master

batch_client = config.batch_client

spark_home = "/home/spark-current"
spark_conf_folder = os.path.join(spark_home, "conf")


def setup_as_master():
    print("Setting up as master.")
    setup_connection()
    start_spark_master()


def setup_as_worker():
    print("Setting up as worker.")
    setup_connection()
    start_spark_worker()


def get_pool() -> batchmodels.CloudPool:
    return batch_client.pool.get(config.pool_id)


def get_node(node_id: str) -> batchmodels.ComputeNode:
    return batch_client.compute_node.get(config.pool_id, node_id)


def list_nodes() -> List[batchmodels.ComputeNode]:
    """
        List all the nodes in the pool.
    """
    # TODO use continuation token & verify against current/target dedicated of
    # pool
    return batch_client.compute_node.list(config.pool_id)


def setup_connection():
    """
        This setup spark config with which nodes are slaves and which are master
    """
    master_node_id = pick_master.get_master_node_id(batch_client.pool.get(config.pool_id))
    master_node = get_node(master_node_id)

    master_config_file = os.path.join(spark_conf_folder, "master")
    master_file = open(master_config_file, "w", encoding="UTF-8")

    print("Adding master node ip {0} to config file '{1}'".format(master_node.ip_address, master_config_file))
    master_file.write("{0}\n".format(master_node.ip_address))

    master_file.close()


def wait_for_master():
    print("Waiting for master to be ready.")
    master_node_id = pick_master.get_master_node_id(batch_client.pool.get(config.pool_id))

    if master_node_id == config.node_id:
        return

    while True:
        master_node = get_node(master_node_id)

        if master_node.state in [batchmodels.ComputeNodeState.idle, batchmodels.ComputeNodeState.running]:
            break
        else:
            print("{0} Still waiting on master", datetime.datetime.now())
            time.sleep(10)


def start_spark_master():
    master_ip = get_node(config.node_id).ip_address
    exe = os.path.join(spark_home, "sbin", "start-master.sh")
    cmd = [exe, "-h", master_ip, "--webui-port", str(config.spark_web_ui_port)]
    print("Starting master with '{0}'".format(" ".join(cmd)))
    call(cmd)
    try:
        start_history_server()
    except Exception as e:
        print("Failed to start history server with the following exception:")
        print(e)


def start_spark_worker():
    wait_for_master()
    exe = os.path.join(spark_home, "sbin", "start-slave.sh")
    master_node_id = pick_master.get_master_node_id(batch_client.pool.get(config.pool_id))
    master_node = get_node(master_node_id)

    cmd = [exe, "spark://{0}:7077".format(master_node.ip_address), "--webui-port", str(config.spark_worker_ui_port)]
    print("Connecting to master with '{0}'".format(" ".join(cmd)))
    call(cmd)


def copyfile(src, dest):
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(src, dest)
        file_stat = os.stat(dest)
        os.chmod(dest, file_stat.st_mode | 0o777)
    except Exception as e:
        print("Failed to copy", src)
        print(e)


def setup_conf():
    """
        Copy spark conf files to spark_home if they were uploaded
    """
    copy_spark_env()
    copy_core_site()
    copy_spark_defaults()
    copy_jars()
    setup_ssh_keys()


def setup_ssh_keys():
    pub_key_path_src = os.path.join(os.environ["AZTK_WORKING_DIR"], "id_rsa.pub")
    priv_key_path_src = os.path.join(os.environ["AZTK_WORKING_DIR"], "id_rsa")
    ssh_key_dest = "/root/.ssh"

    if not os.path.exists(ssh_key_dest):
        os.mkdir(ssh_key_dest)

    copyfile(pub_key_path_src, os.path.join(ssh_key_dest, os.path.basename(pub_key_path_src)))
    copyfile(priv_key_path_src, os.path.join(ssh_key_dest, os.path.basename(priv_key_path_src)))


def copy_spark_env():
    spark_env_path_src = os.path.join(os.environ["AZTK_WORKING_DIR"], "conf/spark-env.sh")
    spark_env_path_dest = os.path.join(spark_home, "conf/spark-env.sh")
    copyfile(spark_env_path_src, spark_env_path_dest)


def copy_spark_defaults():
    spark_default_path_src = os.path.join(os.environ["AZTK_WORKING_DIR"], "conf/spark-defaults.conf")
    spark_default_path_dest = os.path.join(spark_home, "conf/spark-defaults.conf")
    copyfile(spark_default_path_src, spark_default_path_dest)


def copy_core_site():
    spark_core_site_src = os.path.join(os.environ["AZTK_WORKING_DIR"], "conf/core-site.xml")
    spark_core_site_dest = os.path.join(spark_home, "conf/core-site.xml")
    copyfile(spark_core_site_src, spark_core_site_dest)


def copy_jars():
    # Copy jars to $SPARK_HOME/jars
    spark_default_path_src = os.path.join(os.environ["AZTK_WORKING_DIR"], "jars")
    spark_default_path_dest = os.path.join(spark_home, "jars")

    try:
        jar_files = os.listdir(spark_default_path_src)
        for jar in jar_files:
            src = os.path.join(spark_default_path_src, jar)
            dest = os.path.join(spark_default_path_dest, jar)
            print("copy {} to {}".format(src, dest))
            copyfile(src, dest)
    except Exception as e:
        print("Failed to copy jar files with error:")
        print(e)


def parse_configuration_file(path_to_file: str):
    try:
        file = open(path_to_file, "r", encoding="UTF-8")
        properties = {}
        for line in file:
            if not line.startswith("#") and len(line) > 1:
                split = line.split()
                properties[split[0]] = split[1]
        return properties
    except Exception as e:
        print("Failed to parse configuration file:", path_to_file, "with error:")
        print(e)


def start_history_server():
    # configure the history server
    spark_event_log_enabled_key = "spark.eventLog.enabled"
    spark_event_log_directory_key = "spark.eventLog.dir"
    spark_history_fs_log_directory = "spark.history.fs.logDirectory"
    path_to_spark_defaults_conf = os.path.join(spark_home, "conf/spark-defaults.conf")
    properties = parse_configuration_file(path_to_spark_defaults_conf)
    required_keys = [spark_event_log_enabled_key, spark_event_log_directory_key, spark_history_fs_log_directory]

    # only enable the history server if it was enabled in the configuration file
    if properties:
        if all(key in properties for key in required_keys):
            configure_history_server_log_path(properties[spark_history_fs_log_directory])
            exe = os.path.join(spark_home, "sbin", "start-history-server.sh")
            print("Starting history server")
            call([exe])


def configure_history_server_log_path(path_to_log_file):
    # Check if the file path starts with a local file extension
    # If so, create the path on disk otherwise ignore
    print("Configuring spark history server log directory {}.".format(path_to_log_file))
    if path_to_log_file.startswith("file:/"):
        # create the local path on disk
        directory = path_to_log_file.replace("file:", "")
        if os.path.exists(directory):
            print("Skipping. Directory {} already exists.".format(directory))
        else:
            print("Create directory {}.".format(directory))
            os.makedirs(directory)

            # Make sure the directory can be accessed by all users
            os.chmod(directory, mode=0o777)
    else:
        print("Skipping. The eventLog directory is not local.")
