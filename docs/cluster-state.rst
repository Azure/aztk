Cluster state
=============

.. graphviz::

    digraph foo {
        graph [ordering="out"];
        rankdir=LR;

        subgraph Pipeline {
            rank=same;
            "Ready" -> "Booting"[label="Rebooting",color=orange]
            "Allocating" -> "Booting" -> "ElectingMaster" -> "Setup" -> "Ready"[color=green];
        }

        "ElectingMaster" -> "ElectingMasterFailed"[color=red]

        "Setup" -> "SetupFailed"[color=red]


    }
