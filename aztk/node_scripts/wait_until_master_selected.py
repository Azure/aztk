import time


def main():
    master = None

    while master is None:
        try:
            from core import config
            from install.pick_master import get_master_node_id

            batch_client = config.batch_client
            pool = batch_client.pool.get(config.pool_id)
            master = get_master_node_id(pool)
            time.sleep(1)

        except Exception as e:
            print(e)
            time.sleep(1)


if __name__ == "__main__":
    main()
