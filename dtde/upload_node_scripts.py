import os
import logging
import zipfile
from . import util

root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

local_tmp_zipfile = "tmp/node-scripts.zip"


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
            ziph.write(os.path.join(base, file),
                       os.path.join(relative_folder, file))


def __create_zip():
    ensure_dir(local_tmp_zipfile)
    zipf = zipfile.ZipFile(local_tmp_zipfile, 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(root, "node_scripts"), zipf)
    zipf.close()
    logging.debug("Ziped file")


def __upload():
    logging.debug("Uploading node scripts...")
    return util.upload_file_to_container(
        container_name="spark-node-scripts",
        file_path=local_tmp_zipfile,
        use_full_path=False)


def zip_and_upload():
    __create_zip()
    return __upload()
