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


def node_exec_command(node_id, command, username, hostname, port, ssh_key=None, password=None, container_name=None):
    client = connect(hostname=hostname, port=port, username=username, password=password, pkey=ssh_key)
    if container_name:
        cmd = 'sudo docker exec 2>&1 -t {0} /bin/bash -c \'set -e; set -o pipefail; {1}; wait\''.format(container_name, command)
    else:
        cmd = '/bin/bash 2>&1 -c \'set -e; set -o pipefail; {0}; wait\''.format(command)
    stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
    output = [line.decode('utf-8') for line in stdout.read().splitlines()]
    client.close()
    return (node_id, output)


async def clus_exec_command(command, username, nodes, ports=None, ssh_key=None, password=None, container_name=None):
    return await asyncio.gather(
        *[asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(),
                                                   node_exec_command,
                                                   node.id,
                                                   command,
                                                   username,
                                                   node_rls.ip_address,
                                                   node_rls.port,
                                                   ssh_key,
                                                   password,
                                                   container_name) for node, node_rls in nodes]
    )


def copy_from_node(node_id, source_path, destination_path, username, hostname, port, ssh_key=None, password=None, container_name=None):
    client = connect(hostname=hostname, port=port, username=username, password=password, pkey=ssh_key)
    sftp_client = client.open_sftp()
    try:
        destination_path = os.path.join(os.path.dirname(destination_path), node_id, os.path.basename(destination_path))
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, 'wb') as f: #SpooledTemporaryFile instead??
            sftp_client.getfo(source_path, f)
            return (node_id, True, None)
    except OSError as e:
        return (node_id, False, e)
    finally:
        sftp_client.close()
        client.close()


def node_copy(node_id, source_path, destination_path, username, hostname, port, ssh_key=None, password=None, container_name=None):
    client = connect(hostname=hostname, port=port, username=username, password=password, pkey=ssh_key)
    sftp_client = client.open_sftp()
    try:
        if container_name:
            # put the file in /tmp on the host
            tmp_file = '/tmp/' + os.path.basename(source_path)
            sftp_client.put(source_path, tmp_file)
            # move to correct destination on container
            docker_command = 'sudo docker cp {0} {1}:{2}'.format(tmp_file, container_name, destination_path)
            _, stdout, _ = client.exec_command(docker_command, get_pty=True)
            output = [line.decode('utf-8') for line in stdout.read().splitlines()]
            # clean up
            sftp_client.remove(tmp_file)
            return (node_id, True, None)
        else:
            output = sftp_client.put(source_path, destination_path).__str__()
            return (node_id, True, None)
    except (IOError, PermissionError) as e:
        return (node_id, False, e)
    finally:
        sftp_client.close()
        client.close()
    #TODO: progress bar


async def clus_copy(username, nodes, source_path, destination_path, ssh_key=None, password=None, container_name=None, get=False):
    return await asyncio.gather(
        *[asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(),
                                                   copy_from_node if get else node_copy,
                                                   node.id,
                                                   source_path,
                                                   destination_path,
                                                   username,
                                                   node_rls.ip_address,
                                                   node_rls.port,
                                                   ssh_key,
                                                   password,
                                                   container_name) for node, node_rls in nodes]
    )
