import concurrent.futures


# TODO: remove nodes param
def delete_user_on_cluster(base_client, id, nodes, username):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(base_client.delete_user_on_node, id, node.id, username) for node in nodes]
        concurrent.futures.wait(futures)
