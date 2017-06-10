from setuptools import setup

setup(name='dtde',
      version='0.1',
      description='Utility for data engineers or platform developers to Run distributed jobs in Azure',
      url='<tbd>',
      author='Microsoft',
      author_email='jiata@microsoft.com',
      license='MIT',
      packages=['dtde'],
      scripts=['bin/spark-cluster-create',
               'bin/spark-cluster-delete',
               'bin/spark-cluster-create-user',
               'bin/spark-cluster-ssh',
               'bin/spark-cluster-get',
               'bin/spark-cluster-list',
               'bin/spark-submit'],
      zip_safe=False)
