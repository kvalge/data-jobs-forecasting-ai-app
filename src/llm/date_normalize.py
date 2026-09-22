"""Normalize messy LLM date strings to ISO YYYY-MM-DD for Pydantic date fields."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any


# 21.10.2026 / 21/10/2026 / 21-10-2026 (day-month-year, common in EU postings)
_DMY = re.compile(
    r"^\s*(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})\s*$"
)
# 2026.10.21 / 2026/10/21 / 2026-10-21
_YMD = re.compile(
    r"^\s*(\d{4})[./\-](\d{1,2})[./\-](\d{1,2})\s*$"
)
# 21 Oct 2026 / 21 October 2026
_DMONTHY = re.compile(
    r"^\s*(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})\s*$"
)


def normalize_optional_date(value: Any) -> Any:
    """Coerce common LLM deadline strings to ``date`` or ISO ``YYYY-MM-DD``.

    Leaves ``None`` / empty / already-``date`` values alone. Unparseable strings
    are returned unchanged so Pydantic can raise a clear validation error.
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return value

    text = value.strip()
    if not text or text.lower() in ("null", "none", "n/a", "-"):
        return None

    # Already ISO-like
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass

    m = _YMD.match(text)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(year, month, day)
        except ValueError:
            return value

    m = _DMY.match(text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        # Prefer DMY when day > 12 (unambiguous). When both <= 12, still assume DMY
        # because EU job postings dominate this app's inputs.
        try:
            return date(year, month, day)
        except ValueError:
            return value

    m = _DMONTHY.match(text)
    if m:
        day_s, month_s, year_s = m.group(1), m.group(2), m.group(3)
        for fmt in ("%d %b %Y", "%d %B %Y"):
            try:
                return datetime.strptime(f"{day_s} {month_s} {year_s}", fmt).date()
            except ValueError:
                continue

    return value
