import argparse
import typing

import aztk.spark
from aztk_cli import config
from aztk_cli.config import JobConfig


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--id",
        dest="job_id",
        required=False,
        help="The unique id of your Spark Job. Defaults to the id value in .aztk/job.yaml",
    )
    parser.add_argument(
        "--configuration",
        "-c",
        dest="job_conf",
        required=False,
        help="Path to the job.yaml configuration file. Defaults to .aztk/job.yaml",
    )


def execute(args: typing.NamedTuple):
    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    job_conf = JobConfig()

    job_conf.merge(args.job_id, args.job_conf)

    # by default, load spark configuration files in .aztk/
    spark_configuration = config.load_aztk_spark_config()
    # overwrite with values in job_conf if they exist
    if job_conf.spark_defaults_conf:
        spark_configuration.spark_defaults_conf = job_conf.spark_defaults_conf
    if job_conf.spark_env_sh:
        spark_configuration.spark_env_sh = job_conf.spark_env_sh
    if job_conf.core_site_xml:
        spark_configuration.core_site_xml = job_conf.core_site_xml

    job_configuration = aztk.spark.models.JobConfiguration(
        id=job_conf.id,
        applications=job_conf.applications,
        spark_configuration=spark_configuration,
        vm_size=job_conf.vm_size,
        toolkit=job_conf.toolkit,
        max_dedicated_nodes=job_conf.max_dedicated_nodes,
        max_low_pri_nodes=job_conf.max_low_pri_nodes,
        subnet_id=job_conf.subnet_id,
        worker_on_master=job_conf.worker_on_master,
    # scheduling_target=job_conf.scheduling_target,
    )

    # TODO: utils.print_job_conf(job_configuration)
    spark_client.job.submit(job_configuration)
