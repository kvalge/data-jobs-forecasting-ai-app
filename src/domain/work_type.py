# work_type.py
from enum import Enum


class WorkType(str, Enum):
    onsite = "onsite"
    hybrid = "hybrid"
    remote = "remote"
    unknown = "unknown"