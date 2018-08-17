"""
    Diagnostic program that runs on each node in the cluster
    This program must be run with sudo
"""
import io
import json
import os
import socket
import sys
import tarfile
from subprocess import STDOUT, CalledProcessError, check_output
from zipfile import ZIP_DEFLATED, ZipFile

import docker    # pylint: disable=import-error


def main():
    brief = sys.argv[1] == "True"

    # docker container diagnostics
    docker_client = docker.from_env()

    zipf = create_zip_archive()

    if brief:
        for filename, data in get_brief_diagnostics():
            print("writing {} to zip", filename)
            zipf.writestr(filename, data=data)
    else:
        # general node diagnostics
        zipf.writestr("hostname.txt", data=get_hostname())
        zipf.writestr("df.txt", data=get_disk_free())

        for filename, data in get_docker_diagnostics(docker_client):
            zipf.writestr(filename, data=data)

    zipf.close()


def create_zip_archive():
    zip_file_path = "/tmp/debug.zip"
    return ZipFile(zip_file_path, "w", ZIP_DEFLATED)


def get_hostname():
    return socket.gethostname()


def cmd_check_output(cmd):
    try:
        output = check_output(cmd, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        return "CMD: {0}\n" "returncode: {1}" "output: {2}".format(e.cmd, e.returncode, e.output)
    else:
        return output


def get_disk_free():
    return cmd_check_output("df -h")


def get_docker_diagnostics(docker_client):
    """
        returns list of tuples (filename, data) to be written in the zip
    """
    output = []
    output.append(get_docker_images(docker_client))
    logs = get_docker_containers(docker_client)
    for item in logs:
        output.append(item)

    return output


def get_docker_images(docker_client):
    output = ""
    try:
        images = docker_client.images.list()
        for image in images:
            output += json.dumps(image.attrs, sort_keys=True, indent=4)
        return ("docker-images.txt", output)
    except docker.errors.APIError as e:
        return ("docker-images.err", e.__str__())


def get_docker_containers(docker_client):
    container_attrs = ""
    logs = []
    try:
        containers = docker_client.containers.list()
        for container in containers:
            container_attrs += json.dumps(container.attrs, sort_keys=True, indent=4)
            # get docker container logs
            logs.append((container.name + "/docker.log", container.logs()))
            logs.append(get_docker_process_status(container))
            if container.name == "spark":    # TODO: find a more robust way to get specific info off specific containers
                logs.extend(get_container_aztk_script(container))
                logs.extend(get_spark_logs(container))
                logs.extend(get_spark_app_logs(container))

        logs.append(("docker-containers.txt", container_attrs))
        return logs
    except docker.errors.APIError as e:
        return [("docker-containers.err", e.__str__())]


def get_docker_process_status(container):
    try:
        exit_code, output = container.exec_run("ps faux", privileged=True)
        out_file_name = container.name + "/ps_aux.txt"
        if exit_code == 0:
            return (out_file_name, output)
        else:
            return (out_file_name, "exit_code: {0}\n{1}".format(exit_code, output))
    except docker.errors.APIError as e:
        return (container.name + "ps_aux.err", e.__str__())


def get_container_aztk_script(container):
    aztk_path = "/mnt/batch/tasks/startup/wd"
    try:
        stream, _ = container.get_archive(aztk_path)    # second item is stat info
        return extract_tar_in_memory(container, stream)
    except docker.errors.APIError as e:
        return (container.name + "/" + "aztk-scripts.err", e.__str__())


def get_spark_logs(container):
    spark_logs_path = "/home/spark-current/logs"
    try:
        stream, _ = container.get_archive(spark_logs_path)    # second item is stat info
        return extract_tar_in_memory(container, stream)
    except docker.errors.APIError as e:
        return [(container.name + "/" + "spark-logs.err", e.__str__())]


def get_spark_app_logs(container):
    spark_app_logs_path = "/home/spark-current/work"
    try:
        stream, _ = container.get_archive(spark_app_logs_path)
        return extract_tar_in_memory(container, stream)
    except docker.errors.APIError as e:
        return [(container.name + "/" + "spark-work-logs.err", e.__str__())]


def filter_members(members):
    skip_files = ["id_rsa", "id_rsa.pub", "docker.log"]
    skip_extensions = [".pyc", ".zip"]
    skip_directories = [".venv"]
    for tarinfo in members:
        member_path = os.path.normpath(tarinfo.name).split(os.sep)
        if (not any(directory in skip_directories for directory in member_path)
                and os.path.basename(tarinfo.name) not in skip_files
                and os.path.splitext(tarinfo.name)[1] not in skip_extensions):
            yield tarinfo


def extract_tar_in_memory(container, data):
    data = io.BytesIO(b"".join([item for item in data]))
    tarf = tarfile.open(fileobj=data)
    logs = []
    for member in filter_members(tarf):
        file_bytes = tarf.extractfile(member)
        if file_bytes is not None:
            logs.append((container.name + "/" + member.name, b"".join(file_bytes.readlines())))
    return logs


def get_brief_diagnostics():
    batch_dir = "/mnt/batch/tasks/startup/"
    files = ["stdout.txt", "stderr.txt", "wd/logs/docker.log"]
    logs = []
    for file_name in files:
        try:
            logs.append((file_name, open(batch_dir + file_name, "rb").read()))
            # print("LOG:", (file_name, open(batch_dir+file_name, 'rb').read()))
        except FileNotFoundError as e:
            print("file not found", e)
            logs.append((file_name, bytes(e.__str__(), encoding="utf-8")))
    return logs


if __name__ == "__main__":
    main()
