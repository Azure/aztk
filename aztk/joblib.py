import time
import io
from typing import List
from aztk.core import CommandBuilder
import azure.batch.models as batch_models
import azure.batch.models.batch_error as batch_error
from . import util, log, constants


class Job():

    def __init__(self, batch_client, blob_client):
        self.batch_client = batch_client
        self.blob_client = blob_client

    output_file = constants.TASK_WORKING_DIR + \
        "/" + constants.SPARK_SUBMIT_LOGS_FILE

    def get_node(self, node_id: str, cluster_id: str) -> batch_models.ComputeNode:
        return self.batch_client.compute_node.get(cluster_id, node_id)

    def app_submit_cmd(
            self,
            cluster_id: str,
            name: str,
            app: str,
            app_args: str,
            main_class: str,
            jars: List[str],
            py_files: List[str],
            files: List[str],
            driver_java_options: str,
            driver_library_path: str,
            driver_class_path: str,
            driver_memory: str,
            executor_memory: str,
            driver_cores: str,
            executor_cores: str):
        master_id = util.get_master_node_id(cluster_id, self.batch_client)
        master_ip = self.get_node(master_id, cluster_id).ip_address

        # get pool data from pool meta key/value store
        pool = self.batch_client.pool.get(cluster_id)

        spark_home = constants.DOCKER_SPARK_HOME

        # 2>&1 redirect stdout and stderr to be in the same file
        spark_submit_cmd = CommandBuilder(
            '{0}/bin/spark-submit >> {1} 2>&1'.format(spark_home, constants.SPARK_SUBMIT_LOGS_FILE))
        spark_submit_cmd.add_option(
            '--master', 'spark://{0}:7077'.format(master_ip))
        spark_submit_cmd.add_option('--name', name)
        spark_submit_cmd.add_option('--class', main_class)
        spark_submit_cmd.add_option('--jars', jars and ','.join(jars))
        spark_submit_cmd.add_option('--py-files', py_files and ','.join(py_files))
        spark_submit_cmd.add_option('--jars', files and ','.join(files))
        spark_submit_cmd.add_option('--driver-java-options', driver_java_options)
        spark_submit_cmd.add_option('--driver-library-path', driver_library_path)
        spark_submit_cmd.add_option('--driver-class-path', driver_class_path)
        spark_submit_cmd.add_option('--driver-memory', driver_memory)
        spark_submit_cmd.add_option('--executor-memory', executor_memory)
        spark_submit_cmd.add_option('--driver-cores', driver_cores)
        spark_submit_cmd.add_option('--executor-cores', executor_cores)

        spark_submit_cmd.add_argument(
            '/batch/workitems/{0}/{1}/{2}/wd/'.format(cluster_id, "job-1", name) +
            app + ' ' + ' '.join(app_args))

        docker_exec_cmd = CommandBuilder('sudo docker exec')
        docker_exec_cmd.add_option('-e', 'PYSPARK_PYTHON=/usr/bin/python3')
        docker_exec_cmd.add_option('-i', constants.DOCKER_SPARK_CONTAINER_NAME)
        docker_exec_cmd.add_argument(spark_submit_cmd.to_str())

        return [
            docker_exec_cmd.to_str()
        ]

    def submit_app(
            self,
            cluster_id: str,
            name: str,
            app: str,
            app_args: List[str],
            wait: bool,
            main_class: str,
            jars: List[str],
            py_files: List[str],
            files: List[str],
            driver_java_options: str,
            driver_library_path: str,
            driver_class_path: str,
            driver_memory: str,
            executor_memory: str,
            driver_cores: str,
            executor_cores: str):
        """
        Submit a spark app
        """

        resource_files = []

        app_resource_file = util.upload_file_to_container(container_name=name, file_path=app, blob_client=self.blob_client, use_full_path=False)
        # Upload application file
        resource_files.append(app_resource_file)

        # Upload dependent JARS
        for jar in jars:
            resource_files.append(
                util.upload_file_to_container(container_name=name, file_path=jar, blob_client=self.blob_client, use_full_path=True))

        # Upload dependent python files
        for py_file in py_files:
            resource_files.append(
                util.upload_file_to_container(container_name=name, file_path=py_file, blob_client=self.blob_client, use_full_path=True))

        # Upload other dependent files
        for file in files:
            resource_files.append(
                util.upload_file_to_container(container_name=name, file_path=file, blob_client=self.blob_client, use_full_path=True))

        # create command to submit task
        cmd = self.app_submit_cmd(
            cluster_id=cluster_id,
            name=name,
            app=app_resource_file.file_path,
            app_args=app_args,
            main_class=main_class,
            jars=jars,
            py_files=py_files,
            files=files,
            driver_java_options=driver_java_options,
            driver_library_path=driver_library_path,
            driver_class_path=driver_class_path,
            driver_memory=driver_memory,
            executor_memory=executor_memory,
            driver_cores=driver_cores,
            executor_cores=executor_cores)

        # Get pool size
        pool = self.batch_client.pool.get(cluster_id)
        pool_size = util.get_cluster_total_target_nodes(pool)

        # Affinitize task to master node
        master_node_affinity_id = util.get_master_node_id(cluster_id, self.batch_client)

        # Create task
        task = batch_models.TaskAddParameter(
            id=name,
            affinity_info=batch_models.AffinityInformation(
                affinity_id=master_node_affinity_id),
            command_line=util.wrap_commands_in_shell(cmd),
            resource_files=resource_files,
            user_identity=batch_models.UserIdentity(
                auto_user=batch_models.AutoUserSpecification(
                    scope=batch_models.AutoUserScope.task,
                    elevation_level=batch_models.ElevationLevel.admin))
        )

        # Add task to batch job (which has the same name as cluster_id)
        job_id = cluster_id
        self.batch_client.task.add(job_id=job_id, task=task)

        # Wait for the app to finish
        if wait:
            self.read_log(cluster_id, name, tail=True)

    def wait_for_app_to_be_running(self, cluster_id: str, app_name: str) -> batch_models.CloudTask:
        """
            Wait for the batch task to leave the waiting state into running(or completed if it was fast enough)
        """
        while True:
            task = self.batch_client.task.get(cluster_id, app_name)

            if task.state is batch_models.TaskState.active or task.state is batch_models.TaskState.preparing:
                log.info("Task is waiting to be scheduled.")
                time.sleep(5)
            else:
                return task

    def check_task_node_exist(self, cluster_id: str, task: batch_models.CloudTask) -> bool:
        try:
            self.batch_client.compute_node.get(
                cluster_id, task.node_info.node_id)
            return True
        except batch_error.BatchErrorException:
            return False

    def get_output_file_properties(self, cluster_id: str, app_name: str):
        while True:
            try:
                file = util.get_file_properties(
                    cluster_id, app_name, self.output_file, self.batch_client)
                return file
            except batch_error.BatchErrorException as e:
                if e.response.status_code == 404:
                    log.info("Output file hasn't been created yet")
                    time.sleep(5)
                    continue
                else:
                    raise e

    def read_log(self, cluster_id: str, app_name: str, tail=False):
        job_id = cluster_id
        task_id = app_name

        current_bytes = 0

        task = self.wait_for_app_to_be_running(cluster_id, app_name)

        if not self.check_task_node_exist(cluster_id, task):
            log.error("The app ran on doesn't exists anymore(Node id: %s)!",
                      task.node_info.node_id)
            return

        while True:
            file = self.get_output_file_properties(cluster_id, app_name)
            target_bytes = file.content_length

            if target_bytes != current_bytes:
                ocp_range = None

                if tail:
                    ocp_range = "bytes={0}-{1}".format(
                        current_bytes, target_bytes - 1)

                stream = self.batch_client.file.get_from_task(
                    job_id, task_id, self.output_file, batch_models.FileGetFromTaskOptions(ocp_range=ocp_range))
                content = util.read_stream_as_string(stream)

                print(content, end="")
                current_bytes = target_bytes

                if not tail:
                    return

            if task.state is batch_models.TaskState.completed:
                log.info("Spark application is completed!")
                return
            task = self.batch_client.task.get(cluster_id, app_name)

            time.sleep(5)
