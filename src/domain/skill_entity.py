# skill_entity.py
from dataclasses import dataclass

from src.domain.base_entity import BaseEntity


@dataclass
class SkillEntity(BaseEntity):
    """Pure business representation of a skill/technology.

    `name` is the normalized unique key (lowercase).
    `display_name` is the first-seen casing for UI/reports.
    """

    name: str = ""
    display_name: str = ""
