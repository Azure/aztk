"""
    SSH utils
"""
import asyncio
import io
import logging
import os
import select
import socket
import socketserver as SocketServer
import threading
from concurrent.futures import ThreadPoolExecutor

from aztk.error import AztkError
from aztk.models import NodeOutput


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


# pylint: disable=no-member
class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            channel = self.ssh_transport.open_channel("direct-tcpip",
                                                      (self.chain_host, self.chain_port), self.request.getpeername())
        except Exception as e:
            logging.debug("Incoming request to %s:%d failed: %s", self.chain_host, self.chain_port, repr(e))
            return
        if channel is None:
            logging.debug("Incoming request to %s:%d was rejected by the SSH server.", self.chain_host, self.chain_port)
            return

        logging.debug(
            "Connected!  Tunnel open %r -> %r -> %r",
            self.request.getpeername(),
            channel.getpeername(),
            (self.chain_host, self.chain_port),
        )
        while True:
            r, _, _ = select.select([self.request, channel], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if not data:
                    break
                channel.send(data)
            if channel in r:
                data = channel.recv(1024)
                if not data:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        channel.close()
        self.request.close()
        logging.debug("Tunnel closed from %r", peername)


def forward_tunnel(local_port, remote_host, remote_port, transport):
    class SubHandler(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport

    thread = threading.Thread(target=ForwardServer(("", local_port), SubHandler).serve_forever, daemon=True)
    thread.start()
    return thread


def connect(hostname, port=22, username=None, password=None, pkey=None, timeout=None):
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if pkey:
        ssh_key = paramiko.RSAKey.from_private_key(file_obj=io.StringIO(pkey))
    else:
        ssh_key = None

    timeout = timeout or 20
    logging.debug("Connecting to %s@%s:%d, timeout=%d", username, hostname, port, timeout)
    try:
        client.connect(hostname, port=port, username=username, password=password, pkey=ssh_key, timeout=timeout)
    except socket.timeout:
        raise AztkError("Connection timed out to: {}".format(hostname))

    return client


def forward_ports(client, port_forward_list):
    threads = []
    if not port_forward_list:
        return threads

    for port_forwarding_specification in port_forward_list:
        threads.append(
            forward_tunnel(
                port_forwarding_specification.remote_port,
                "127.0.0.1",
                port_forwarding_specification.local_port,
                client.get_transport(),
            ))
    return threads


def node_exec_command(node_id,
                      command,
                      username,
                      hostname,
                      port,
                      ssh_key=None,
                      password=None,
                      container_name=None,
                      timeout=None):
    try:
        client = connect(
            hostname=hostname, port=port, username=username, password=password, pkey=ssh_key, timeout=timeout)
    except AztkError as e:
        return NodeOutput(node_id, None, e)
    if container_name:
        cmd = "sudo docker exec 2>&1 -t {0} /bin/bash -c 'set -e; set -o pipefail; {1}; wait'".format(
            container_name, command)
    else:
        cmd = "/bin/bash 2>&1 -c 'set -e; set -o pipefail; {0}; wait'".format(command)
    _, stdout, _ = client.exec_command(cmd, get_pty=True)
    output = stdout.read().decode("utf-8")
    client.close()
    return NodeOutput(node_id, output, None)


async def clus_exec_command(command,
                            username,
                            nodes,
                            ports=None,
                            ssh_key=None,
                            password=None,
                            container_name=None,
                            timeout=None):
    return await asyncio.gather(*[
        asyncio.get_event_loop().run_in_executor(
            ThreadPoolExecutor(),
            node_exec_command,
            node.id,
            command,
            username,
            node_rls.ip_address,
            node_rls.port,
            ssh_key,
            password,
            container_name,
            timeout,
        ) for node, node_rls in nodes
    ])


def copy_from_node(
        node_id,
        source_path,
        destination_path,
        username,
        hostname,
        port,
        ssh_key=None,
        password=None,
        container_name=None,
        timeout=None,
):
    try:
        client = connect(
            hostname=hostname, port=port, username=username, password=password, pkey=ssh_key, timeout=timeout)
    except AztkError as e:
        return NodeOutput(node_id, False, e)
    sftp_client = client.open_sftp()
    try:
        if destination_path:
            destination_path = os.path.join(
                os.path.dirname(destination_path), node_id, os.path.basename(destination_path))
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            with open(destination_path, "wb") as f:
                sftp_client.getfo(source_path, f)
                return NodeOutput(node_id, f, None)
        else:
            import tempfile

            # create 2mb temporary file
            f = tempfile.SpooledTemporaryFile(2 * 1024**3)
            sftp_client.getfo(source_path, f)
            return NodeOutput(node_id, f, None)
    except OSError as e:
        return NodeOutput(node_id, None, e)
    finally:
        sftp_client.close()
        client.close()


def node_copy(
        node_id,
        source_path,
        destination_path,
        username,
        hostname,
        port,
        ssh_key=None,
        password=None,
        container_name=None,
        timeout=None,
):
    try:
        client = connect(
            hostname=hostname, port=port, username=username, password=password, pkey=ssh_key, timeout=timeout)
    except AztkError as e:
        return NodeOutput(node_id, None, e)
    sftp_client = client.open_sftp()
    try:
        if container_name:
            # put the file in /tmp on the host
            tmp_file = "/tmp/" + os.path.basename(source_path)
            sftp_client.put(source_path, tmp_file)
            # move to correct destination on container
            docker_command = "sudo docker cp {0} {1}:{2}".format(tmp_file, container_name, destination_path)
            _, stdout, _ = client.exec_command(docker_command, get_pty=True)
            output = stdout.read().decode("utf-8")
            # clean up
            sftp_client.remove(tmp_file)
            return NodeOutput(node_id, output, None)
        else:
            output = sftp_client.put(source_path, destination_path).__str__()
            return NodeOutput(node_id, output, None)
    except (IOError, PermissionError) as e:
        return NodeOutput(node_id, None, e)
    finally:
        sftp_client.close()
        client.close()
    # TODO: progress bar


async def clus_copy(
        username,
        nodes,
        source_path,
        destination_path,
        ssh_key=None,
        password=None,
        container_name=None,
        get=False,
        timeout=None,
):
    return await asyncio.gather(*[
        asyncio.get_event_loop().run_in_executor(
            ThreadPoolExecutor(),
            copy_from_node if get else node_copy,
            node.id,
            source_path,
            destination_path,
            username,
            node_rls.ip_address,
            node_rls.port,
            ssh_key,
            password,
            container_name,
            timeout,
        ) for node, node_rls in nodes
    ])


def node_ssh(username, hostname, port, ssh_key=None, password=None, port_forward_list=None, timeout=None):
    try:
        client = connect(
            hostname=hostname, port=port, username=username, password=password, pkey=ssh_key, timeout=timeout)
        forward_ports(client=client, port_forward_list=port_forward_list)
    except AztkError as e:
        raise e

    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # catch and ignore so stacktrace isn't printed
        pass
