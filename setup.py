from setuptools import setup, find_packages
from cli import constants
from aztk import version


setup(name='aztk',
      version=version.__version__,
      description='Utility for data engineers or platform developers to Run distributed jobs in Azure',
      url='<tbd>',
      author='Microsoft',
      author_email='jiata@microsoft.com',
      license='MIT',
      packages=find_packages(),
      scripts=[
      #     'bin/aztk',
      ],
      entry_points=dict(
            console_scripts=[
                  "{0} = cli.entrypoint:main".format(constants.CLI_EXE)
            ]
      ),
      zip_safe=False)
