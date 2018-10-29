from enum import Enum


class ClusterState(Enum):
    deleting = "deleting"
    resizing = "resizing"
    steady = "steady"
    stopping_resize = "stopping"
