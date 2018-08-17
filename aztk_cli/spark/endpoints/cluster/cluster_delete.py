import argparse
import typing

import aztk
from aztk_cli import config, log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--id", dest="cluster_ids", nargs="*", required=True, help="The unique id of your spark cluster")
    parser.add_argument(
        "--force",
        "-f",
        dest="force",
        required=False,
        action="store_true",
        help="Do not prompt for confirmation, force deletion of cluster.",
    )
    parser.add_argument(
        "--keep-logs",
        "-k",
        dest="keep_logs",
        action="store_true",
        required=False,
        help="Prevent logs in storage from being deleted.",
    )
    parser.set_defaults(force=False, keep_logs=False)


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    cluster_ids = args.cluster_ids

    for cluster_id in cluster_ids:
        if not args.force:
            if not args.keep_logs:
                log.warning("All logs persisted for this cluster will be deleted.")

            confirmation_cluster_id = input(
                "Please confirm the id of the cluster you wish to delete [{}]: ".format(cluster_id))

            if confirmation_cluster_id != cluster_id:
                log.error("Confirmation cluster id does not match. Please try again.")
                return

        if spark_client.cluster.delete(id=cluster_id, keep_logs=args.keep_logs):
            log.info("Deleting cluster %s", cluster_id)
        else:
            log.error("Cluster with id '%s' doesn't exist or was already deleted.", cluster_id)
