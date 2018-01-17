import sys, os, time
import aztk.models
import aztk.spark
from aztk.error import AztkError

# set your secrets
secrets_confg = aztk.spark.models.SecretsConfiguration(
    service_principal=aztk.models.ServicePrincipalConfiguration(
        tenant_id="<org>.onmicrosoft.com",
        client_id="",
        credential="",
        batch_account_resource_id="",
        storage_account_resource_id="",
    ),
    ssh_pub_key=""
)

# set path to root of repository to reference files
ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))

# create a client
client = aztk.spark.Client(secrets_confg)

# list available clusters
clusters = client.list_clusters()

# define a custom script
custom_script = aztk.spark.models.CustomScript(
    name="simple.sh",
    script=os.path.join(ROOT_PATH, 'custom-scripts', 'simple.sh'),
    run_on="all-nodes")

# define spark configuration
spark_conf = aztk.spark.models.SparkConfiguration(
    spark_defaults_conf=os.path.join(ROOT_PATH, 'config', 'spark-defaults.conf'),
    spark_env_sh=os.path.join(ROOT_PATH, 'config', 'spark-env.sh')
)

# configure my cluster
cluster_config = aztk.spark.models.ClusterConfiguration(
    cluster_id="sdk_test",
    vm_low_pri_count=2,
    vm_size="standard_f2",
    custom_scripts=[custom_script],
    spark_configuration=spark_conf
)

# create a cluster, and wait until it is ready
try:
    cluster = client.create_cluster(cluster_config)
    cluster = client.wait_until_cluster_is_ready(cluster.id)
except AztkError as e:
    print(e.message)
    sys.exit()

# get details of specific cluster
cluster = client.get_cluster(cluster_config.cluster_id)

# # create a user for the cluster
client.create_user(cluster.id, "sdk_example_user", "example_password")

# create some apps to run
app1 = aztk.spark.models.Application(
    name="pipy1",
    application=os.path.join(ROOT_PATH, 'examples', 'src', 'main', 'python', 'pi.py'),
    application_args="10"
)

app2 = aztk.spark.models.Application(
    name="pipy2",
    application=os.path.join(ROOT_PATH, 'examples', 'src', 'main', 'python', 'pi.py'),
    application_args="20"
)

app3 = aztk.spark.models.Application(
    name="pipy3",
    application=os.path.join(ROOT_PATH, 'examples', 'src', 'main', 'python', 'pi.py'),
    application_args="30"
)

# submit an app and wait until it is finished running
client.submit(cluster.id, app1)
client.wait_until_application_done(cluster.id, app1.name)

# get logs for app, print to console
app1_logs = client.get_application_log(cluster_id=cluster_config.cluster_id, application_name=app1.name)
print(app1_logs.log)

# submit some other apps to the cluster in parallel
client.submit_all_applications(cluster.id, [app2, app3])

# get status of app
status = client.get_application_status(cluster_config.cluster_id, app2.name)

# stream logs of app, print to console as it runs
current_bytes = 0
while True:
    app2_logs = client.get_application_log(
        cluster_id=cluster_config.cluster_id,
        application_name=app2.name,
        tail=True,
        current_bytes=current_bytes)

    print(app2_logs.log, end="")

    if app2_logs.application_state == 'completed':
        break
    current_bytes = app2_logs.total_bytes
    time.sleep(1)

# wait until all jobs finish, then delete the cluster
client.wait_until_applications_done(cluster.id)
client.delete_cluster(cluster.id)
