Azure Distributed Data Engineering Toolkit
==========================================
Azure Distributed Data Engineering Toolkit (AZTK) is a python CLI application for provisioning on-demand Spark on Docker clusters in Azure. It's a cheap and easy way to get up and running with a Spark cluster, and a great tool for Spark users who want to experiment and start testing at scale.

This toolkit is built on top of Azure Batch but does not require any Azure Batch knowledge to use.

.. _user-docs:

.. toctree::
   :maxdepth: 2
   :caption: User documentation:

   00-getting-started
   10-clusters
   12-docker-image
   13-configuration
   14-azure-files
   15-plugins
   20-spark-submit
   30-cloud-storage
   60-gpu
   70-jobs
   80-migration

.. _sdk-docs:
.. toctree::
   :maxdepth: 2
   :caption: SDK documentation:

   sdk-examples
   51-define-plugin
   aztk


.. _dev-docs:

.. toctree::
   :maxdepth: 2
   :caption: Developer documentation:

   dev/docs
   dev/writing-models
   dev/tests



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
