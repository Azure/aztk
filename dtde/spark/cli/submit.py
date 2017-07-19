import argparse
import typing
from dtde import joblib


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest='cluster_id', required=True,
                        help='The unique id of your spark cluster')

    parser.add_argument('--name', required=True,
                        help='a name for your application')

    parser.add_argument('--wait', dest='wait', action='store_true',
                        help='Wait for app to complete')
    parser.add_argument('--no-wait', dest='wait', action='store_false',
                        help='Do not wait for app to complete')
    parser.set_defaults(wait=True)

    parser.add_argument('--class', dest='main_class',
                        help='Your application\'s main class (for Java only).')

    parser.add_argument('--jars',
                        help='Comma-separated list of local jars to include \
                              on the driver and executor classpaths. Use \
                              absolute path to reference files.')

    parser.add_argument('--py-files',
                        help='Comma-separated list of .zip, .egg, or .py files \
                              to place on the PYTHONPATH for Python apps. Use \
                              absolute path to reference files.')

    parser.add_argument('--files',
                        help='Comma-separated list of .zip, .egg, or .py files \
                              to place on the PYTHONPATH for Python apps. Use \
                              absolute path ot reference files.')

    parser.add_argument('--driver-java-options',
                        help='Extra Java options to pass to the driver.')

    parser.add_argument('--driver-library-path',
                        help='Extra library path entries to pass to the driver.')

    parser.add_argument('--driver-class-path',
                        help='Extra class path entries to pass to the driver. \
                              Note that jars added with --jars are automatically \
                              included in the classpath.')

    parser.add_argument('--driver-memory',
                        help="Memory for driver (e.g. 1000M, 2G) (Default: 1024M).")

    parser.add_argument('--executor-memory',
                        help='Memory per executor (e.g. 1000M, 2G) (Default: 1G).')

    parser.add_argument('--driver-cores',
                        help='Cores for driver (Default: 1).')

    parser.add_argument('--executor-cores',
                        help='Number of cores per executor. (Default: All \
                              available cores on the worker')

    parser.add_argument('app',
                        help='App jar OR python file to execute. Use absolute \
                              path to reference file.')

    parser.add_argument('app_args', nargs='*',
                        help='Arguments for the application')


def execute(args: typing.NamedTuple):
    jars = []
    py_files = []
    files = []

    if args.jars is not None:
        jars = args.jars.replace(' ', '').split(',')

    if args.py_files is not None:
        py_files = args.py_files.replace(' ', '').split(',')

    if args.files is not None:
        files = args.py_files.replace(' ', '').split(',')

    print('-------------------------------------------')
    print('Spark cluster id:        {}'.format(args.cluster_id))
    print('Spark app name:          {}'.format(args.name))
    print('Wait for app completion: {}'.format(args.wait))
    if args.main_class is not None:
        print('Entry point class:       {}'.format(args.main_class))
    if jars:
        print('JARS:                    {}'.format(jars))
    if py_files:
        print('PY_Files:                {}'.format(py_files))
    if files:
        print('Files:                   {}'.format(files))
    if args.driver_java_options is not None:
        print('Driver java options:     {}'.format(args.driver_java_options))
    if args.driver_library_path is not None:
        print('Driver library path:     {}'.format(args.driver_library_path))
    if args.driver_class_path is not None:
        print('Driver class path:       {}'.format(args.driver_class_path))
    if args.driver_memory is not None:
        print('Driver memory:           {}'.format(args.driver_memory))
    if args.executor_memory is not None:
        print('Executor memory:         {}'.format(args.executor_memory))
    if args.driver_cores is not None:
        print('Driver cores:            {}'.format(args.driver_cores))
    if args.executor_cores is not None:
        print('Executor cores:          {}'.format(args.executor_cores))
    print('Application:             {}'.format(args.app))
    print('Application arguments:   {}'.format(args.app_args))
    print('-------------------------------------------')

    joblib.submit_app(
        cluster_id=args.cluster_id,
        name=args.name,
        app=args.app,
        app_args=args.app_args,
        wait=args.wait,
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
        executor_cores=args.executor_cores)
