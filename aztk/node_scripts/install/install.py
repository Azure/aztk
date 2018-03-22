import os
from core import config
from install import pick_master, spark, scripts, create_user, plugins
import wait_until_master_selected


def setup_node():
    client = config.batch_client

    create_user.create_user(batch_client=client)

    spark.setup_conf()

    if os.environ['AZ_BATCH_NODE_IS_DEDICATED'] == "true" or os.environ['MIXED_MODE'] == "False":
        is_master = pick_master.find_master(client)
    else:
        is_master = False
        wait_until_master_selected.main()

    master_node_id = pick_master.get_master_node_id(config.batch_client.pool.get(config.pool_id))
    master_node = config.batch_client.compute_node.get(config.pool_id, master_node_id)

    os.environ["MASTER_IP"] = master_node.ip_address

    if is_master:
        setup_as_master()
        plugins.setup_plugins(is_master=True, is_worker=True)
        scripts.run_custom_scripts(is_master=True, is_worker=True)

    else:
        setup_as_worker()
        plugins.setup_plugins(is_master=False, is_worker=True)
        scripts.run_custom_scripts(is_master=False, is_worker=True)

    open("/tmp/setup_complete", 'a').close()


def setup_as_master():
    print("Setting up as master.")
    spark.setup_connection()
    spark.start_spark_master()
    if os.environ["WORKER_ON_MASTER"] == "True":
        spark.start_spark_worker()


def setup_as_worker():
    print("Setting up as worker.")
    spark.setup_connection()
    spark.start_spark_worker()
