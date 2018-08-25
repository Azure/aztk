import argparse
import typing

import aztk.spark
from aztk_cli import config, log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="job_id", required=True, help="The unique id of your AZTK Job")
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
    job_id = args.job_id

    if not args.force:
        # check if job exists before prompting for confirmation
        spark_client.job.get(id=job_id)

        if not args.keep_logs:
            log.warning("All logs persisted for this job will be deleted.")

        confirmation_cluster_id = input("Please confirm the id of the cluster you wish to delete: ")

        if confirmation_cluster_id != job_id:
            log.error("Confirmation cluster id does not match. Please try again.")
            return

    if spark_client.job.delete(id=job_id, keep_logs=args.keep_logs):
        log.info("Deleting Job %s", job_id)
    else:
        log.error("Job with id '%s' doesn't exist or was already deleted.", job_id)
