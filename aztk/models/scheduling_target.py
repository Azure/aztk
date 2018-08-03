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

    Dedicated = "dedicated"
    """
    Any dedicated node is allowed to run task(Default)
    """

    Any = "any"
    """
    Any node(Not recommended if using low pri)
    """
