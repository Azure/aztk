import aztk.error as error
import aztk.models as models
from aztk.utils import ssh as ssh_lib


def node_run(base_client, cluster_id, node_id, command, internal, container_name=None, timeout=None):
    cluster = base_client.get(cluster_id)
    pool, nodes = cluster.pool, list(cluster.nodes)
    try:
        node = next(node for node in nodes if node.id == node_id)
    except StopIteration:
        raise error.AztkError("Node with id {} not found".format(node_id))
    if internal:
        node_rls = models.RemoteLogin(ip_address=node.ip_address, port="22")
    else:
        node_rls = base_client.get_remote_login_settings(pool.id, node.id)
    try:
        generated_username, ssh_key = base_client.generate_user_on_node(pool.id, node.id)
        output = ssh_lib.node_exec_command(
            node.id,
            command,
            generated_username,
            node_rls.ip_address,
            node_rls.port,
            ssh_key=ssh_key.exportKey().decode("utf-8"),
            container_name=container_name,
            timeout=timeout,
        )
        return output
    finally:
        base_client.delete_user_on_node(cluster_id, node.id, generated_username)
