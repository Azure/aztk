import concurrent.futures


# TODO: remove nodes param
def create_user_on_cluster(base_operations, id, nodes, username, ssh_pub_key=None, password=None):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(base_operations.create_user_on_node, id, node.id, username, ssh_pub_key, password): node
            for node in nodes
        }
        concurrent.futures.wait(futures)
