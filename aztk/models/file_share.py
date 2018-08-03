from aztk.core.models import Model, fields


class FileShare(Model):
    storage_account_name = fields.String()
    storage_account_key = fields.String()
    file_share_path = fields.String()
    mount_path = fields.String()
