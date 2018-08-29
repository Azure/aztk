import os

import wait_until_master_selected
from aztk.internal import cluster_data
from aztk.models.plugins import PluginTarget
from core import config
from install import create_user, pick_master, plugins, spark, spark_container

# from .node_scheduling import setup_node_scheduling


def read_cluster_config():
    data = cluster_data.ClusterData(config.blob_client, config.cluster_id)
    cluster_config = data.read_cluster_config()
    print("Got cluster config", cluster_config)
    return cluster_config


def setup_host(docker_repo: str, docker_run_options: str):
    """
    Code to be run on the node (NOT in a container)
    :param docker_repo: location of the Docker image to use
    :param docker_run_options: additional command-line options to pass to docker run
    """
    client = config.batch_client

    create_user.create_user(batch_client=client)
    if os.environ["AZ_BATCH_NODE_IS_DEDICATED"] == "true" or os.environ["AZTK_MIXED_MODE"] == "false":
        is_master = pick_master.find_master(client)
    else:
        is_master = False
        wait_until_master_selected.main()

    is_worker = not is_master or os.environ.get("AZTK_WORKER_ON_MASTER") == "true"
    master_node_id = pick_master.get_master_node_id(config.batch_client.pool.get(config.pool_id))
    master_node = config.batch_client.compute_node.get(config.pool_id, master_node_id)

    if is_master:
        os.environ["AZTK_IS_MASTER"] = "true"
    else:
        os.environ["AZTK_IS_MASTER"] = "false"
    if is_worker:
        os.environ["AZTK_IS_WORKER"] = "true"
    else:
        os.environ["AZTK_IS_WORKER"] = "false"

    os.environ["AZTK_MASTER_IP"] = master_node.ip_address

    cluster_conf = read_cluster_config()

    # setup_node_scheduling(client, cluster_conf, is_master)

    # TODO pass azure file shares
    spark_container.start_spark_container(
        docker_repo=docker_repo,
        docker_run_options=docker_run_options,
        gpu_enabled=os.environ.get("AZTK_GPU_ENABLED") == "true",
        plugins=cluster_conf.plugins,
    )
    plugins.setup_plugins(target=PluginTarget.Host, is_master=is_master, is_worker=is_worker)


def setup_spark_container():
    """
    Code run in the main spark container
    """
    is_master = os.environ.get("AZTK_IS_MASTER") == "true"
    is_worker = os.environ.get("AZTK_IS_WORKER") == "true"
    print("Setting spark container. Master: ", is_master, ", Worker: ", is_worker)

    print("Copying spark setup config")
    spark.setup_conf()
    print("Done copying spark setup config")

    spark.setup_connection()

    if is_master:
        spark.start_spark_master()

    if is_worker:
        spark.start_spark_worker()

    plugins.setup_plugins(target=PluginTarget.SparkContainer, is_master=is_master, is_worker=is_worker)

    open("/tmp/setup_complete", "a").close()
