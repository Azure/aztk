"""
    Code that handle spark configuration
"""
import datetime
import time
import os
import json
import shutil
from subprocess import call, Popen, check_output
from typing import List
import azure.batch.models as batchmodels
from core import config
from install import pick_master

batch_client = config.batch_client

spark_home = "/home/spark-current"
spark_conf_folder = os.path.join(spark_home, "conf")

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
    master_node_id = pick_master.get_master_node_id(
        batch_client.pool.get(config.pool_id))
    master_node = get_node(master_node_id)

    master_config_file = os.path.join(spark_conf_folder, "master")
    master_file = open(master_config_file, 'w')

    print("Adding master node ip {0} to config file '{1}'".format(
        master_node.ip_address, master_config_file))
    master_file.write("{0}\n".format(master_node.ip_address))

    master_file.close()


def wait_for_master():
    print("Waiting for master to be ready.")
    master_node_id = pick_master.get_master_node_id(
        batch_client.pool.get(config.pool_id))

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
    cmd = [exe, "-h", master_ip, "--webui-port",
           str(config.spark_web_ui_port)]
    print("Starting master with '{0}'".format(" ".join(cmd)))
    call(cmd)


def start_spark_worker():
    wait_for_master()
    exe = os.path.join(spark_home, "sbin", "start-slave.sh")
    master_node_id = pick_master.get_master_node_id(
        batch_client.pool.get(config.pool_id))
    master_node = get_node(master_node_id)

    my_env = os.environ.copy()
    my_env["SPARK_MASTER_IP"] = master_node.ip_address

    cmd = [exe, "spark://{0}:7077".format(master_node.ip_address),
           "--webui-port", str(config.spark_worker_ui_port)]
    print("Connecting to master with '{0}'".format(" ".join(cmd)))
    call(cmd)


def setup_conf():
    """
        Copy spark conf files to spark_home if they were uplaoded
    """
    copy_spark_env()
    copy_core_site()
    copy_jars()


def copy_spark_env():
    spark_env_path_src = os.path.join(os.environ['DOCKER_WORKING_DIR'], 'conf/spark-env.sh')
    spark_env_path_dest = os.path.join(spark_home, 'conf/spark-env.sh')

    try:
        shutil.copyfile(spark_env_path_src, spark_env_path_dest)
        file_stat = os.stat(spark_env_path_dest)
        os.chmod(spark_env_path_dest, file_stat.st_mode | 0o777)
    except Exception as e:
        print("Failed to copy spark-env.sh file")
        print(e)


def copy_core_site():
    spark_default_path_src = os.path.join(os.environ['DOCKER_WORKING_DIR'], 'conf/spark-defaults.conf')
    spark_default_path_dest = os.path.join(spark_home, 'conf/spark-defaults.conf')

    try:
        shutil.copyfile(spark_default_path_src, spark_default_path_dest)
    except Exception as e:
        print("Failed to copy spark-defaults.conf file")
        print(e)


    spark_default_path_src = os.path.join(os.environ['DOCKER_WORKING_DIR'], 'conf/core-site.xml')
    spark_default_path_dest = os.path.join(spark_home, 'conf/core-site.xml')

    try:
        shutil.copyfile(spark_default_path_src, spark_default_path_dest)
    except Exception as e:
        print("Failed to copy spark-defaults.conf file")
        print(e)


def copy_jars():
    # Copy jars to $SPARK_HOME/jars
    spark_default_path_src = os.path.join(os.environ['DOCKER_WORKING_DIR'], 'jars')
    spark_default_path_dest = os.path.join(spark_home, 'jars')

    try:
        jar_files = os.listdir(spark_default_path_src)
        for jar in jar_files:
            src = os.path.join(spark_default_path_src, jar)
            dest = os.path.join(spark_default_path_dest, jar)
            print("copy {} to {}".format(src, dest))
            shutil.copyfile(src, dest)
    except Exception as e:
        print("Failed to copy jar files")
        print(e)
