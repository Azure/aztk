from aztk.utils.command_builder import CommandBuilder


class DockerCmd:
    """
    Class helping to write a docker command
    """

    def __init__(self, name: str, docker_repo: str, docker_run_options: str, cmd: str, gpu_enabled=False):
        if gpu_enabled:
            self.cmd = CommandBuilder("nvidia-docker run")
        else:
            self.cmd = CommandBuilder("docker run")
        self.cmd.add_option("--net", "host")
        self.cmd.add_option("--name", name)
        self.cmd.add_argument("-d")
        self.cmd.add_argument(docker_run_options)
        self.cmd.add_argument(docker_repo)
        self.cmd.add_argument(cmd)

    def add_env(self, env: str, value: str):
        self.cmd.add_option("-e", "{0}={1}".format(env, value))

    def pass_env(self, env: str):
        """
        Give the value of an environment variable in the main process to the docker image
        """
        self.cmd.add_option("-e", "{0}".format(env))

    def share_folder(self, folder: str):
        self.cmd.add_option("-v", "{0}:{0}".format(folder))

    def open_port(self, port: int):
        self.cmd.add_option("-p", "{0}:{0}".format(port))    # Spark Master UI

    def to_str(self):
        return self.cmd.to_str()
