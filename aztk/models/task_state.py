from enum import Enum


class TaskState(Enum):
    Running = "running"
    Completed = "completed"
    Failed = "failed"
    Preparing = "preparing"
