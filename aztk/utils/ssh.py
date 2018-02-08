'''
    SSH utils
'''
import asyncio
import io
import os
import select
import socketserver as SocketServer
import sys
from concurrent.futures import ThreadPoolExecutor

import paramiko

from . import helpers


def connect(hostname,
            port=22,
            username=None,
            password=None,
            pkey=None):

    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if pkey:
        ssh_key = paramiko.RSAKey.from_private_key(file_obj=io.StringIO(pkey))
    else:
        ssh_key = None

    client.connect(
        hostname,
        port=port,
        username=username,
        password=password,
        pkey=ssh_key
    )

    return client


def node_exec_command(command, container_name, username, hostname, port, ssh_key=None, password=None):
    client = connect(hostname=hostname, port=port, username=username, password=password, pkey=ssh_key)
    docker_exec = 'sudo docker exec 2>&1 -t {0} /bin/bash -c \'set -e; set -o pipefail; {1}; wait\''.format(container_name, command)
    stdin, stdout, stderr = client.exec_command(docker_exec, get_pty=True)
    [print(line.decode('utf-8')) for line in stdout.read().splitlines()]
    client.close()


async def clus_exec_command(command, container_name, username, nodes, ports=None, ssh_key=None, password=None):
    await asyncio.wait(
        [asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(),
                                                  node_exec_command,
                                                  command,
                                                  container_name,
                                                  username,
                                                  node.ip_address,
                                                  node.port,
                                                  ssh_key,
                                                  password) for node in nodes]
    )


def node_copy(container_name, source_path, destination_path, username, hostname, port, ssh_key=None, password=None):
    client = connect(hostname=hostname, port=port, username=username, password=password, pkey=ssh_key)
    sftp_client = client.open_sftp()

    try:
        # put the file in /tmp on the host
        tmp_file = '/tmp/' + os.path.basename(source_path)
        sftp_client.put(source_path, tmp_file)
        # move to correct destination on container
        docker_command = 'sudo docker cp {0} {1}:{2}'.format(tmp_file, container_name, destination_path)
        _, stdout, _ = client.exec_command(docker_command, get_pty=True)
        [print(line.decode('utf-8')) for line in stdout.read().splitlines()]
        # clean up
        sftp_client.remove(tmp_file)
    except (IOError, PermissionError) as e:
        print(e)

    client.close()

    #TODO: progress bar

async def clus_copy(container_name, username, nodes, source_path, destination_path, ssh_key=None, password=None):
    await asyncio.gather(
        *[asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(),
                                                   node_copy,
                                                   container_name,
                                                   source_path,
                                                   destination_path,
                                                   username,
                                                   node.ip_address,
                                                   node.port,
                                                   ssh_key,
                                                   password) for node in nodes
        ])
