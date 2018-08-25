import asyncio

import azure.batch.models.batch_error as batch_error

import aztk.models as models
from aztk import error
from aztk.utils import ssh as ssh_lib
from aztk.utils import helpers


def cluster_copy(
        cluster_operations,
        cluster_id,
        source_path,
        destination_path=None,
        container_name=None,
        internal=False,
        get=False,
        timeout=None,
):
    cluster = cluster_operations.get(cluster_id)
    pool, nodes = cluster.pool, list(cluster.nodes)
    if internal:
        cluster_nodes = [(node, models.RemoteLogin(ip_address=node.ip_address, port="22")) for node in nodes]
    else:
        cluster_nodes = [(node, cluster_operations.get_remote_login_settings(pool.id, node.id)) for node in nodes]

    try:
        generated_username, ssh_key = cluster_operations.generate_user_on_cluster(pool.id, nodes)
    except batch_error.BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))

    try:
        output = asyncio.get_event_loop().run_until_complete(
            ssh_lib.clus_copy(
                container_name=container_name,
                username=generated_username,
                nodes=cluster_nodes,
                source_path=source_path,
                destination_path=destination_path,
                ssh_key=ssh_key.exportKey().decode("utf-8"),
                get=get,
                timeout=timeout,
            ))
        return output
    except (OSError, batch_error.BatchErrorException) as exc:
        raise exc
    finally:
        cluster_operations.delete_user_on_cluster(pool.id, nodes, generated_username)
