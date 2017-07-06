import os
import zipfile
from . import util, constants

root = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

local_tmp_zipfile = "node-scripts.zip";

def zipdir(path, ziph):
    """
        Zip all the files in the given directory into the zip file handler
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), file)


def zip_node_scripts():
    zipf = zipfile.ZipFile(local_tmp_zipfile, 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(root, "node"), zipf)
    zipf.close()
    print("Ziped file")

def upload(blob_client):
    print("Uploading node scripts...")
    util.upload_file_to_container(
                blob_client, 
                container_name = "node-scripts", 
                file_path = "node-scripts.zip", 
                use_full_path = True)


    print("Uploaded")

if __name__ == '__main__':
    zip_node_scripts()