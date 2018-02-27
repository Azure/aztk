import subprocess
import time
from datetime import datetime

import azure.batch.models as batch_models
from azure.batch.models import BatchErrorException

import aztk.spark
import pytest
from aztk.utils import constants
from aztk.error import AztkError
from cli import config


# base cluster name
dt = datetime.now()
current_time = dt.microsecond
base_cluster_id = "cluster-{}".format(current_time)

# load secrets
# note: this assumes secrets are set up in .aztk/secrets
spark_client = aztk.spark.Client(config.load_aztk_secrets())


# helper method
def wait_until_cluster_deleted(cluster_id: str):
    while True:
        try:
            spark_client.get_cluster(cluster_id)
            time.sleep(1)
        except AztkError:
            # break when the cluster is not found
            break


def test_create_cluster():
    test_id = "test-create-"
    try:
        # TODO: make Cluster Configuration more robust, test each value
        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )

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
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)


def test_get_cluster():
    test_id = "test-get-"

    try:
        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )

        spark_client.create_cluster(cluster_configuration, wait=True)
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
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)



def test_list_clusters():
    test_id = "test-list-"
    try:

        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )

        spark_client.create_cluster(cluster_configuration, wait=True)
        clusters = spark_client.list_clusters()

        assert cluster_configuration.cluster_id in [cluster.id for cluster in clusters]

    except (AztkError, BatchErrorException):
        assert False

    finally:
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)



def test_get_remote_login_settings():
    test_id = "test-get-remote-login-"
    try:

        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )


        spark_client.create_cluster(cluster_configuration, wait=True)
        cluster = spark_client.get_cluster(cluster_id=cluster_configuration.cluster_id)
        rls = spark_client.get_remote_login_settings(cluster_id=cluster.id, node_id=cluster.master_node_id)

        assert rls.ip_address is not None
        assert rls.port is not None

    except (AztkError, BatchErrorException):
        assert False

    finally:
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)



def test_submit():
    test_id = "test-submit-"
    try:
        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )

        spark_client.create_cluster(cluster_configuration, wait=True)
        application_configuration = aztk.spark.models.ApplicationConfiguration(
            name="pipy100",
            application="examples/src/main/python/pi.py",
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
            max_retry_count=None
        )
        spark_client.submit(cluster_id=cluster_configuration.cluster_id, application=application_configuration, wait=True)
        assert True

    except (AztkError, BatchErrorException):
        assert False

    finally:
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)



def test_get_application_log():
    test_id = "test-get-app-log-"
    try:
        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )

        spark_client.create_cluster(cluster_configuration, wait=True)
        application_configuration = aztk.spark.models.ApplicationConfiguration(
            name="pipy100",
            application="examples/src/main/python/pi.py",
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
            max_retry_count=None
        )
        spark_client.submit(cluster_id=cluster_configuration.cluster_id, application=application_configuration, wait=True)
        application_log = spark_client.get_application_log(cluster_id=cluster_configuration.cluster_id,
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
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)



def test_create_user_password():
    #TODO: test with paramiko
    pass


def test_create_user_ssh_key():
    #TODO: test with paramiko
    pass


def test_get_application_status_complete():
    test_id = "test-app-status-complete-"

    try:
        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )

        spark_client.create_cluster(cluster_configuration, wait=True)
        application_configuration = aztk.spark.models.ApplicationConfiguration(
            name="pipy100",
            application="examples/src/main/python/pi.py",
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
            max_retry_count=None
        )
        spark_client.submit(cluster_id=cluster_configuration.cluster_id, application=application_configuration, wait=True)
        spark_client.submit(cluster_configuration.cluster_id, application_configuration)
        spark_client.wait_until_application_done(cluster_id=cluster_configuration.cluster_id, task_id=application_configuration.name)
        status = spark_client.get_application_status(cluster_id=cluster_configuration.cluster_id, app_name=application_configuration.name)

        assert status == "completed"

    except (AztkError, BatchErrorException):
        assert False

    finally:
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)



def test_delete_cluster():
    test_id = "test-delete-"
    try:
        cluster_configuration = aztk.spark.models.ClusterConfiguration(
            cluster_id=test_id+base_cluster_id,
            vm_count=2,
            vm_low_pri_count=0,
            vm_size="standard_f2",
            subnet_id=None,
            custom_scripts=None,
            file_shares=None,
            docker_repo=None,
            spark_configuration=None
        )

        spark_client.create_cluster(cluster_configuration, wait=True)
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)

        assert success is True

    except (AztkError, BatchErrorException):
        assert False

    finally:
        success = spark_client.delete_cluster(cluster_id=cluster_configuration.cluster_id)
        wait_until_cluster_deleted(cluster_id=cluster_configuration.cluster_id)
