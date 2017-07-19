import argparse
import typing
from dtde import clusterlib, util


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
    print('-------------------------------------------')
    print('spark cluster id:    {}'.format(args.cluster_id))
    print('open masterui:       {}'.format(args.masterui))
    print('open webui:          {}'.format(args.webui))
    print('open jupyter:        {}'.format(args.jupyter))
    print('ssh username:        {}'.format(args.username))
    print('connect:             {}'.format(args.connect))
    print('-------------------------------------------')

    # get ssh command
    clusterlib.ssh(
        cluster_id=args.cluster_id,
        masterui=args.masterui,
        webui=args.webui,
        jupyter=args.jupyter,
        username=args.username,
        connect=args.connect)
