from aztk.spark import models


def get_application_log(core_base_operations,
                        cluster_id: str,
                        application_name: str,
                        tail=False,
                        current_bytes: int = 0):
    base_application_log = core_base_operations.get_application_log(cluster_id, application_name, tail, current_bytes)
    return models.ApplicationLog(base_application_log)
