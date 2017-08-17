import sys
from install import install

def run():
    if len(sys.argv) < 2:
        print("Error: Expected at least one argument")
        exit(1)

    action = sys.argv[1]

    if action == "install":
        install.setup_node()
    else:
        print("Action not supported")


if __name__ == "__main__":
    run()
