import argparse
import os
import sys
import typing

import aztk.spark
from aztk_cli import config, log, utils


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument("--id", dest="cluster_id", required=True, help="The unique id of your spark cluster")

    parser.add_argument("--name", required=True, help="a name for your application")

    parser.add_argument("--wait", dest="wait", action="store_true", help="Wait for app to complete")
    parser.add_argument("--no-wait", dest="wait", action="store_false", help="Do not wait for app to complete")
    parser.set_defaults(wait=True)

    parser.add_argument("--class", dest="main_class", help="Your application's main class (for Java only).")

    parser.add_argument(
        "--jars",
        help="Comma-separated list of local jars to include \
                              on the driver and executor classpaths. Use \
                              absolute path to reference files.",
    )

    parser.add_argument(
        "--py-files",
        help="Comma-separated list of .zip, .egg, or .py files \
                              to place on the PYTHONPATH for Python apps. Use \
                              absolute path to reference files.",
    )

    parser.add_argument(
        "--files",
        help="Comma-separated list of .zip, .egg, or .py files \
                              to place on the PYTHONPATH for Python apps. Use \
                              absolute path ot reference files.",
    )

    parser.add_argument("--driver-java-options", help="Extra Java options to pass to the driver.")

    parser.add_argument("--driver-library-path", help="Extra library path entries to pass to the driver.")

    parser.add_argument(
        "--driver-class-path",
        help="Extra class path entries to pass to the driver. \
                              Note that jars added with --jars are automatically \
                              included in the classpath.",
    )

    parser.add_argument("--driver-memory", help="Memory for driver (e.g. 1000M, 2G) (Default: 1024M).")

    parser.add_argument("--executor-memory", help="Memory per executor (e.g. 1000M, 2G) (Default: 1G).")

    parser.add_argument("--driver-cores", help="Cores for driver (Default: 1).")

    parser.add_argument(
        "--executor-cores",
        help="Number of cores per executor. (Default: All \
                              available cores on the worker)",
    )

    parser.add_argument(
        "--max-retry-count",
        help="Number of times the Spark job may be retried \
                              if there is a failure",
    )

    parser.add_argument(
        "--output",
        help="Path to the file you wish to output to. If not \
                              specified, output is printed to stdout",
    )

    parser.add_argument(
        "--remote",
        action="store_true",
        help="Do not upload the app to the cluster, assume it is \
                              already accessible at the given path",
    )

    parser.add_argument(
        "app",
        help="App jar OR python file to execute. A path to a local "
        "file is expected, unless used in conjunction with "
        "the --remote flag. When the --remote flag is set, a "
        "remote path that is accessible from the cluster is "
        "expected. Remote paths are not validated up-front.",
    )

    parser.add_argument("app_args", nargs="*", help="Arguments for the application")


def execute(args: typing.NamedTuple):
    if not args.wait and args.output:
        raise aztk.error.AztkError("--output flag requires --wait flag")

    spark_client = aztk.spark.Client(config.load_aztk_secrets())
    jars = []
    py_files = []
    files = []

    if args.jars is not None:
        jars = args.jars.replace(" ", "").split(",")

    if args.py_files is not None:
        py_files = args.py_files.replace(" ", "").split(",")

    if args.files is not None:
        files = args.files.replace(" ", "").split(",")

    log_application(args, jars, py_files, files)

    spark_client.cluster.submit(
        id=args.cluster_id,
        application=aztk.spark.models.ApplicationConfiguration(
            name=args.name,
            application=args.app,
            application_args=args.app_args,
            main_class=args.main_class,
            jars=jars,
            py_files=py_files,
            files=files,
            driver_java_options=args.driver_java_options,
            driver_library_path=args.driver_library_path,
            driver_class_path=args.driver_class_path,
            driver_memory=args.driver_memory,
            executor_memory=args.executor_memory,
            driver_cores=args.driver_cores,
            executor_cores=args.executor_cores,
            max_retry_count=args.max_retry_count,
        ),
        remote=args.remote,
        wait=False,
    )

    if args.wait:
        if not args.output:
            exit_code = utils.stream_logs(client=spark_client, cluster_id=args.cluster_id, application_name=args.name)
        else:
            with utils.Spinner():
                spark_client.cluster.wait(
                    id=args.cluster_id, application_name=args.name)    # TODO: replace wait_until_application_done
                application_log = spark_client.cluster.get_application_log(
                    id=args.cluster_id, application_name=args.name)
                with open(os.path.abspath(os.path.expanduser(args.output)), "w", encoding="UTF-8") as f:
                    f.write(application_log.log)
                exit_code = application_log.exit_code

        sys.exit(exit_code)


def log_application(args, jars, py_files, files):
    log.info("-------------------------------------------")
    log.info("Spark cluster id:        %s", args.cluster_id)
    log.info("Spark app name:          %s", args.name)
    log.info("Wait for app completion: %s", args.wait)
    if args.main_class is not None:
        log.info("Entry point class:       %s", args.main_class)
    if jars:
        log.info("JARS:                    %s", jars)
    if py_files:
        log.info("PY_Files:                %s", py_files)
    if files:
        log.info("Files:                   %s", files)
    if args.driver_java_options is not None:
        log.info("Driver java options:     %s", args.driver_java_options)
    if args.driver_library_path is not None:
        log.info("Driver library path:     %s", args.driver_library_path)
    if args.driver_class_path is not None:
        log.info("Driver class path:       %s", args.driver_class_path)
    if args.driver_memory is not None:
        log.info("Driver memory:           %s", args.driver_memory)
    if args.executor_memory is not None:
        log.info("Executor memory:         %s", args.executor_memory)
    if args.driver_cores is not None:
        log.info("Driver cores:            %s", args.driver_cores)
    if args.executor_cores is not None:
        log.info("Executor cores:          %s", args.executor_cores)
    log.info("Application:             %s", args.app)
    log.info("Application arguments:   %s", args.app_args)
    log.info("-------------------------------------------")
