import argparse
import typing
from . import delete
from . import get_app_logs
from . import get_app
from . import get
from . import list
from . import list_apps
from . import stop_app
from . import stop
from . import submit


class ClusterAction:
    get_app_logs = "get-app-logs"
    get_app = "get-app"
    delete = "delete"
    get = "get"
    list = "list"
    list_apps = "list-apps"
    stop_app = "stop-app"
    stop = "stop"
    submit = "submit"


def setup_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(title="Actions", dest="job_action", metavar="<action>")
    subparsers.required = True

    get_app_logs_parser = subparsers.add_parser(ClusterAction.get_app_logs, help="Get a Job's application logs")
    get_app_parser = subparsers.add_parser(ClusterAction.get_app, help="Get information about a Job's application")
    delete_parser = subparsers.add_parser(ClusterAction.delete, help="Delete a Job")
    get_parser = subparsers.add_parser(ClusterAction.get, help="Get information about a Job")
    list_parser = subparsers.add_parser(ClusterAction.list, help="List Jobs in your account")
    list_apps_parser = subparsers.add_parser(ClusterAction.list_apps, help="List all applications on an AZTK Job")
    stop_app_parser = subparsers.add_parser(ClusterAction.stop_app, help="Stop a Job's application")
    stop_parser = subparsers.add_parser(ClusterAction.stop, help="Stop a Job from running")
    submit_parser = subparsers.add_parser(ClusterAction.submit, help="Submit a new spark Job")

    get_app_logs.setup_parser(get_app_logs_parser)
    get_app.setup_parser(get_app_parser)
    delete.setup_parser(delete_parser)
    get.setup_parser(get_parser)
    list.setup_parser(list_parser)
    list_apps.setup_parser(list_apps_parser)
    stop_app.setup_parser(stop_app_parser)
    stop.setup_parser(stop_parser)
    submit.setup_parser(submit_parser)


def execute(args: typing.NamedTuple):
    actions = {}

    actions[ClusterAction.get_app_logs] = get_app_logs.execute
    actions[ClusterAction.get_app] = get_app.execute
    actions[ClusterAction.delete] = delete.execute
    actions[ClusterAction.get] = get.execute
    actions[ClusterAction.list] = list.execute
    actions[ClusterAction.list_apps] = list_apps.execute
    actions[ClusterAction.stop_app] = stop_app.execute
    actions[ClusterAction.stop] = stop.execute
    actions[ClusterAction.submit] = submit.execute

    func = actions[args.job_action]
    func(args)
