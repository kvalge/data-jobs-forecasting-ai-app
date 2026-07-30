"""Make Python values safe for PostgreSQL / SQLAlchemy JSON columns.

Postgres JSON rejects NaN/Infinity tokens that Python's default json encoding
(and SQLAlchemy's JSON serializer) can emit from float('nan').
"""

from __future__ import annotations

import math
from typing import Any


def json_safe(value: Any) -> Any:
    """Recursively replace NaN/Inf with None; leave other values unchanged."""
    if value is None:
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value

    # numpy scalars (optional dependency)
    try:
        import numpy as np

        if isinstance(value, np.floating):
            f = float(value)
            if math.isnan(f) or math.isinf(f):
                return None
            return f
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, np.ndarray):
            return json_safe(value.tolist())
    except ImportError:
        pass

    # pandas NA / NaT
    try:
        import pandas as pd

        if value is pd.NA:
            return None
        if isinstance(value, pd.Timestamp):
            if pd.isna(value):
                return None
            return value.isoformat()
    except ImportError:
        pass

    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]

    return value
