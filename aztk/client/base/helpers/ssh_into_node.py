import aztk.models as models
from aztk.utils import ssh as ssh_lib


def ssh_into_node(base_client,
                  pool_id,
                  node_id,
                  username,
                  ssh_key=None,
                  password=None,
                  port_forward_list=None,
                  internal=False):
    if internal:
        result = base_client.batch_client.compute_node.get(pool_id=pool_id, node_id=node_id)
        rls = models.RemoteLogin(ip_address=result.ip_address, port="22")
    else:
        result = base_client.batch_client.compute_node.get_remote_login_settings(pool_id, node_id)
        rls = models.RemoteLogin(ip_address=result.remote_login_ip_address, port=str(result.remote_login_port))

    ssh_lib.node_ssh(
        username=username,
        hostname=rls.ip_address,
        port=rls.port,
        ssh_key=ssh_key,
        password=password,
        port_forward_list=port_forward_list,
    )
