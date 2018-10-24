from aztk.models import SchedulingTarget

from .get_recent_job import get_recent_job
from .task_table import list_task_table_entries


def list_tasks(core_base_operations, id):
    """List all tasks on a job or cluster

    This will work for both Batch scheduling and scheduling_target

    Args:
        id: cluster or job id
    Returns:
        List[aztk.models.Task]

    """
    scheduling_target = core_base_operations.get_cluster_configuration(id).scheduling_target
    if scheduling_target is not SchedulingTarget.Any:
        return list_task_table_entries(core_base_operations.table_service, id)
    else:
        # note: this currently only works for job_schedules
        # cluster impl is planned to move to job schedules
        recent_run_job = get_recent_job(core_base_operations, id)
        tasks = core_base_operations.list_batch_tasks(id=recent_run_job.id)
        return tasks
