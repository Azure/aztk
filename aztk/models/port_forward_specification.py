from aztk.core.models import Model, fields


class PortForwardingSpecification(Model):
    remote_port = fields.Integer()
    local_port = fields.Integer()
