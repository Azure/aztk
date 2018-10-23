import os
import sys
import time

import aztk.spark
from aztk.error import AztkError

# set your secrets
secrets_configuration = aztk.spark.models.SecretsConfiguration(
    service_principal=aztk.spark.models.ServicePrincipalConfiguration(
        tenant_id="<org>.onmicrosoft.com",
        client_id="",
        credential="",
        batch_account_resource_id="",
        storage_account_resource_id="",
    ),
    ssh_pub_key="")

# set path to root of repository to reference files
ROOT_PATH = os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

# create a client
client = aztk.spark.Client(secrets_configuration)

# list available clusters
clusters = client.cluster.list()

# define spark configuration
configuration_file_path = os.path.join(ROOT_PATH, 'aztk_cli', 'config')
spark_configuration = aztk.spark.models.SparkConfiguration(
    spark_defaults_conf=os.path.join(configuration_file_path, 'spark-defaults.conf'),
    spark_env_sh=os.path.join(configuration_file_path, 'spark-env.sh'),
    core_site_xml=os.path.join(configuration_file_path, 'core-site.xml'),
    jars=[
        os.path.join(configuration_file_path, 'jars', jar)
        for jar in os.listdir(os.path.join(configuration_file_path, 'jars'))
    ])

# configure my cluster
cluster_configuration = aztk.spark.models.ClusterConfiguration(
    cluster_id="sdk-test",
    toolkit=aztk.spark.models.SparkToolkit(version="2.3.0"),
    size=2,
    vm_size="standard_f2",
    spark_configuration=spark_configuration)

# create a cluster, and wait until it is ready
try:
    cluster = client.cluster.create(cluster_configuration, wait=True)
except AztkError as e:
    raise e

# get details of the cluster
cluster = client.cluster.get(cluster.id)

# # create a user for the cluster
client.cluster.create_user(cluster.id, "sdk_example_user", "example_password")

# define a Spark application to run
app1 = aztk.spark.models.ApplicationConfiguration(
    name="pipy1",
    application=os.path.join(ROOT_PATH, 'examples', 'src', 'main', 'python', 'pi.py'),
    application_args="10")

# submit the application and wait until it is finished running
client.cluster.submit(cluster.id, app1)

# get status of application
status = client.cluster.get_application_state(cluster_configuration.cluster_id, app1.name)

# stream logs of app, print to console as it runs
current_bytes = 0
while True:
    app1_logs = client.cluster.get_application_log(
        id=cluster_configuration.cluster_id, application_name=app1.name, tail=True, current_bytes=current_bytes)

    print(app1_logs.log, end="")

    if app1_logs.application_state == 'completed':
        break
    current_bytes = app1_logs.total_bytes
    time.sleep(1)

# alternatively, get entire log for application, print to console
app1_logs = client.cluster.get_application_log(id=cluster_configuration.cluster_id, application_name=app1.name)

# delete the cluster
client.cluster.delete(cluster.id)
