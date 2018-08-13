import sys
from install import install
from core import logger


def run():
    if len(sys.argv) < 2:
        print("Error: Expected at least one argument")
        exit(1)

    action = sys.argv[1]

    if action == "setup-node":
        install.setup_host(sys.argv[2], sys.argv[3])
    elif action == "setup-spark-container":
        install.setup_spark_container()
    else:
        print("Action not supported")


if __name__ == "__main__":
    logger.setup_logging()
    run()
