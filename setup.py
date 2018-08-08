import fnmatch
import os

from setuptools import find_packages, setup

from aztk import version
from aztk_cli import constants

data_files = []


def _includeFile(filename: str, exclude: [str]) -> bool:
    for pattern in exclude:
        if fnmatch.fnmatch(filename, pattern):
            return False

    return True


def find_package_files(root, directory, dest=""):
    paths = []
    for (path, _, filenames) in os.walk(os.path.join(root, directory)):
        for filename in filenames:
            if _includeFile(filename, exclude=["*.pyc*"]):
                paths.append(os.path.relpath(os.path.join(dest, path, filename), root))
    return paths


with open('README.md', encoding='UTF-8') as fd:
    long_description = fd.read()

setup(
    name='aztk',
    version=version.__version__,
    description='On-demand, Dockerized, Spark Jobs on Azure (powered by Azure Batch)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Azure/aztk',
    author='Microsoft',
    author_email='askaztk@microsoft.com',
    license='MIT',
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "azure-batch~=4.1.3",
        "azure-mgmt-batch~=5.0.0",
        "azure-mgmt-storage~=2.0.0",
        "azure-storage-blob~=1.3.1",
        "pyyaml>=3.12",
        "pycryptodomex>=3.4",
        "paramiko>=2.4",
    ],
    package_data={
        'aztk': find_package_files("aztk", ""),
        'aztk_cli': find_package_files("aztk_cli", ""),
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
