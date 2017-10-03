import fnmatch
import io
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
            if __includeFile(file):
                with io.open(os.path.join(base, file), 'r') as f:
                    ziph.writestr(os.path.join(relative_folder, file), f.read().replace('\r\n', '\n'))

def __includeFile(filename: str) -> bool:
    if fnmatch.fnmatch(filename, '*.pyc'):
        return False

    return True

def __create_zip():
    ensure_dir(local_tmp_zipfile)
    zipf = zipfile.ZipFile(local_tmp_zipfile, 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(root, "node_scripts"), zipf)

    # zipf.write()
    zipf.close()
    logging.debug("Ziped file")


def __upload(blob_client):
    logging.debug("Uploading node scripts...")
    return util.upload_file_to_container(
        container_name="spark-node-scripts",
        file_path=local_tmp_zipfile,
        blob_client=blob_client,
        use_full_path=False)


def zip_and_upload(blob_client):
    __create_zip()
    return __upload(blob_client)
