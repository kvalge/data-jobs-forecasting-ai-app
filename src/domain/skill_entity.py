# skill_entity.py
from dataclasses import dataclass

from src.domain.base_entity import BaseEntity


@dataclass
class SkillEntity(BaseEntity):
    """Pure business representation of a skill/technology.

    `name` is the normalized unique key (lowercase English).
    `display_name` is the first-seen original casing/language.
    `display_name_en` is the English label.
    """

    name: str = ""
    display_name: str = ""
    display_name_en: str = ""
