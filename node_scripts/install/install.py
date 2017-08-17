from core import config
from install import pick_master, spark

def setup_node():
    client = config.batch_client

    is_master = pick_master.find_master(client)

    if is_master:
        setup_as_master()
    else:
        setup_as_worker()


def setup_as_master():
    print("Setting up as master.")
    spark.setup_connection()
    spark.start_spark_master()
    spark.start_spark_worker()


def setup_as_worker():
    print("Setting up as worker.")
    spark.setup_connection()
    spark.start_spark_worker()
