import argparse
import typing
from dtde import clusterlib, log


def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('--id', dest="cluster_id", required=True,
                        help='The unique id of your spark cluster')
    parser.add_argument('--masterui',
                        help='Local port to port spark\'s master UI to')
    parser.add_argument('--webui',
                        help='Local port to port spark\'s webui to')
    parser.add_argument('--jupyter',
                        help='Local port to port jupyter to')
    parser.add_argument('-u', '--username',
                        help='Username to spark cluster')
    parser.add_argument('--no-connect', dest="connect",
                        action='store_false',
                        help='Do not create the ssh session. Only print out \
                        the command to run.')

    parser.set_defaults(connect=True)


def execute(args: typing.NamedTuple):
    log.info("-------------------------------------------")
    log.info("spark cluster id:    %s", args.cluster_id)
    log.info("open masterui:       %s", args.masterui)
    log.info("open webui:          %s", args.webui)
    log.info("open jupyter:        %s", args.jupyter)
    log.info("ssh username:        %s", args.username)
    log.info("connect:             %s", args.connect)
    log.info("-------------------------------------------")

    # get ssh command
    ssh_cmd = clusterlib.ssh_in_master(
        cluster_id=args.cluster_id,
        masterui=args.masterui,
        webui=args.webui,
        jupyter=args.jupyter,
        username=args.username,
        connect=args.connect)

    if not args.connect:
        log.info("")
        log.info("Use the following command to connect to your spark head node:")
        log.info("\t%s", ssh_cmd)
