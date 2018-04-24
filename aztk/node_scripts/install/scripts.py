import os
import subprocess
import yaml
from pathlib import Path


def _read_yaml_file(path=None):
    custom_scripts = None
    if not os.path.isfile(path):
        print("Configuration file doesn't exist at {0}".format(path))
    else:
        with open(path, 'r', encoding='UTF-8') as stream:
            try:
                custom_scripts = yaml.load(stream)
            except yaml.YAMLError as err:
                print("Error in cluster.yaml: {0}".format(err))

    return custom_scripts


def _run_on_this_node(script_obj=None, is_master=False, is_worker=False):
    if script_obj['runOn'] == 'master' and is_master is True:
        return True
    if script_obj['runOn'] == 'worker' and is_worker is True:
        return True
    if script_obj['runOn'] == 'all-nodes':
        return True

    return False


def _run_script_or_scripts_dir(scripts=None, is_master=False, is_worker=False, custom_scripts_dir=None):
    for script_obj in scripts:
        if _run_on_this_node(script_obj, is_master, is_worker):
            path = Path(os.path.join(custom_scripts_dir, script_obj['script']))
            if path.is_dir():
                _run_scripts_dir(str(path))
            else:
                _run_script(str(path))


def _run_script(script_path: str = None):
    if not os.path.isfile(script_path):
        print("Cannot run script: {0} file does not exist".format(script_path))
        return
    file_stat = os.stat(script_path)
    os.chmod(script_path, file_stat.st_mode | 0o777)
    print("Running custom script:", script_path)
    try:
        subprocess.call([script_path], shell = True)
    except Exception as e:
        print(e)

def _run_scripts_dir(root: str = None):
    try:
        for path, subdirs, files in os.walk(root):
            for name in files:
                script_path = os.path.join(path, name)
                _run_script(script_path)
    except FileNotFoundError as e:
        print(e)
    except IOError as e:
        print(e)


def run_custom_scripts(is_master: bool = False, is_worker: bool = False):
    custom_scripts_dir = os.path.join(os.environ['AZTK_WORKING_DIR'], 'custom-scripts')

    custom_scripts = _read_yaml_file(os.path.join(custom_scripts_dir, 'custom-scripts.yaml'))

    if custom_scripts is not None:
        _run_script_or_scripts_dir(custom_scripts, is_master, is_worker, custom_scripts_dir)
