import sys
from install import pick_master
from core import config


def setup_as_master():
    print("Setting up as master.")


def setup_as_worker():
    print("Setting up as worker.")


def run():

    if len(sys.argv) < 2:
        print("Error: Expected at least one argument")
        exit(1)

    action = sys.argv[1]

    if action == "install":

        client = config.batch_client

        is_master = pick_master.find_master(client)

        if is_master:
            setup_as_master()
        else:
            setup_as_worker()
    else:
        print("Action not supported")


if __name__ == "__main__":
    run()
