from aztk.error import InvalidModelError
from aztk.utils import constants, deprecate
from aztk.core.models import Model, fields

class ToolkitDefinition:
    def __init__(self, versions, environments):
        self.versions = versions
        self.environments = environments

class ToolkitEnvironmentDefinition:
    def __init__(self, versions=None, default=""):
        self.versions = versions or [""]
        self.default = default

TOOLKIT_MAP = dict(
    spark=ToolkitDefinition(
        versions=["1.6.3", "2.1.0", "2.2.0", "2.3.0"],
        environments=dict(
            base=ToolkitEnvironmentDefinition(),
            r=ToolkitEnvironmentDefinition(),
            miniconda=ToolkitEnvironmentDefinition(),
            anaconda=ToolkitEnvironmentDefinition(),
        )
    ),
)


class Toolkit(Model):
    """
    Toolkit for a cluster.
    This will help pick the docker image needed

    Args:
        software (str): Name of the toolkit(spark)
        version (str): Version of the toolkit
        environment (str): Which environment to use for this toolkit
        environment_version (str): If there is multiple version for an environment you can specify which one
        docker_repo (str): Optional docker repo
    """

    software = fields.String()
    version = fields.String()
    environment = fields.String(default=None)
    environment_version = fields.String(default=None)
    docker_repo = fields.String(default=None)

    def __validate__(self):
        if self.software not in TOOLKIT_MAP:
            raise InvalidModelError("Toolkit '{0}' is not in the list of allowed toolkits {1}".format(
                self.software, list(TOOLKIT_MAP.keys())))

        toolkit_def = TOOLKIT_MAP[self.software]

        if self.version not in toolkit_def.versions:
            raise InvalidModelError("Toolkit '{0}' with version '{1}' is not available. Use one of: {2}".format(
                self.software, self.version, toolkit_def.versions))
        if self.version == "1.6":
            deprecate("0.9.0", "Spark version 1.6 is being deprecated for Aztk.", "Please use 2.1 and above.")

        if self.environment:
            if self.environment not in toolkit_def.environments:
                raise InvalidModelError("Environment '{0}' for toolkit '{1}' is not available. Use one of: {2}".format(
                    self.environment, self.software, list(toolkit_def.environments.keys())))

            env_def = toolkit_def.environments[self.environment]

            if self.environment_version and self.environment_version not in env_def.versions:
                raise InvalidModelError(
                    "Environment '{0}' version '{1}' for toolkit '{2}' is not available. Use one of: {3}".format(
                        self.environment, self.environment_version, self.software, env_def.versions))


    def get_docker_repo(self, gpu: bool):
        if self.docker_repo:
            return self.docker_repo

        repo = "aztk/{0}".format(self.software)

        return "{repo}:{tag}".format(
            repo=repo,
            tag=self._get_docker_tag(gpu),
        )

    def _get_docker_tag(self, gpu: bool):
        environment = self.environment or "base"
        environment_def = self._get_environment_definition()
        environment_version = self.environment_version or (environment_def and environment_def.default)

        array = [
            "v{docker_image_version}".format(docker_image_version=constants.DOCKER_IMAGE_VERSION),
            "{toolkit}{version}".format(toolkit=self.software, version=self.version),
        ]
        if self.environment:
            array.append("{0}{1}".format(environment, environment_version))

        array.append("gpu" if gpu else "base")

        return '-'.join(array)


    def _get_environment_definition(self) -> ToolkitEnvironmentDefinition:
        toolkit = TOOLKIT_MAP.get(self.software)

        if toolkit:
            return toolkit.environments.get(self.environment or "base")
        return None
