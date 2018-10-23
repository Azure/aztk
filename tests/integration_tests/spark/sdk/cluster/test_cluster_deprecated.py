import os
import subprocess
import time
from datetime import datetime
from zipfile import ZipFile

import azure.batch.models as batch_models
import pytest
from azure.batch.models import BatchErrorException
from tests.integration_tests.spark.sdk.clean_up_cluster import clean_up_cluster
from tests.integration_tests.spark.sdk.ensure_spark_processes import \
    ensure_spark_processes
from tests.integration_tests.spark.sdk.get_client import (get_spark_client,
                                                          get_test_suffix)
from tests.integration_tests.spark.sdk.wait_for_all_nodes import \
    wait_for_all_nodes

import aztk.spark
from aztk.error import AztkError
from aztk.utils import constants
from aztk_cli import config

base_cluster_id = get_test_suffix("cluster")
spark_client = get_spark_client()


def test_create_cluster():
    test_id = "test-create-deprecated-"
    # TODO: make Cluster Configuration more robust, test each value
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
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

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_get_cluster():
    test_id = "test-get-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
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

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_list_clusters():
    test_id = "test-list-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)
        with pytest.warns(DeprecationWarning):
            clusters = spark_client.list_clusters()

        assert cluster_configuration.cluster_id in [cluster.id for cluster in clusters]

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_get_remote_login_settings():
    test_id = "test-get-remote-login-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
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

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_submit():
    test_id = "test-submit-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
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

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_get_application_log():
    test_id = "test-get-app-log-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
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
        assert application_log.application_state == aztk.spark.models.ApplicationState.Completed
        assert application_log.log is not None
        assert application_log.total_bytes is not None

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_create_user_password():
    #TODO: test with paramiko
    pass


def test_create_user_ssh_key():
    #TODO: test with paramiko
    pass


def test_get_application_state_complete():
    test_id = "test-app-status-complete-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
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

        assert status == aztk.spark.models.ApplicationState.Completed

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_delete_cluster():
    test_id = "test-delete-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)

    try:
        with pytest.warns(DeprecationWarning):
            spark_client.create_cluster(cluster_configuration, wait=True)
            success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)

        assert success is True

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_spark_processes_up():
    test_id = "test-spark-processes-up-deprecated-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
        file_shares=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        spark_configuration=None)

    try:
        with pytest.warns(DeprecationWarning):
            cluster = spark_client.create_cluster(cluster_configuration, wait=True)
            wait_for_all_nodes(spark_client, cluster.id, cluster.nodes)

        ensure_spark_processes(spark_client=spark_client, id=cluster_configuration.cluster_id)

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)


def test_debug_tool():
    test_id = "test-debug-tool-"
    cluster_configuration = aztk.spark.models.ClusterConfiguration(
        cluster_id=test_id + base_cluster_id,
        size=2,
        size_low_priority=0,
        vm_size="standard_f2",
        subnet_id=None,
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
        wait_for_all_nodes(spark_client, cluster.id, nodes)

        with pytest.warns(DeprecationWarning):
            cluster_output = spark_client.run_cluster_diagnostics(cluster_id=cluster.id)

        for node_output in cluster_output:
            node_output.output.seek(0)    # tempfile requires seek 0 before reading
            debug_zip = ZipFile(node_output.output)
            assert node_output.id in [node.id for node in nodes]
            assert node_output.error is None
            assert any(member in name for name in debug_zip.namelist() for member in expected_members)

    finally:
        clean_up_cluster(spark_client, cluster_configuration.cluster_id)
