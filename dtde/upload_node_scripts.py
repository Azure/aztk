import os
import zipfile
from . import constants, util

root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

local_tmp_zipfile = "tmp/node-scripts.zip";

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def zipdir(path, ziph):
    """
        Zip all the files in the given directory into the zip file handler
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), file)


def zip():
    ensure_dir(local_tmp_zipfile)
    zipf = zipfile.ZipFile(local_tmp_zipfile, 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(root, "node"), zipf)
    zipf.close()
    print("Ziped file")

def upload():
    print("Uploading node scripts...")
    return util.upload_file_to_container(
                container_name = "spark-node-scripts", 
                file_path = local_tmp_zipfile, 
                use_full_path = False)

def zip_and_upload():
    zip()
    return upload()