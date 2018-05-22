import os
import subprocess
from datetime import datetime

from azure.batch.models import BatchErrorException

import aztk.spark
from aztk.error import AztkError
from aztk_cli import config

dt = datetime.now()
time = dt.microsecond
base_job_id = "job-{}".format(time)


# load secrets
# note: this assumes secrets are set up in .aztk/secrets
tenant_id = os.environ.get("TENANT_ID")
client_id = os.environ.get("CLIENT_ID")
credential = os.environ.get("CREDENTIAL")
batch_account_resource_id = os.environ.get("BATCH_ACCOUNT_RESOURCE_ID")
storage_account_resource_id = os.environ.get("STORAGE_ACCOUNT_RESOURCE_ID")
ssh_pub_key = os.environ.get("ID_RSA_PUB")
ssh_priv_key = os.environ.get("ID_RSA")
keys = [tenant_id, client_id, credential, batch_account_resource_id,
        storage_account_resource_id, ssh_priv_key, ssh_pub_key]

if all(keys):
    spark_client = aztk.spark.Client(
        aztk.spark.models.SecretsConfiguration(
            service_principal=aztk.spark.models.ServicePrincipalConfiguration(
                tenant_id=tenant_id,
                client_id=client_id,
                credential=credential,
                batch_account_resource_id=batch_account_resource_id,
                storage_account_resource_id=storage_account_resource_id
            )
        )
    )
else:
    # fallback to local secrets if envrionment variables don't exist
    spark_client = aztk.spark.Client(config.load_aztk_secrets())


def test_submit_job():
    test_id = "submit-"
    app1 = aztk.spark.models.ApplicationConfiguration(
        name="pipy100",
        application="./examples/src/main/python/pi.py",
        application_args=[100]
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[100]
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id+base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0
    )
    try:
        job = spark_client.submit_job(job_configuration=job_configuration)
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
        application_args=[100]
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[100]
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id+base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        custom_scripts=None,
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=1,
        max_low_pri_nodes=0,
        worker_on_master=True
    )
    try:
        spark_client.submit_job(job_configuration=job_configuration)
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
        application_args=[100]
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[100]
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id+base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        custom_scripts=None,
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0
    )
    try:
        spark_client.submit_job(job_configuration=job_configuration)
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
        application_args=[100]
    )
    app2 = aztk.spark.models.ApplicationConfiguration(
        name="pipy101",
        application="./examples/src/main/python/pi.py",
        application_args=[100]
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id+base_job_id,
        applications=[app1, app2],
        vm_size="standard_f1",
        custom_scripts=None,
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=1,
        max_low_pri_nodes=0,
        worker_on_master=True
    )
    try:
        spark_client.submit_job(job_configuration=job_configuration)
        spark_client.wait_until_job_finished(job_configuration.id)

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
        application_args=[100]
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id+base_job_id,
        applications=[app1],
        vm_size="standard_f1",
        custom_scripts=None,
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0
    )
    try:
        spark_client.submit_job(job_configuration=job_configuration)
        spark_client.wait_until_job_finished(job_configuration.id)
        application = spark_client.get_application(job_id=job_configuration.id, application_name=app1.name)
        assert isinstance(application, aztk.spark.models.Application)
        assert application.exit_code == 0
        assert application.state == "completed"
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
        application_args=[100]
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id+base_job_id,
        applications=[app1],
        vm_size="standard_f1",
        custom_scripts=None,
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=2,
        max_low_pri_nodes=0
    )
    try:
        spark_client.submit_job(job_configuration=job_configuration)
        spark_client.wait_until_job_finished(job_configuration.id)

        application_log = spark_client.get_job_application_log(job_id=job_configuration.id, application_name=app1.name)

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
        application_args=[100]
    )
    job_configuration = aztk.spark.models.JobConfiguration(
        id=test_id+base_job_id,
        applications=[app1],
        vm_size="standard_f1",
        custom_scripts=None,
        spark_configuration=None,
        toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
        max_dedicated_nodes=1,
        max_low_pri_nodes=0,
        worker_on_master=True
    )
    try:
        spark_client.submit_job(job_configuration=job_configuration)
        spark_client.wait_until_job_finished(job_configuration.id)
        spark_client.delete_job(job_configuration.id)
        assert job_configuration.id not in spark_client.list_jobs()
        try:
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
        spark_client.delete_job(job_id)
    except (BatchErrorException, AztkError):
        pass
