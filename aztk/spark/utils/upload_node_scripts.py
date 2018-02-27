import fnmatch
import io
import os
import datetime
import logging
import zipfile
import yaml
import json
from pathlib import Path
from aztk.utils import constants
from aztk.utils import helpers
from aztk.error import InvalidCustomScriptError
import aztk.spark.models
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from aztk.spark.models import ClusterConfiguration, PluginConfiguration
from typing import List

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


def zip_file_to_dir(file, directory: str, zipf: str, binary: bool = False):
    """
        Zip the given file into the given a directory of the zip file
    """
    if not zipf:
        zipf = zipfile.ZipFile(local_tmp_zipfile, "w", zipfile.ZIP_DEFLATED)
    if isinstance(file, (str, bytes)):
        full_file_path = Path(file)

        with io.open(file, 'r') as f:
            if binary:
                zipf.write(file, os.path.join(directory, full_file_path.name))
            else:
                zipf.writestr(os.path.join(directory, full_file_path.name), f.read().replace('\r\n', '\n'))
    elif isinstance(file, aztk.spark.models.File):
        zipf.writestr(os.path.join(directory, file.name), file.payload.getvalue())

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
        if isinstance(custom_script.script, (str, bytes)):
            new_file_name = str(index) + '_' + os.path.basename(custom_script.script)
            try:
                with io.open(custom_script.script, 'r') as f:
                    zipf.writestr(os.path.join('custom-scripts', new_file_name), f.read().replace('\r\n', '\n'))
            except FileNotFoundError:
                raise InvalidCustomScriptError("Custom script '{0}' doesn't exists.".format(custom_script.script))
        elif isinstance(custom_script.script, aztk.spark.models.File):
            new_file_name = str(index) + '_' + custom_script.script.name
            zipf.writestr(os.path.join('custom-scripts', new_file_name), custom_script.script.payload.getvalue())
        data.append(dict(script=new_file_name, runOn=str(custom_script.run_on)))


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


def zip_scripts(blob_client, container_id, custom_scripts, spark_configuration, user_conf=None, plugins=None):
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

    if plugins:
        zipf = __add_plugins(zipf, plugins)

    if user_conf:
        encrypted_aes_session_key, cipher_aes_nonce, tag, ciphertext = encrypt_password(spark_configuration.ssh_key_pair['pub_key'], user_conf.password)
        user_conf = yaml.dump({'username': user_conf.username,
                               'password': ciphertext,
                               'ssh-key': user_conf.ssh_key,
                               'aes_session_key': encrypted_aes_session_key,
                               'cipher_aes_nonce': cipher_aes_nonce,
                               'tag': tag,
                               'cluster_id': container_id})
        zipf = __add_str_to_zip(zipf, user_conf, 'user.yaml')

    # add helper file to node_scripts/submit/
    zip_file_to_dir(file=os.path.join(constants.ROOT_PATH, 'aztk', 'utils', 'command_builder.py'), directory='', zipf=zipf, binary=False)

    zipf.close()

    return __upload(blob_client, container_id)


def encrypt_password(ssh_pub_key, password):
    if not password:
        return [None, None, None, None]
    recipient_key = RSA.import_key(ssh_pub_key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    encrypted_aes_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(password.encode())
    return [encrypted_aes_session_key, cipher_aes.nonce, tag, ciphertext]

def __add_plugins(zipf, plugins: List[PluginConfiguration]):
    data = []
    for plugin in plugins:
        for file in plugin.files:
            zipf = __add_str_to_zip(zipf, file.content(), 'plugins/{0}/{1}'.format(plugin.name, file.target))
        if plugin.execute:
            data.append(dict(
                name=plugin.name,
                execute='{0}/{1}'.format(plugin.name, plugin.execute),
                args=plugin.args,
                env=plugin.env,
                runOn=plugin.run_on.value,
            ))

    zipf.writestr(os.path.join('plugins', 'plugins-manifest.yaml'), yaml.dump(data))
    return zipf
