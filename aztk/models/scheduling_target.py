from enum import Enum


class SchedulingTarget(Enum):
    """
    Target where task will get scheduled.
    For spark this is where the driver will live.
    """

    Master = "master"
    """
    Only master is allowed to run task
    """

    Any = "any"
    """
    Any node(Not recommended if using low pri) (Default)
    """
