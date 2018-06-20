# Migration Guide


## 0.6.0 to 0.7.0
This guide will describe the steps needed to update a 0.6.0 aztk installation to 0.7.0.

## Installation from pip
[AZTK is now published on pip!](https://pypi.org/project/aztk/) If you installed from github previously, please reinstall.

To uninstall run:
```
pip3 uninstall aztk
```

The following command will get the latest release of aztk (please ensure you are using python3.5+):
```
pip3 install aztk
```
Or, you can install 0.7.0 specifically using:
```
pip3 install aztk==0.7.0
```

## Configuration Files
A number of changes have been made that affect previously init'ed aztk environments. To limit potential issues with previous versions, we recommend that you replace any existing `.aztk` directories.

1. Backup your existing `.aztk` directory by renaming it to `.aztk.old`.
2. Run `aztk spark init` to create a new `.aztk` directory
3. Copy the **values** from `.aztk.old/secrets.yaml` to `.aztk/secrets.yaml`
4. Update the new `.aztk/cluster.yaml` with values from `.aztk.old/cluster.yaml` if applicable. Please be aware of the new `toolkit` section that replaces `docker_repo` for supported images. Similarly for `.aztk/job.yaml`.
5. Update the new defaults in `.aztk/spark-defaults.conf`, `.aztk/core-site.xml` and `.aztk/spark-env.sh` if applicable.
6. Be sure to **not** copy over the `.aztk.old/jars` directory. All jars that were placed here by default have been moved on the Docker image. You can add any custom jars you had by placing them in `.aztk/jars/`.
7. Create your new 0.7.0 cluster!

### cluster.yaml
In cluster.yaml, the `toolkit` key has been added. It is used to select the default, supported Docker images. Please refer to [the configuration file documentation.](13-configuration.html#cluster-yaml)

## Docker images
A major backwards-incompatible refactor of the Docker images has occurred. Previous Docker images will no longer work with 0.7.0. To update to a new supported docker image, you will need to update your `.aztk/cluster.yaml` configuration file with the `toolkit` block in place of `docker_repo`. If you do not do so, cluster creation will fail!

Please refer to the [the configuration file documentation](13-configuration.html#cluster-yaml) for more information on the `toolkit` in `cluster.yaml`.


## Custom scripts depreciation and Plugins
Custom scripts have been depreciated in favor of Plugins. Plugins have a number of advantages, including the ability to execute on the host (and not in the Spark Docker container). A number of supported plugins are shipped with aztk, please refer to [the plugin documentation to learn more.](15-plugins.html)

## Read the Docs
[Documentation has migrated to readthedocs](https://aztk.readthedocs.io/en/latest).