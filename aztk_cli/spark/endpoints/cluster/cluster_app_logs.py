import argparse
import os
import typing

import aztk
from aztk_cli import config, utils, log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="cluster_id", required=True, help="The unique id of your spark cluster")
    parser.add_argument("--name", dest="app_name", required=True, help="The unique id of your job name")

    output_group = parser.add_mutually_exclusive_group()

    output_group.add_argument(
        "--output",
        help="Path to the file you wish to output to. If not \
                                    specified, output is printed to stdout",
    )
    output_group.add_argument("--tail", dest="tail", action="store_true")


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())

    if args.tail:
        utils.stream_logs(client=spark_client, cluster_id=args.cluster_id, application_name=args.app_name)
    else:
        app_log = spark_client.cluster.get_application_log(id=args.cluster_id, application_name=args.app_name)
        if args.output:
            with utils.Spinner():
                with open(os.path.abspath(os.path.expanduser(args.output)), "w", encoding="UTF-8") as f:
                    f.write(app_log.log)
        else:
            log.print(app_log.log)
