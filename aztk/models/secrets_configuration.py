from aztk.core.models import Model, fields
from aztk.error import InvalidModelError


class ServicePrincipalConfiguration(Model):
    """
    Container class for AAD authentication
    """

    tenant_id = fields.String()
    client_id = fields.String()
    credential = fields.String()
    batch_account_resource_id = fields.String()
    storage_account_resource_id = fields.String()


class SharedKeyConfiguration(Model):
    """
    Container class for shared key authentication
    """

    batch_account_name = fields.String()
    batch_account_key = fields.String()
    batch_service_url = fields.String()
    storage_account_name = fields.String()
    storage_account_key = fields.String()
    storage_account_suffix = fields.String()


class DockerConfiguration(Model):
    """
    Configuration for connecting to private docker

    Args:
        endpoint (str): Which docker endpoint to use. Default to docker hub.
        username (str): Docker endpoint username
        password (str): Docker endpoint password
    """

    endpoint = fields.String(default=None)
    username = fields.String(default=None)
    password = fields.String(default=None)


class SecretsConfiguration(Model):
    service_principal = fields.Model(ServicePrincipalConfiguration, default=None)
    shared_key = fields.Model(SharedKeyConfiguration, default=None)
    docker = fields.Model(DockerConfiguration, default=None)
    ssh_pub_key = fields.String(default=None)
    ssh_priv_key = fields.String(default=None)

    def __validate__(self):
        if self.service_principal and self.shared_key:
            raise InvalidModelError("Both service_principal and shared_key auth are configured, must use only one")

        if not self.service_principal and not self.shared_key:
            raise InvalidModelError("Neither service_principal and shared_key auth are configured, must use only one")

    def is_aad(self):
        return self.service_principal is not None
