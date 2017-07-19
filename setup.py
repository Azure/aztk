from setuptools import setup
from dtde import constants

setup(name='dtde',
      version='0.1',
      description='Utility for data engineers or platform developers to Run distributed jobs in Azure',
      url='<tbd>',
      author='Microsoft',
      author_email='jiata@microsoft.com',
      license='MIT',
      packages=['dtde'],
      scripts=[
      #     'bin/azb',
      ],
      entry_points=dict(
            console_scripts=[
                  "{0} = dtde.cli:main".format(constants.CLI_EXE)
            ]
      ),
      zip_safe=False)
