import os
import subprocess
import time
from datetime import datetime
from zipfile import ZipFile

import azure.batch.models as batch_models
import pytest
from azure.batch.models import BatchErrorException

import aztk.spark
from aztk.error import AztkError
from aztk.utils import constants
from aztk_cli import config
from tests.integration_tests.spark.sdk.get_client import get_spark_client, get_test_suffix


base_cluster_id = get_test_suffix("cluster")
spark_client = get_spark_client()


def clean_up_cluster(cluster_id):
    try:
        spark_client.delete_cluster(cluster_id=cluster_id)
    except (BatchErrorException, AztkError):
        # pass in the event that the cluster does not exist
        pass


def ensure_spark_master(cluster_id):
    results = spark_client.cluster_run(cluster_id,
                "if $AZTK_IS_MASTER ; then $SPARK_HOME/sbin/spark-daemon.sh status org.apache.spark.deploy.master.Master 1 ;" \
                " else echo AZTK_IS_MASTER is false ; fi")
    for _, result in results:
        if isinstance(result, Exception):
            raise result
        print(result[0])
        assert result[0] in ["org.apache.spark.deploy.master.Master is running.", "AZTK_IS_MASTER is false"]


def ensure_spark_worker(cluster_id):
    results = spark_client.cluster_run(cluster_id,
                "if $AZTK_IS_WORKER ; then $SPARK_HOME/sbin/spark-daemon.sh status org.apache.spark.deploy.worker.Worker 1 ;" \
                " else echo AZTK_IS_WORKER is false ; fi")
    for _, result in results:
        if isinstance(result, Exception):
            raise result
        assert result[0] in ["org.apache.spark.deploy.worker.Worker is running.", "AZTK_IS_WORKER is false"]


def ensure_spark_processes(cluster_id):
    ensure_spark_master(cluster_id)
    ensure_spark_worker(cluster_id)


def wait_for_all_nodes(cluster_id, nodes):
    while True:
        for node in nodes:
            if node.state in [batch_models.ComputeNodeState.unusable, batch_models.ComputeNodeState.start_task_failed]:
                raise AztkError("Node {} in failed state.".format(node.id))
            if node.state not in [batch_models.ComputeNodeState.idle, batch_models.ComputeNodeState.running]:
                break
        else:
            nodes = spark_client.cluster.get(cluster_id).nodes
            continue
        break


def test_create_cluster():
    test_id = "test-create-"
    # TODO: make Cluster Configuration more robust, test each value
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    try:
        with pytest.warns(DeprecationWarning):
            cluster = spark_client.create_cluster(cluster_configuration, wait=True)

        assert cluster.pool is not None
        assert cluster.nodes is not None
        assert cluster.id == cluster_configuration.cluster_id
        assert cluster.vm_size == "standard_f2"
        assert cluster.current_dedicated_nodes == 2
        assert cluster.gpu_enabled is False
        assert cluster.master_node_id is not None
        assert cluster.current_low_pri_nodes == 0

    except (AztkError, BatchErrorException) as e:
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_get_cluster():
    test_id = "test-get-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)
        with pytest.warns(DeprecationWarning):
            cluster = spark_client.get_cluster(cluster_id=cluster_configuration.cluster_id)

        assert cluster.pool is not None
        assert cluster.nodes is not None
        assert cluster.id == cluster_configuration.cluster_id
        assert cluster.vm_size == "standard_f2"
        assert cluster.current_dedicated_nodes == 2
        assert cluster.gpu_enabled is False
        assert cluster.master_node_id is not None
        assert cluster.current_low_pri_nodes == 0

    except (AztkError, BatchErrorException) as e:
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_list_clusters():
    test_id = "test-list-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)
        with pytest.warns(DeprecationWarning):
            clusters = spark_client.list_clusters()

        assert cluster_configuration.cluster_id in [cluster.id for cluster in clusters]

    except (AztkError, BatchErrorException):
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_get_remote_login_settings():
    test_id = "test-get-remote-login-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)
        with pytest.warns(DeprecationWarning):
            cluster = spark_client.get_cluster(cluster_id=cluster_configuration.cluster_id)
        with pytest.warns(DeprecationWarning):
            rls = spark_client.get_remote_login_settings(cluster_id=cluster.id, node_id=cluster.master_node_id)

        assert rls.ip_address is not None
        assert rls.port is not None

    except (AztkError, BatchErrorException) as e:
        raise e
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_submit():
    test_id = "test-submit-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    application_configuration = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[100],
        main_class=None,
        jars=[],
        py_files=[],
        files=[],
        driver_java_options=None,
        driver_class_path=None,
        driver_memory=None,
        driver_cores=None,
        executor_memory=None,
        executor_cores=None,
        max_retry_count=None)
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)

        with pytest.warns(DeprecationWarning):
            spark_client.submit(
                cluster_id=cluster_configuration.cluster_id, application=application_configuration, wait=True)
        
        assert True

    except (AztkError, BatchErrorException):
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_get_application_log():
    test_id = "test-get-app-log-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    application_configuration = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[100],
        main_class=None,
        jars=[],
        py_files=[],
        files=[],
        driver_java_options=None,
        driver_class_path=None,
        driver_memory=None,
        driver_cores=None,
        executor_memory=None,
        executor_cores=None,
        max_retry_count=None)
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)

        with pytest.warns(DeprecationWarning):
            spark_client.submit(
                cluster_id=cluster_configuration.cluster_id, application=application_configuration, wait=True)
        with pytest.warns(DeprecationWarning):
            application_log = spark_client.get_application_log(
                cluster_id=cluster_configuration.cluster_id,
                application_name=application_configuration.name,
                tail=False,
                current_bytes=0)

        assert application_log.exit_code == 0
        assert application_log.name == application_configuration.name == "pipy100"
        assert application_log.application_state == "completed"
        assert application_log.log is not None
        assert application_log.total_bytes is not None

    except (AztkError, BatchErrorException):
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_create_user_password():
    #TODO: test with paramiko
    pass


def test_create_user_ssh_key():
    #TODO: test with paramiko
    pass


def test_get_application_status_complete():
    test_id = "test-app-status-complete-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    application_configuration = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[100],
        main_class=None,
        jars=[],
        py_files=[],
        files=[],
        driver_java_options=None,
        driver_class_path=None,
        driver_memory=None,
        driver_cores=None,
        executor_memory=None,
        executor_cores=None,
        max_retry_count=None)
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)
        with pytest.warns(DeprecationWarning):
            spark_client.submit(
                cluster_id=cluster_configuration.cluster_id, application=application_configuration, wait=True)
        with pytest.warns(DeprecationWarning):
            status = spark_client.get_application_status(
                cluster_id=cluster_configuration.cluster_id, app_name=application_configuration.name)

        assert status == "completed"

    except (AztkError, BatchErrorException):
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_delete_cluster():
    test_id = "test-delete-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)

    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)
            success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)

        assert success is True

    except (AztkError, BatchErrorException):
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_spark_processes_up():
    test_id = "test-spark-processes-up-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        vm_count=2,
        vm_low_pri_count=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)

    try:
        with pytest.warns(DeprecationWarning):
            cluster = spark_client.create_cluster(cluster_configuration, wait=True)
            wait_for_all_nodes(cluster.id, cluster.nodes)

        with pytest.warns(DeprecationWarning):
            success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)

        assert success is True

    except (AztkError, BatchErrorException):
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)


def test_debug_tool():
    test_id = "debug-tool-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
        custom_scripts=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    expected_members = [
        "df.txt", "hostname.txt", "docker-images.txt", "docker-containers.txt", "spark/docker.log", "spark/ps_aux.txt",
        "spark/logs", "spark/wd"
    ]
    try:
        with pytest.warns(DeprecationWarning):
            cluster = spark_client.create_cluster(cluster_configuration, wait=True)

        nodes = [node for node in cluster.nodes]
        wait_for_all_nodes(cluster.id, nodes)

        with pytest.warns(DeprecationWarning):
            cluster_output = spark_client.run_cluster_diagnostics(cluster_id=cluster.id)

        for node_output in cluster_output:
            node_output.output.seek(0)    # tempfile requires seek 0 before reading
            debug_zip = ZipFile(node_output.output)
            assert node_output.id in [node.id for node in nodes]
            assert node_output.error is None
            assert any(member in name for name in debug_zip.namelist() for member in expected_members)
    except (AztkError, BatchErrorException):
        assert False

    finally:
        clean_up_cluster(cluster_configuration.cluster_id)
