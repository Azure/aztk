def delete_user(self, pool_id: str, node_id: str, username: str) -> str:
    """
        Create a pool user
        :param pool: the pool to add the user to
        :param node: the node to add the user to
        :param username: username of the user to add
    """
    # Delete a user on the given node
    self.batch_client.compute_node.delete_user(pool_id, node_id, username)
