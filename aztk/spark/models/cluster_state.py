from enum import Enum

class ClusterState(Enum):
    """
    State giving information of the Spark cluster status
    """

    Allocating = "allocating"
    """
    No nodes able to be the master have been allocated yet.
    """

    Booting = "booting"
    """
    At least on node is now starting
    """

    ElectingMaster = "electing_master"
    """
    At least one node is now trying to be the master
    """

    ElectingMasterFailed = "electing_master_failed"
    """
    Goes to this state when all the node able to be the master fail before electing a master
    """

    Setup = "setup"
    """
    When the cluster has elected a master and is now installing software, setting up plugins, etc.
    """

    SetupFailed = "setup"
    """
    When the master node initialization failed
    """

    Ready = "ready"
    """
    Master is ready. This cluster can start running spark jobs
    """
