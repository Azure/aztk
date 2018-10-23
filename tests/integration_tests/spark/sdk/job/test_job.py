import os
import subprocess
from datetime import datetime

from azure.batch.models import BatchErrorException
from tests.integration_tests.spark.sdk.get_client import (get_spark_client, get_test_suffix)

import aztk.spark
from aztk.error import AztkError
from aztk_cli import config

base_job_id = get_test_suffix("j")
spark_client = get_spark_client()


def test_submit_job():
    test_id = "submit-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0)
    try:
        job = spark_client.job.submit(job_configuration=job_configuration, wait=True)

        assert job.id == job_configuration.id
        assert job.state is not None

    except (AztkError, BatchErrorException) as e:
        raise e

    finally:
        clean_up_job(job_configuration.id)


def test_list_jobs():
    test_id = "list-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=1,
        max_low_pri_nodes=0,
        worker_on_master=True)
    try:
        spark_client.job.submit(job_configuration=job_configuration, wait=True)

        jobs = spark_client.job.list()

        assert jobs is not None
        assert job_configuration.id in [job.id for job in jobs]

    except (AztkError, BatchErrorException) as e:
        raise e

    finally:
        clean_up_job(job_configuration.id)


def test_list_applications():
    test_id = "list-apps-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0)
    try:
        spark_client.job.submit(job_configuration=job_configuration, wait=True)

        applications = spark_client.job.list_applications(id=job_configuration.id)

        assert applications not in (None, [])
        assert len(applications) == 2
        for application in applications:
            assert isinstance(application, (aztk.spark.models.Application, str))

    except (AztkError, BatchErrorException) as e:
        raise e

    finally:
        clean_up_job(job_configuration.id)


def test_get_job():
    test_id = "get-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=1,
        max_low_pri_nodes=0,
        worker_on_master=True)
    try:
        spark_client.job.submit(job_configuration=job_configuration, wait=True)

        job = spark_client.job.get(id=job_configuration.id)
        assert job.id == job_configuration.id
        assert app1.name in [app.name for app in job.applications]
        assert app2.name in [app.name for app in job.applications]

    except (AztkError, BatchErrorException) as e:
        raise e

    finally:
        clean_up_job(job_configuration.id)


def test_get_application():
    test_id = "get-app-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0)
    try:
        spark_client.job.submit(job_configuration=job_configuration, wait=True)
        application = spark_client.job.get_application(id=job_configuration.id, application_name=app1.name)
        assert isinstance(application, aztk.spark.models.Application)
        assert application.exit_code == 0
        assert application.state == aztk.spark.models.ApplicationState.Completed
        assert application.name == "pipy100"
    except (AztkError, BatchErrorException) as e:
        raise e
    finally:
        clean_up_job(job_configuration.id)


def test_get_application_log():
    test_id = "gal-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0)
    try:
        spark_client.job.submit(job_configuration=job_configuration, wait=True)

        application_log = spark_client.job.get_application_log(id=job_configuration.id, application_name=app1.name)

        assert isinstance(application_log, aztk.spark.models.ApplicationLog)
        assert application_log.log is not None
        assert application_log.exit_code == 0
        assert application_log.name == "pipy100"
        assert application_log.total_bytes != 0

    except (AztkError, BatchErrorException) as e:
        raise e

    finally:
        clean_up_job(job_configuration.id)


def test_delete_job():
    test_id = "delete-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[10],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=1,
        max_low_pri_nodes=0,
        worker_on_master=True)
    try:
        spark_client.job.submit(job_configuration=job_configuration, wait=True)
        spark_client.job.delete(job_configuration.id)
        assert job_configuration.id not in spark_client.job.list()
        try:
            spark_client.job.get(job_configuration.id)
        except AztkError:
            # this should fail
            assert True
    except (AztkError, BatchErrorException) as e:
        raise e
    finally:
        clean_up_job(job_configuration.id)


def test_scheduling_target_submit():
    test_id = "starget-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy001",
        application="./examples/src/main/python/pi.py",
        application_args=[],
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy002",
        application="./examples/src/main/python/pi.py",
        application_args=[],
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id + base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0,
        scheduling_target=aztk.spark.models.SchedulingTarget.Master)
    try:
        job = spark_client.job.submit(job_configuration=job_configuration, wait=True)

        application = spark_client.job.get_application(id=job.id, application_name=app2.name)
        assert application.failure_info is None
        assert application.name == "pipy002"
        assert application.node_id is not None
        assert application.end_time > application.start_time
        assert application.state == aztk.spark.models.ApplicationState.Completed

        application_log = spark_client.job.get_application_log(id=job_configuration.id, application_name=app1.name)
        assert application_log.exit_code == 0
        assert application_log.log is not None
        assert application_log.cluster_id == job_configuration.id

    except (AztkError, BatchErrorException) as e:
        raise e

    finally:
        clean_up_job(job_configuration.id)


def clean_up_job(job_id):
    try:
        spark_client.job.delete(job_id)
    except Exception:
        pass
