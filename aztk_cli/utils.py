import datetime
import getpass
import subprocess
import sys
import threading
import time
from typing import List

import azure.batch.models as batch_models

from aztk import error, utils
from aztk.models import ClusterConfiguration
from aztk.spark import models
from aztk.utils import get_ssh_key

from . import log


def get_ssh_key_or_prompt(ssh_key, username, password, secrets_configuration):
    ssh_key = get_ssh_key.get_user_public_key(ssh_key, secrets_configuration)

    if username is not None and password is None and ssh_key is None:
        log.warning("It is recommended to use an SSH key for user creation instead of a password.")
        for i in range(3):
            if i > 0:
                log.error("Please try again.")
            password = getpass.getpass("Please input a password for user '{0}': ".format(username))
            confirm_password = getpass.getpass("Please confirm your password for user '{0}': ".format(username))
            if password != confirm_password:
                log.error("Password confirmation did not match.")
            elif not password:
                log.error("Password cannot be empty.")
            else:
                break
        else:
            raise error.AztkError(
                "Failed to get valid password, cannot add user to cluster. "
                "It is recommended that you provide a ssh public key in .aztk/secrets.yaml. "
                "Or provide an ssh-key or password with command line parameters (--ssh-key or --password). "
                "You may also run the 'aztk spark cluster add-user' command to add a user to this cluster.")
    return ssh_key, password


def print_cluster(client, cluster: models.Cluster, internal: bool = False):
    node_count = __pretty_node_count(cluster)

    log.info("")
    log.info("Cluster         %s", cluster.id)
    log.info("------------------------------------------")
    log.info("State:          %s", cluster.visible_state)
    log.info("Node Size:      %s", cluster.vm_size)
    log.info("Nodes:          %s", node_count)
    log.info("| Dedicated:    %s", __pretty_dedicated_node_count(cluster))
    log.info("| Low priority: %s", __pretty_low_pri_node_count(cluster))
    log.info("")

    print_format = "|{:^36}| {:^19} | {:^21}| {:^10} | {:^8} |"
    print_format_underline = "|{:-^36}|{:-^21}|{:-^22}|{:-^12}|{:-^10}|"
    if internal:
        log.info(print_format.format("Nodes", "State", "IP", "Dedicated", "Master"))
    else:
        log.info(print_format.format("Nodes", "State", "IP:Port", "Dedicated", "Master"))
    log.info(print_format_underline.format("", "", "", "", ""))

    if not cluster.nodes:
        return
    for node in cluster.nodes:
        remote_login_settings = client.cluster.get_remote_login_settings(cluster.id, node.id)
        if internal:
            ip = node.ip_address
        else:
            ip = "{}:{}".format(remote_login_settings.ip_address, remote_login_settings.port)
        log.info(
            print_format.format(
                node.id,
                node.state.value,
                ip,
                "*" if node.is_dedicated else "",
                "*" if node.id == cluster.master_node_id else "",
            ))
    log.info("")


def __pretty_node_count(cluster: models.Cluster) -> str:
    if cluster.pool.allocation_state is batch_models.AllocationState.resizing:
        return "{} -> {}".format(cluster.total_current_nodes, cluster.total_target_nodes)
    else:
        return "{}".format(cluster.total_current_nodes)


def __pretty_dedicated_node_count(cluster: models.Cluster) -> str:
    if (cluster.pool.allocation_state is batch_models.AllocationState.resizing or cluster.pool.state is
            batch_models.PoolState.deleting) and cluster.current_dedicated_nodes != cluster.target_dedicated_nodes:
        return "{} -> {}".format(cluster.current_dedicated_nodes, cluster.target_dedicated_nodes)
    else:
        return "{}".format(cluster.current_dedicated_nodes)


def __pretty_low_pri_node_count(cluster: models.Cluster) -> str:
    if (cluster.pool.allocation_state is batch_models.AllocationState.resizing or cluster.pool.state is
            batch_models.PoolState.deleting) and cluster.current_low_pri_nodes != cluster.target_low_pri_nodes:
        return "{} -> {}".format(cluster.current_low_pri_nodes, cluster.target_low_pri_nodes)
    else:
        return "{}".format(cluster.current_low_pri_nodes)


def print_clusters(clusters: List[models.Cluster]):
    print_format = "{:<34}| {:<10}| {:<20}| {:<7}"
    print_format_underline = "{:-<34}|{:-<11}|{:-<21}|{:-<7}"

    log.info(print_format.format("Cluster", "State", "VM Size", "Nodes"))
    log.info(print_format_underline.format("", "", "", ""))
    for cluster in clusters:
        node_count = __pretty_node_count(cluster)

        log.info(print_format.format(cluster.id, cluster.visible_state, cluster.vm_size, node_count))


def print_clusters_quiet(clusters: List[models.Cluster]):
    log.print("\n".join([str(cluster.id) for cluster in clusters]))


def stream_logs(client, cluster_id, application_name):
    current_bytes = 0
    while True:
        app_logs = client.cluster.get_application_log(
            id=cluster_id, application_name=application_name, tail=True, current_bytes=current_bytes)
        log.print(app_logs.log)
        if app_logs.application_state == "completed":
            return app_logs.exit_code
        current_bytes = app_logs.total_bytes
        time.sleep(3)


def ssh_in_master(
        client,
        cluster_id: str,
        cluster_configuration: models.ClusterConfiguration,
        username: str = None,
        webui: str = None,
        jobui: str = None,
        jobhistoryui: str = None,
        ports=None,
        host: bool = False,
        connect: bool = True,
        internal: bool = False,
):
    """
        SSH into head node of spark-app
        :param cluster_id: Id of the cluster to ssh in
        :param username: Username to use to ssh
        :param webui: Port for the spark master web ui (Local port)
        :param jobui: Port for the job web ui (Local port)
        :param ports: an list of local and remote ports
        :type ports: [[<local-port>, <remote-port>]]
    """
    # check if ssh is available, this throws OSError if ssh is not present
    subprocess.call(["ssh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get master node id from task (job and task are both named pool_id)
    cluster = client.cluster.get(cluster_id)

    master_node_id = cluster.master_node_id

    if master_node_id is None:
        raise error.ClusterNotReadyError("Master node has not yet been picked!")

    # get remote login settings for the user
    remote_login_settings = client.cluster.get_remote_login_settings(cluster.id, master_node_id)
    master_internal_node_ip = [node.ip_address for node in cluster.nodes if node.id == master_node_id][0]
    master_node_ip = remote_login_settings.ip_address
    master_node_port = remote_login_settings.port

    spark_web_ui_port = utils.constants.DOCKER_SPARK_WEB_UI_PORT
    spark_job_ui_port = utils.constants.DOCKER_SPARK_JOB_UI_PORT
    spark_job_history_ui_port = utils.constants.DOCKER_SPARK_JOB_UI_HISTORY_PORT

    ssh_command = utils.command_builder.CommandBuilder("ssh")

    # get ssh private key path if specified
    ssh_priv_key = client.secrets_configuration.ssh_priv_key
    if ssh_priv_key is not None:
        ssh_command.add_option("-i", ssh_priv_key)

    ssh_command.add_argument("-t")
    ssh_command.add_option("-L", "{0}:localhost:{1}".format(webui, spark_web_ui_port), enable=bool(webui))
    ssh_command.add_option("-L", "{0}:localhost:{1}".format(jobui, spark_job_ui_port), enable=bool(jobui))
    ssh_command.add_option(
        "-L", "{0}:localhost:{1}".format(jobhistoryui, spark_job_history_ui_port), enable=bool(jobui))

    if ports is not None:
        for port in ports:
            ssh_command.add_option("-L", "{0}:localhost:{1}".format(port[0], port[1]))
    if cluster_configuration and cluster_configuration.plugins:
        for plugin in cluster_configuration.plugins:
            for port in plugin.ports:
                if port.expose_publicly:
                    ssh_command.add_option("-L", "{0}:localhost:{1}".format(port.public_port, port.internal))

    user = username if username is not None else "<username>"
    if internal:
        ssh_command.add_argument("{0}@{1}".format(user, master_internal_node_ip))
    else:
        ssh_command.add_argument("{0}@{1} -p {2}".format(user, master_node_ip, master_node_port))

    if host is False:
        ssh_command.add_argument("'sudo docker exec -it spark /bin/bash'")

    command = ssh_command.to_str()

    if connect:
        subprocess.call(command, shell=True)

    return "\n\t{}\n".format(command)


def print_batch_exception(batch_exception):
    """
    Prints the contents of the specified Batch exception.
    :param batch_exception:
    """
    log.error("-------------------------------------------")
    log.error("Exception encountered:")
    if batch_exception.error and batch_exception.error.message and batch_exception.error.message.value:
        log.error(batch_exception.error.message.value)
        if batch_exception.error.values:
            log.error("")
            for mesg in batch_exception.error.values:
                log.error("%s:\t%s", mesg.key, mesg.value)
    log.error("-------------------------------------------")


def print_jobs(jobs: List[models.Job]):
    print_format = "{:<34}| {:<10}| {:<20}"
    print_format_underline = "{:-<34}|{:-<11}|{:-<21}"

    log.info(print_format.format("Job", "State", "Creation Time"))
    log.info(print_format_underline.format("", "", "", ""))
    for job in jobs:

        log.info(print_format.format(job.id, job.state, utc_to_local(job.creation_time)))


def print_job(client, job: models.Job):
    print_format = "{:<36}| {:<15}"

    log.info("")
    log.info("Job               %s", job.id)
    log.info("------------------------------------------")
    log.info("State:            %s", job.state)
    log.info("Transition Time:  %s", utc_to_local(job.state_transition_time))
    log.info("")

    if job.cluster:
        print_cluster_summary(job.cluster)
    else:
        if job.state == "completed":
            log.info("Cluster           %s", "Job completed, cluster deallocated.")
            log.info("")
        else:
            log.info(print_format.format("Cluster", "Provisioning"))
            log.info("")

    if job.applications:
        application_summary(job.applications)
    else:
        application_summary(client.job.list_applications(job.id))
    log.info("")


def node_state_count(cluster: models.Cluster):
    states = {}
    for node in cluster.nodes:
        states[node.state] = states.get(node.state, 0) + 1
    return states


def print_cluster_summary(cluster: models.Cluster):
    log.info("Cluster           %s", cluster.id)
    log.info("-" * 42)
    log.info("Nodes             %s", __pretty_node_count(cluster))
    log.info("| Dedicated:      %s", __pretty_dedicated_node_count(cluster))
    log.info("| Low priority:   %s", __pretty_low_pri_node_count(cluster))
    state_count = node_state_count(cluster)
    if state_count:
        log.info("| Node States:")
        for state in state_count:
            log.info("| \t%s: %d", state.name, state_count[state])
    log.info("Master:            %s", cluster.master_node_id or "Pending")
    log.info("")


def application_summary(applications):
    states = {"scheduling": 0}
    for state in batch_models.TaskState:
        states[state.name] = 0

    warn_scheduling = False

    for application in applications:
        if isinstance(application, str):
            states["scheduling"] += 1
            warn_scheduling = True
        else:
            states[application.state] += 1

    print_format = "{:<17} {:<14}"
    log.info("Applications")
    log.info("-" * 42)
    for state in states:
        if states[state] > 0:
            log.info(print_format.format(state + ":", states[state]))

    if warn_scheduling:
        log.warning("\nNo Spark applications will be scheduled until the master is selected.")


def print_applications(applications):
    print_format = "{:<36}| {:<15}| {:<16} | {:^9} |"
    print_format_underline = "{:-<36}|{:-<16}|{:-<18}|{:-<11}|"
    log.info(print_format.format("Applications", "State", "Transition Time", "Exit Code"))
    log.info(print_format_underline.format("", "", "", ""))

    warn_scheduling = False
    for name in applications:
        if applications[name] is None:
            log.info(print_format.format(name, "scheduling", "-", "-"))
            warn_scheduling = True
        else:
            application = applications[name]
            log.info(
                print_format.format(
                    application.name,
                    application.state,
                    utc_to_local(application.state_transition_time),
                    application.exit_code if application.exit_code is not None else "-",
                ))
    if warn_scheduling:
        log.warning("\nNo Spark applications will be scheduled until the master is selected.")


def print_application(application: models.Application):
    print_format = "{:<30}| {:<15}"

    log.info("")
    log.info("Application         %s", application.name)
    log.info("-" * 42)
    log.info(print_format.format("State", application.state))
    log.info(print_format.format("State transition time", utc_to_local(application.state_transition_time)))
    log.info("")


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in "|/-\\":
                yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.stop()

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write("\b")
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task, daemon=True).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime("%H:%M%p %d/%m/%y")


def print_cluster_conf(cluster_conf: ClusterConfiguration, wait: bool):
    user_configuration = cluster_conf.user_configuration
    log.info("-------------------------------------------")
    log.info("cluster id:              %s", cluster_conf.cluster_id)
    log.info("cluster toolkit:         %s %s", cluster_conf.toolkit.software, cluster_conf.toolkit.version)
    log.info("cluster size:            %s", cluster_conf.size + cluster_conf.size_low_priority)
    log.info(">        dedicated:      %s", cluster_conf.size)
    log.info(">     low priority:      %s", cluster_conf.size_low_priority)
    log.info("cluster vm size:         %s", cluster_conf.vm_size)
    log.info("subnet ID:               %s", cluster_conf.subnet_id)
    log.info("file shares:             %s",
             len(cluster_conf.file_shares) if cluster_conf.file_shares is not None else 0)
    log.info("gpu enabled:             %s", str(cluster_conf.gpu_enabled()))
    log.info("docker repo name:        %s", cluster_conf.get_docker_repo())
    if cluster_conf.get_docker_run_options():
        log.info("docker run options:      %s", cluster_conf.get_docker_run_options())
    log.info("wait for cluster:        %s", wait)
    if user_configuration:
        log.info("username:                %s", user_configuration.username)
        if user_configuration.password:
            log.info("Password: %s", "*" * len(user_configuration.password))
    log.info("Plugins:")
    if not cluster_conf.plugins:
        log.info("    None Configured")
    else:
        for plugin in cluster_conf.plugins:
            log.info("  - %s", plugin.name)
    log.info("-------------------------------------------")


def log_property(label: str, value: str):
    label += ":"
    log.info("{0:30} {1}".format(label, value))


def log_node_copy_output(node_output):
    log.info("-" * (len(node_output.id) + 4))
    log.info("| %s |", node_output.id)
    log.info("-" * (len(node_output.id) + 4))
    if node_output.error:
        log.error(node_output.error)
    else:
        log.print("Copy successful")


def log_node_run_output(node_output):
    log.info("-" * (len(node_output.id) + 4))
    log.info("| %s |", node_output.id)
    log.info("-" * (len(node_output.id) + 4))
    if node_output.error:
        log.error("%s\n", node_output.error)
    else:
        log.print(node_output.output)
