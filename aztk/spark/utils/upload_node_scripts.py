import fnmatch
import io
import os
import datetime
import logging
import zipfile
import yaml
from pathlib import Path
from aztk.utils import constants
from aztk.utils import helpers

root = constants.ROOT_PATH

local_tmp_zipfile = os.path.join(root, "tmp/node-scripts.zip")


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def zipdir(path, ziph):
    """
        Zip all the files in the given directory into the zip file handler
    """
    for base, _, files in os.walk(path):
        relative_folder = os.path.relpath(base, path)
        for file in files:
            if __includeFile(file):
                with io.open(os.path.join(base, file), 'r') as f:
                    ziph.writestr(os.path.join(relative_folder, file), f.read().replace('\r\n', '\n'))


def zip_file_to_dir(file: str, directory: str, zipf: str, binary: bool = False):
    """
        Zip the given file into the given a directory of the zip file
    """
    if not zipf:
        zipf = zipfile.ZipFile(local_tmp_zipfile, "w", zipfile.ZIP_DEFLATED)

    full_file_path = Path(file)
    with io.open(file, 'r') as f:
        if binary:
            zipf.write(file, os.path.join(directory, full_file_path.name))
        else:
            zipf.writestr(os.path.join(directory, full_file_path.name), f.read().replace('\r\n', '\n'))

    return zipf


def __includeFile(filename: str) -> bool:
    if fnmatch.fnmatch(filename, '*.pyc'):
        return False

    return True


def __create_zip():
    ensure_dir(local_tmp_zipfile)
    zipf = zipfile.ZipFile(local_tmp_zipfile, 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(root, "node_scripts"), zipf)

    logging.debug("Ziped node_scripts")
    return zipf


def __upload(blob_client, cluster_id):
    logging.debug("Uploading node scripts...")

    return helpers.upload_file_to_container(
        container_name=cluster_id,
        application_name="aztk-node-scripts",
        file_path=local_tmp_zipfile,
        blob_client=blob_client,
        use_full_path=False)


def __add_custom_scripts(zipf, custom_scripts):
    data = []
    for index, custom_script in enumerate(custom_scripts):
        new_file_name = str(index) + '_' + os.path.basename(custom_script.script)
        data.append(dict(script=new_file_name, runOn=str(custom_script.run_on)))
        with io.open(custom_script.script, 'r') as f:
            zipf.writestr(os.path.join('custom-scripts', new_file_name), f.read().replace('\r\n', '\n'))

    zipf.writestr(os.path.join('custom-scripts', 'custom-scripts.yaml'), yaml.dump(data, default_flow_style=False))

    return zipf


def __add_file_to_zip(zipf, file_path, zip_file_path, binary):
    if not file_path:
        return zipf
    zipf = zip_file_to_dir(file_path, zip_file_path, zipf, binary)
    return zipf

def __add_str_to_zip(zipf, payload, zipf_file_path=None):
    if not payload:
        return zipf
    zipf.writestr(zipf_file_path, payload)
    return zipf

def zip_scripts(blob_client, container_id, custom_scripts, spark_configuration):
    zipf = __create_zip()
    if custom_scripts:
        zipf = __add_custom_scripts(zipf, custom_scripts)

    if spark_configuration:
        zipf = __add_file_to_zip(zipf, spark_configuration.spark_defaults_conf, 'conf', binary=False)
        zipf = __add_file_to_zip(zipf, spark_configuration.spark_env_sh, 'conf', binary=False)
        zipf = __add_file_to_zip(zipf, spark_configuration.core_site_xml, 'conf', binary=False)
        # add ssh keys for passwordless ssh
        zipf = __add_str_to_zip(zipf, spark_configuration.ssh_key_pair['pub_key'], 'id_rsa.pub')
        zipf = __add_str_to_zip(zipf, spark_configuration.ssh_key_pair['priv_key'], 'id_rsa')
        if spark_configuration.jars:
            for jar in spark_configuration.jars:
                zipf = __add_file_to_zip(zipf, jar, 'jars', binary=True)

    # add helper file to node_scripts/submit/
    zip_file_to_dir(file=os.path.join(constants.ROOT_PATH, 'aztk', 'utils', 'command_builder.py'), directory='', zipf=zipf, binary=False)

    zipf.close()
    return __upload(blob_client, container_id)
