import os
from setuptools import setup, find_packages
from aztk_cli import constants
from aztk import version

data_files = []


def find_package_files(root, directory, dest=""):
    paths = []
    for (path, _, filenames) in os.walk(os.path.join(root, directory)):
        for filename in filenames:
            paths.append(os.path.relpath(os.path.join(dest, path, filename), root))
    return paths


with open('README.md') as fd:
    long_description = fd.read()

setup(
    name='aztk',
    version=version.__version__,
    description='On-demand, Dockerized, Spark Jobs on Azure (powered by Azure Batch)',
    long_description=long_description,
    url='https://github.com/Azure/aztk',
    author='Microsoft',
    author_email='askaztk@microsoft.com',
    license='MIT',
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "azure-batch==3.0.0",
        "azure-mgmt-batch==5.0.0",
        "azure-mgmt-storage==1.5.0",
        "azure-storage-blob==1.1.0",
        "pyyaml>=3.12",
        "pycryptodome>=3.4",
        "paramiko>=2.4",
    ],
    package_data={
        'aztk': find_package_files("", "node_scripts", ".."),
        'aztk_cli': find_package_files("aztk_cli", "config"),
    },
    scripts=[],
    entry_points=dict(console_scripts=["{0} = aztk_cli.entrypoint:main".format(constants.CLI_EXE)]),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={
        'Documentation': 'https://github.com/Azure/aztk/wiki/',
        'Source': 'https://github.com/Azure/aztk/',
        'Tracker': 'https://github.com/Azure/aztk/issues',
    },
    python_requires='>=3.5',
)
