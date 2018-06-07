
# Define a custom plugin

## Full example
```py

from aztk.spark.models.plugins import PluginConfiguration, PluginFile,PluginPort, PluginTarget, PluginTargetRole

cluster_config = ClusterConfiguration(
  ...# Other config,
  plugins=[
    PluginConfiguration(
        name="my-custom-plugin",
        files=[
            PluginFile("file.sh", "/my/local/path/to/file.sh"),
            PluginFile("data/one.json", "/my/local/path/to/data/one.json"),
            PluginFile("data/two.json", "/my/local/path/to/data/two.json"),
        ],
        execute="file.sh", # This must be one of the files defined in the file list and match the target path,
        env=dict(
            SOME_ENV_VAR="foo"
        ),
        args=["arg1"], # Those arguments are passed to your execute script
        ports=[
            PluginPort(internal="1234"),                # Internal only(For node communication for example)
            PluginPort(internal="2345", public=True),   # Open the port to the public(When ssh into). Used for UI for example
        ],

        # Pick where you want the plugin to run
        target=PluginTarget.Host,                       # The script will be run on the host. Default value is to run in the spark container
        target_role=PluginTargetRole.All,               # If the plugin should be run only on the master worker or all. You can use environment variables(See below to have different master/worker config)
    )
  ]
)
```

## Parameters

### `PluginConfiguration`

#### name  `required`  | `string`
Name of your plugin(This will be used for creating folder, it is recommended to have a simple letter, dash, underscore only name)

#### files `required`  | `List[PluginFile|PluginTextFile]`
List of files to upload

#### execute `required`  | `str`
Script to execute. This script must be defined in the files above and must match its remote path

#### args `optional`  | List[str]
List of arguments to be passed to your execute scripts

#### env `optional`  | dict
List of environment variables to access in the script(This can be used to pass arguments to your script instead of args)

#### ports  `optional`  | `List[PluginPort]`
List of ports to open if the script is running in a container. A port can also be specific public and it will then be accessible when ssh into the master node.

#### target     | `optional`  | `PluginTarget`
Define where the execute script should be running. Potential values are `PluginTarget.SparkContainer(Default)` and `PluginTarget.Host`

#### `taget_role` | `optional`  | `PluginTargetRole`
If the plugin should be run only on the master worker or all. You can use environment variables(See below to have different master/worker config)

### `PluginFile`

#### `target`      `required`  | `str`
Where the file should be dropped relative to the plugin working directory

#### `local_path` | `required`  | `str`
Path to the local file you want to upload(Could form the plugins parameters)

### `TextPluginFile`

#### target  | `required`  | `str`
 Where the file should be dropped relative to the plugin working directory

#### content | `required`  | `str` | `io.StringIO`
 Path to the local file you want to upload(Could form the plugins parameters)

### `PluginPort`
#### internal | `required`  | `int`
 Internal port to open on the docker container
#### public   | `optional`  | `bool`
 If the port should be open publicly(Default: `False`)

## Environment variables available in the plugin

AZTK provide a few environment variables that can be used in your plugin script

* `AZTK_IS_MASTER`: Is the plugin running on the master node. Can be either `true` or `false`
* `AZTK_IS_WORKER`: Is a worker setup on the current node(This might also be a master if you have `worker_on_master` set to true) Can be either `true` or `false`
* `AZTK_MASTER_IP`: Internal ip of the master

## Debug your plugin
When your plugin is not working as expected there is a few things you do to investigate issues

Check the logs, you can either use the debug tool or [BatchLabs](https://github.com/Azure/BatchLabs)
Navigate to `startup/wd/logs/plugins`
![](misc/plugin-logs.png)

* Now if you see a file named `<your-plugin-name>.txt` under that folder it means that your plugin started correctly and you can check this file to see what you execute script logged.
* IF this file doesn't exists this means the script was not run on this node. There could be multiple reasons for this:
  - If you want your plugin to run on the spark container check the `startup/wd/logs/docker.log` file for information about this
  - If you want your plugin to run on the host check the `startup/stdout.txt` and `startup/stderr.txt`

  The log could mention you picked the wrong target or target role for that plugin which is why this plugin is not running on this node.
