"""Tests for JSON-safe sanitization used before Postgres JSON inserts."""

import json
import math

import numpy as np

from src.dal.json_safe import json_safe


def test_json_safe_replaces_nan_and_inf():
    payload = {
        "key": "AI Security Engineer",
        "latest": float("nan"),
        "nested": {"slope": float("inf"), "ok": 1.5},
        "list": [float("-inf"), 2, None],
        "np": np.float64("nan"),
    }
    cleaned = json_safe(payload)
    assert cleaned["latest"] is None
    assert cleaned["nested"]["slope"] is None
    assert cleaned["nested"]["ok"] == 1.5
    assert cleaned["list"] == [None, 2, None]
    assert cleaned["np"] is None
    json.dumps(cleaned, allow_nan=False)
    assert not any(
        isinstance(v, float) and math.isnan(v)
        for v in [cleaned["latest"], cleaned["np"]]
    )
