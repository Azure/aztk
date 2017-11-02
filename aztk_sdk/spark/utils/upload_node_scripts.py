import fnmatch
import io
import os
import logging
import zipfile
import yaml
from pathlib import Path
from aztk_sdk.utils import constants
from aztk_sdk.utils import helpers

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


def __upload(blob_client):
    logging.debug("Uploading node scripts...")
    return helpers.upload_file_to_container(
        container_name="spark-node-scripts",
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
        return
    zipf = zip_file_to_dir(file_path, zip_file_path, zipf, binary)
    return zipf


def zip_scripts(blob_client, custom_scripts, spark_conf):
    zipf = __create_zip()
    if custom_scripts:
        zipf = __add_custom_scripts(zipf, custom_scripts)

    if spark_conf:
        zipf = __add_file_to_zip(zipf, spark_conf.spark_defaults_conf, 'conf', binary=False)
        zipf = __add_file_to_zip(zipf, spark_conf.spark_env_sh, 'conf', binary=False)
        zipf = __add_file_to_zip(zipf, spark_conf.core_site_xml, 'conf', binary=False)
        if spark_conf.jars:
            for jar in spark_conf.jars:
                zipf = __add_file_to_zip(zipf, jar, 'jars', binary=True)

    zipf.close()
    return __upload(blob_client)
