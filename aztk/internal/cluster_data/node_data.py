import fnmatch
import io
import os
import zipfile
from pathlib import Path
from typing import List

import yaml

from aztk import models
from aztk.error import InvalidCustomScriptError
from aztk.utils import constants, file_utils, secure_utils

ROOT_PATH = constants.ROOT_PATH

# Constants for node data
NODE_SCRIPT_FOLDER = "aztk"
PLUGIN_FOLDER = "plugins"


class NodeData:
    """
    Class made to bundle data to be uploaded to the node as a zip
    """

    def __init__(self, cluster_config: models.ClusterConfiguration):
        self.zip_path = io.BytesIO()
        self.cluster_config = cluster_config
        self.zipf = zipfile.ZipFile(self.zip_path, "w", zipfile.ZIP_DEFLATED)

    def add_core(self):
        self._add_node_scripts()
        self._add_plugins()
        self._add_spark_configuration()
        self._add_user_conf()
        return self

    def done(self):
        self.zipf.close()
        return self

    def add_file(self, file: str, zip_dir: str, binary: bool = True):
        if not file:
            return
        if isinstance(file, (str, bytes)):
            full_file_path = Path(file)
            with io.open(file, "r", encoding="UTF-8") as f:
                if binary:
                    self.zipf.write(file, os.path.join(zip_dir, full_file_path.name))
                else:
                    self.zipf.writestr(os.path.join(zip_dir, full_file_path.name), f.read().replace("\r\n", "\n"))
        elif isinstance(file, models.File):
            self.zipf.writestr(os.path.join(zip_dir, file.name), file.payload.getvalue())

    def add_files(self, file_paths: List[str], zip_dir, binary: bool = True):
        """
        Add a list of local files to the node data
        """
        for file in file_paths:
            self.add_file(file, zip_dir, binary)

    def add_dir(self, path: str, dest: str = None, exclude: List[str] = None):
        """
            Zip all the files in the given directory into the zip file handler
        """
        exclude = exclude or []

        for base, _, files in os.walk(path):
            relative_folder = os.path.relpath(base, path)
            for file in files:
                if self._includeFile(file, exclude):
                    self.add_file(os.path.join(base, file), os.path.join(dest, relative_folder), binary=False)

    def _add_spark_configuration(self):
        spark_configuration = self.cluster_config.spark_configuration
        if not spark_configuration:
            return
        self.add_files(
            [
                spark_configuration.spark_defaults_conf,
                spark_configuration.spark_env_sh,
                spark_configuration.core_site_xml,
            ],
            "conf",
            binary=False,
        )

        # add ssh keys for passwordless ssh
        self.zipf.writestr("id_rsa.pub", spark_configuration.ssh_key_pair["pub_key"])
        self.zipf.writestr("id_rsa", spark_configuration.ssh_key_pair["priv_key"])

        if spark_configuration.jars:
            for jar in spark_configuration.jars:
                self.add_file(jar, "jars", binary=True)

    def _add_user_conf(self):
        user_conf = self.cluster_config.user_configuration
        if not user_conf:
            return
        encrypted_aes_session_key, cipher_aes_nonce, tag, ciphertext = secure_utils.encrypt_password(
            self.cluster_config.spark_configuration.ssh_key_pair["pub_key"], user_conf.password)
        user_conf = yaml.dump({
            "username": user_conf.username,
            "password": ciphertext,
            "ssh-key": user_conf.ssh_key,
            "aes_session_key": encrypted_aes_session_key,
            "cipher_aes_nonce": cipher_aes_nonce,
            "tag": tag,
            "cluster_id": self.cluster_config.cluster_id,
        })
        self.zipf.writestr("user.yaml", user_conf)

    def _add_plugins(self):
        if not self.cluster_config.plugins:
            return

        data = []
        for plugin in self.cluster_config.plugins:
            for file in plugin.files:
                self.zipf.writestr("plugins/{0}/{1}".format(plugin.name, file.target), file.content())
            if plugin.execute:
                data.append(
                    dict(
                        name=plugin.name,
                        execute="{0}/{1}".format(plugin.name, plugin.execute),
                        args=plugin.args,
                        env=plugin.env,
                        target=plugin.target.value,
                        target_role=plugin.target_role.value,
                    ))

        self.zipf.writestr(os.path.join("plugins", "plugins-manifest.yaml"), yaml.dump(data))

    def _add_node_scripts(self):
        self.add_dir(os.path.join(ROOT_PATH, NODE_SCRIPT_FOLDER), NODE_SCRIPT_FOLDER, exclude=["*.pyc*", "*.png"])

    def _includeFile(self, filename: str, exclude: List[str]) -> bool:
        exclude = exclude or []
        for pattern in exclude:
            if fnmatch.fnmatch(filename, pattern):
                return False

        return True
