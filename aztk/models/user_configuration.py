from aztk.core.models import Model, fields


class UserConfiguration(Model):
    username = fields.String()
    ssh_key = fields.String(default=None)
    password = fields.String(default=None)
