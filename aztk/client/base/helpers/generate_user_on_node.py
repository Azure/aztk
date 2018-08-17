from Cryptodome.PublicKey import RSA

from aztk.utils import secure_utils


def generate_user_on_node(base_client, pool_id, node_id):
    generated_username = secure_utils.generate_random_string()
    ssh_key = RSA.generate(2048)
    ssh_pub_key = ssh_key.publickey().exportKey("OpenSSH").decode("utf-8")
    base_client.create_user_on_node(pool_id, node_id, generated_username, ssh_pub_key)
    return generated_username, ssh_key
