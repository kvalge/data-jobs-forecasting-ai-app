# base_entity.py
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class BaseEntity:
    """Common fields/behavior shared by all domain entities."""

    id: int | None = field(default=None)
    created_at: datetime = field(default_factory=datetime.now)