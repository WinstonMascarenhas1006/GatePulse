"""Smoke tests for GatePulse."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gatepulse.etl import clean_milestones  # noqa: E402
from gatepulse.quality import score_quality  # noqa: E402


def test_generate_linked(tmp_path, monkeypatch):
    import gatepulse.generate_data as gd

    monkeypatch.setattr(gd, "DATA_RAW", tmp_path)
    tables = gd.generate_all(seed=1)
    assert "campuses" in tables
    assert "campus_code" in tables["launches"].columns
    assert len(tables["launches"]) >= 8
    assert set(tables["milestones"]["launch_id"]).issubset(set(tables["launches"]["launch_id"]))


def test_clean_milestones():
    df = pd.DataFrame(
        [
            {
                "milestone_id": "M-1",
                "launch_id": "L-1",
                "sequence": 1,
                "milestone_type": "Pilot",
                "planned_date": "2026-99-99",
                "actual_date": None,
                "status": "Unkown",
                "progress_pct": None,
                "slip_days": 0,
                "is_delayed_flag": 0,
            },
            {
                "milestone_id": "M-2",
                "launch_id": "L-1",
                "sequence": 2,
                "milestone_type": "Exam papers ready",
                "planned_date": "2026-10-01",
                "actual_date": None,
                "status": "In progress",
                "progress_pct": 40,
                "slip_days": 2,
                "is_delayed_flag": 0,
            },
        ]
    )
    clean, issues = clean_milestones(df)
    assert len(issues) >= 2
    assert clean["progress_pct"].notna().all()


def test_quality_bounds():
    milestones = pd.DataFrame({"milestone_id": ["M-1"], "launch_id": ["L-1"]})
    issues = pd.DataFrame(
        [
            {
                "table_name": "milestones",
                "record_id": "M-1",
                "field": "status",
                "issue_type": "invalid_category",
                "raw_value": "x",
                "severity": "y",
            }
        ]
    )
    out = score_quality(issues, milestones)
    assert 0 <= out["summary"]["overall_quality_score"] <= 100
