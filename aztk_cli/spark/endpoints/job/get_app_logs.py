import argparse
import typing
import aztk.spark
from aztk_cli import utils, config

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id',
                        dest='job_id',
                        required=True,
                        help='The unique id of your AZTK job')
    parser.add_argument('--name',
                        dest='app_name',
                        required=True,
                        help='The unique id of your job name')


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    app_logs = spark_client.get_job_application_log(args.job_id, args.app_name)
    print(app_logs.log)
