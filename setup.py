from setuptools import setup

setup(name='redbull',
      version='0.1',
      description='Utility for data engineers or platform developers to Run spark jobs in Azure',
      url='<tbd>',
      author='Microsoft',
      author_email='jiata@microsoft.com',
      license='MIT',
      packages=['redbull'],
      scripts=['bin/spark-cluster-create',
               'bin/spark-cluster-delete',
               'bin/spark-app-submit',
               'bin/spark-app-ssh',
               'bin/spark-app-list',
               'bin/spark-app-jupyter'],
      zip_safe=False)
