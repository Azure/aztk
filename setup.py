from setuptools import setup
from aztk import constants

setup(name='aztk',
      version='0.1',
      description='Utility for data engineers or platform developers to Run distributed jobs in Azure',
      url='<tbd>',
      author='Microsoft',
      author_email='jiata@microsoft.com',
      license='MIT',
      packages=['aztk'],
      scripts=[
      #     'bin/aztk',
      ],
      entry_points=dict(
            console_scripts=[
                  "{0} = aztk.cli:main".format(constants.CLI_EXE)
            ]
      ),
      zip_safe=False)
