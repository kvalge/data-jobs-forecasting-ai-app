# skill_entity.py
from dataclasses import dataclass

from src.domain.base_entity import BaseEntity


@dataclass
class SkillEntity(BaseEntity):
    """Pure business representation of a skill/technology."""

    name: str = ""