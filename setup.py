from setuptools import setup

setup(name='redbull',
      version='0.1',
      description='Utility for data engineers or platform developers to Run spark jobs in Azure',
      url='<tbd>',
      author='Microsoft',
      author_email='jiata@microsoft.com',
      license='MIT',
      packages=['redbull'],
      scripts=['bin/az_spark_start',
               'bin/az_spark_submit',
               'bin/az_spark_stop'],
      zip_safe=False)
