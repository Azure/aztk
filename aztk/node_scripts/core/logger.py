import sys
import logging

log = logging.getLogger("aztk.node-agent")

DEFAULT_FORMAT = "%(message)s"


def setup_logging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    log.setLevel(logging.INFO)
    logging.basicConfig(stream=sys.stdout, format=DEFAULT_FORMAT)
