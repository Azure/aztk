import os
from aztk.config import SecretsConfig

def get_user_public_key(key_or_path: str = None):
    """
        Return the ssh key.
        It will first check if the given argument is a ssh key or a path to one
        otherwise will check the configuration file.
    """
    if not key_or_path:
       secrets_conf = SecretsConfig()
       secrets_conf.load_secrets_config()

       if not secrets_conf.ssh_pub_key:
           return None

       key_or_path = secrets_conf.ssh_pub_key
    if not key_or_path:
        return None

    key = None
    if os.path.isfile(os.path.expanduser(key_or_path)):
        key = __read_ssh_key_from_file(key_or_path)
    else:
        key = key_or_path

    return key

def get_user_private_key_path():
    """
        Return the path to the ssh private key if given.
        It check the configuration file secrets.yaml.
    """
    secrets_conf = SecretsConfig()
    secrets_conf.load_secrets_config()
    return secrets_conf.ssh_priv_key


def __read_ssh_key_from_file(path: str) -> str:
    """
        Read the content of the given file
    """
    with open(os.path.expanduser(path), 'r') as content_file:
        content = content_file.read()
        return content
