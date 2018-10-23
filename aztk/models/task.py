from datetime import datetime

from aztk.core.models import Model, fields


class Task(Model):
    id = fields.String()
    node_id = fields.String(default=None)
    state = fields.String(default=None)
    state_transition_time = fields.String(default=None)
    command_line = fields.String(default=None)
    exit_code = fields.Integer(default=None)
    start_time = fields.Datetime(datetime, default=None)
    end_time = fields.Datetime(datetime, default=None)
    failure_info = fields.String(default=None)
