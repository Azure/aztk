import azure.batch.models as batch_models


class ApplicationLog:
    def __init__(
            self,
            name: str,
            cluster_id: str,
            log: str,
            total_bytes: int,
            application_state: batch_models.TaskState,
            exit_code: int,
    ):
        self.name = name
        self.cluster_id = cluster_id    # TODO: change to something cluster/job agnostic
        self.log = log
        self.total_bytes = total_bytes
        self.application_state = application_state
        self.exit_code = exit_code
