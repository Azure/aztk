Cluster state
=============

.. graphviz::

    digraph MasterState {
        graph [fontname="Arial"];
        node [shape=record;fontname="Arial"];
        edge [fontname="Arial"];

        rankdir=LR;

        Ready -> Preempted -> Booting[color=orange]

        Ready -> Booting[label=Rebooting,color=orange]

        ElectingMaster -> ElectingMasterFailed[color=red]

        Setup -> SetupFailed[color=red]

        subgraph Temporary {
            rank=3;
            Preempted;
        }

        subgraph Pipeline {
            rank=same;
            Allocating -> Booting -> ElectingMaster -> Setup -> Ready[color=green];
        }

        subgraph ErrorStates {
            rank=same;
            ElectingMasterFailed[color=darkred];
            SetupFailed[color=darkred];
        }

    }


.. autoclass:: aztk.models.MasterState
    :members:
    :undoc-members:
    :show-inheritance:

