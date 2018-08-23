import azure.batch.models as batch_models

from aztk.error import AztkError


def ensure_spark_master(spark_client, id):
    results = spark_client.cluster.run(
        id,
        "if $AZTK_IS_MASTER ; then $SPARK_HOME/sbin/spark-daemon.sh status org.apache.spark.deploy.master.Master 1 ;"
        " else echo AZTK_IS_MASTER is false ; fi")
    for result in results:
        if result.error:
            raise result.error
        assert result.output.rstrip() in [
            "org.apache.spark.deploy.master.Master is running.", "AZTK_IS_MASTER is false"
        ]


def ensure_spark_worker(spark_client, id):
    results = spark_client.cluster.run(
        id,
        "if $AZTK_IS_WORKER ; then $SPARK_HOME/sbin/spark-daemon.sh status org.apache.spark.deploy.worker.Worker 1 ;"
        " else echo AZTK_IS_WORKER is false ; fi")
    for result in results:
        if result.error:
            raise result
        assert result.output.rstrip() in [
            "org.apache.spark.deploy.worker.Worker is running.", "AZTK_IS_WORKER is false"
        ]


def ensure_spark_processes(spark_client, id):
    ensure_spark_master(spark_client, id)
    ensure_spark_worker(spark_client, id)
