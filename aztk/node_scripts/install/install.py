import os
import subprocess
from core import config
from install import pick_master, spark, scripts, create_user, plugins, spark_container
import wait_until_master_selected
from aztk.models.plugins import PluginTarget

def setup_node(docker_repo: str):
    """
    Code to be run on the node(NOT in a container)
    """
    client = config.batch_client

    create_user.create_user(batch_client=client)
    if os.environ['AZ_BATCH_NODE_IS_DEDICATED'] == "true" or os.environ['AZTK_MIXED_MODE'] == "False":
        is_master = pick_master.find_master(client)
    else:
        is_master = False
        wait_until_master_selected.main()

    is_worker = not is_master or os.environ["AZTK_WORKER_ON_MASTER"]
    master_node_id = pick_master.get_master_node_id(config.batch_client.pool.get(config.pool_id))
    master_node = config.batch_client.compute_node.get(config.pool_id, master_node_id)

    env = os.environ.copy()
    if is_master:
        env["AZTK_IS_MASTER"] = "1"
    if is_worker:
        env["AZTK_IS_WORKER"] = "1"

    env["AZTK_MASTER_IP"] = master_node.ip_address


    spark_container.start_spark_container(
        docker_repo=docker_repo,
        gpu_enabled=os.environ.get("AZTK_GPU_ENABLED") == "true",
    )
    plugins.setup_plugins(target=PluginTarget.Node, is_master=is_master, is_worker=is_worker)


def setup_spark_container():
    """
    Code run in the main spark container
    """

    is_master = os.environ["AZTK_IS_MASTER"]
    is_worker = os.environ["AZTK_IS_WORKER"]

    spark.setup_conf()
    master_node_id = pick_master.get_master_node_id(config.batch_client.pool.get(config.pool_id))
    master_node = config.batch_client.compute_node.get(config.pool_id, master_node_id)


    if is_master:
        spark.setup_as_master()
    else:
        spark.setup_as_worker()

    plugins.setup_plugins(target=PluginTarget.SparkContainer, is_master=is_master, is_worker=is_worker)
    scripts.run_custom_scripts(is_master=is_master, is_worker=is_worker)

    open("/tmp/setup_complete", 'a').close()
