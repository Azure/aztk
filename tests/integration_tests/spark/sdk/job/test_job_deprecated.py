import os
import subprocess
from datetime import datetime

import pytest
from azure.batch.models import BatchErrorException
from tests.integration_tests.spark.sdk.get_client import (get_spark_client, get_test_suffix)

import aztk.spark
from aztk.error import AztkError
from aztk_cli import config

base_job_id = get_test_suffix("job")
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
        with pytest.warns(DeprecationWarning):
            job = spark_client.submit_job(job_configuration=job_configuration)
        with pytest.warns(DeprecationWarning):
            spark_client.wait_until_job_finished(job_id=job_configuration.id)

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
        with pytest.warns(DeprecationWarning):
            spark_client.submit_job(job_configuration=job_configuration)
        with pytest.warns(DeprecationWarning):
            spark_client.wait_until_job_finished(job_configuration.id)

        jobs = spark_client.list_jobs()

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
        with pytest.warns(DeprecationWarning):
            spark_client.submit_job(job_configuration=job_configuration)
        with pytest.warns(DeprecationWarning):
            spark_client.wait_until_job_finished(job_configuration.id)

        applications = spark_client.list_applications(job_id=job_configuration.id)

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
        with pytest.warns(DeprecationWarning):
            spark_client.submit_job(job_configuration=job_configuration)
        with pytest.warns(DeprecationWarning):
            spark_client.wait_until_job_finished(job_configuration.id)
        with pytest.warns(DeprecationWarning):
            job = spark_client.get_job(job_id=job_configuration.id)

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
        with pytest.warns(DeprecationWarning):
            spark_client.submit_job(job_configuration=job_configuration)
        with pytest.warns(DeprecationWarning):
            spark_client.wait_until_job_finished(job_configuration.id)
        with pytest.warns(DeprecationWarning):
            application = spark_client.get_application(job_id=job_configuration.id, application_name=app1.name)

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
        with pytest.warns(DeprecationWarning):
            spark_client.submit_job(job_configuration=job_configuration)
        with pytest.warns(DeprecationWarning):
            spark_client.wait_until_job_finished(job_configuration.id)

        with pytest.warns(DeprecationWarning):
            application_log = spark_client.get_job_application_log(
                job_id=job_configuration.id, application_name=app1.name)

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

        with pytest.warns(DeprecationWarning):
            spark_client.submit_job(job_configuration=job_configuration)
        with pytest.warns(DeprecationWarning):
            spark_client.wait_until_job_finished(job_configuration.id)
        with pytest.warns(DeprecationWarning):
            spark_client.delete_job(job_configuration.id)

        with pytest.warns(DeprecationWarning):
            assert job_configuration.id not in spark_client.list_jobs()
        try:
            with pytest.warns(DeprecationWarning):
                spark_client.get_job(job_configuration.id)
        except AztkError:
            # this should fail
            assert True
    except (AztkError, BatchErrorException) as e:
        raise e
    finally:
        clean_up_job(job_configuration.id)


def clean_up_job(job_id):
    try:
        with pytest.warns(DeprecationWarning):
            spark_client.delete_job(job_id)
    except Exception:
        pass
