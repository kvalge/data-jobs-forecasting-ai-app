# prediction_types.py
"""Shared forecast target types and run status strings."""

from __future__ import annotations


class TargetType:
    ROLE = "role"
    SALARY_ROLE = "salary_role"
    SKILL = "skill"
    BASELINE_ROLE = "baseline_role"
    BASELINE_SKILL = "baseline_skill"


class RunStatus:
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"
