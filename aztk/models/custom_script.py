from aztk.core.models import Model, fields


class CustomScript(Model):
    name = fields.String()
    script = fields.String()
    run_on = fields.String()
