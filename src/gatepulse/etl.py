"""
ETL: raw CSV -> cleaned frames -> SQLite.
Sources: S-PRIOR-01 pattern, S-DQ-01 cleaning rules. Analogous to Power Query refresh.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from gatepulse.config import DATA_PROCESSED, DATA_RAW, DB_PATH, STATUSES


def _read_raw(name: str) -> pd.DataFrame:
    path = DATA_RAW / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing raw file: {path}. Run generate_data first.")
    return pd.read_csv(path)


def clean_milestones(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    issues = []
    clean = df.copy()

    parsed = pd.to_datetime(clean["planned_date"], errors="coerce", format="mixed")
    bad_dates = parsed.isna() & clean["planned_date"].notna()
    for idx in clean.index[bad_dates]:
        issues.append(
            {
                "table_name": "milestones",
                "record_id": clean.at[idx, "milestone_id"],
                "field": "planned_date",
                "issue_type": "invalid_date",
                "raw_value": str(clean.at[idx, "planned_date"]),
                "severity": "Imputed from campus-programme median planned date",
            }
        )
    clean.loc[bad_dates, "planned_date"] = pd.NaT
    clean["planned_date"] = parsed
    for lid, grp in clean.groupby("launch_id"):
        med = grp["planned_date"].median()
        mask = clean["launch_id"].eq(lid) & clean["planned_date"].isna()
        clean.loc[mask, "planned_date"] = med

    clean["actual_date"] = pd.to_datetime(clean["actual_date"], errors="coerce")

    null_prog = clean["progress_pct"].isna()
    for idx in clean.index[null_prog]:
        issues.append(
            {
                "table_name": "milestones",
                "record_id": clean.at[idx, "milestone_id"],
                "field": "progress_pct",
                "issue_type": "missing_value",
                "raw_value": "",
                "severity": "Imputed 0 if Not started else 50",
            }
        )
    clean.loc[null_prog & clean["status"].eq("Not started"), "progress_pct"] = 0
    clean.loc[null_prog & ~clean["status"].eq("Not started"), "progress_pct"] = 50

    bad_status = ~clean["status"].isin(STATUSES)
    for idx in clean.index[bad_status]:
        issues.append(
            {
                "table_name": "milestones",
                "record_id": clean.at[idx, "milestone_id"],
                "field": "status",
                "issue_type": "invalid_category",
                "raw_value": str(clean.at[idx, "status"]),
                "severity": "Mapped to In progress",
            }
        )
    clean.loc[bad_status, "status"] = "In progress"

    clean["progress_pct"] = clean["progress_pct"].astype(float).clip(0, 100)
    clean["slip_days"] = pd.to_numeric(clean["slip_days"], errors="coerce").fillna(0).astype(int)
    clean["is_delayed_flag"] = pd.to_numeric(clean["is_delayed_flag"], errors="coerce").fillna(0).astype(int)
    clean["planned_date"] = clean["planned_date"].dt.strftime("%Y-%m-%d")
    clean["actual_date"] = clean["actual_date"].dt.strftime("%Y-%m-%d")
    clean["actual_date"] = clean["actual_date"].replace("NaT", np.nan)
    return clean, pd.DataFrame(issues)


def build_launch_facts(
    launches: pd.DataFrame,
    milestones: pd.DataFrame,
    tasks: pd.DataFrame,
    launch_workstreams: pd.DataFrame,
    workstreams: pd.DataFrame,
    programs: pd.DataFrame,
) -> pd.DataFrame:
    m = milestones.copy()
    open_ms = m[m["status"] != "Completed"]

    agg = (
        m.groupby("launch_id")
        .agg(
            milestone_count=("milestone_id", "count"),
            avg_progress=("progress_pct", "mean"),
            max_slip_days=("slip_days", "max"),
            avg_slip_days=("slip_days", "mean"),
            delayed_milestones=("is_delayed_flag", "sum"),
        )
        .reset_index()
    )
    open_counts = open_ms.groupby("launch_id").size().rename("open_milestones").reset_index()
    blocked = (
        m[m["status"] == "Blocked"]
        .groupby("launch_id")
        .size()
        .rename("blocked_milestones")
        .reset_index()
    )
    task_agg = (
        tasks.groupby("launch_id")
        .agg(
            task_count=("task_id", "count"),
            open_tasks=("status", lambda s: int((s != "Completed").sum())),
            blocked_tasks=("status", lambda s: int((s == "Blocked").sum())),
            effort_hours=("effort_hours", "sum"),
        )
        .reset_index()
    )
    ws = launch_workstreams.merge(workstreams, on="ws_code", how="left")
    ws_agg = (
        ws.groupby("launch_id")
        .agg(
            workstream_count=("ws_code", "count"),
            avg_complexity=("complexity", "mean"),
            max_complexity=("complexity", "max"),
            typical_days_sum=("typical_days", "sum"),
        )
        .reset_index()
    )

    facts = (
        launches.merge(programs, on="program_id", how="left")
        .merge(agg, on="launch_id", how="left")
        .merge(open_counts, on="launch_id", how="left")
        .merge(blocked, on="launch_id", how="left")
        .merge(task_agg, on="launch_id", how="left")
        .merge(ws_agg, on="launch_id", how="left")
    )
    for col in ["open_milestones", "blocked_milestones", "delayed_milestones"]:
        facts[col] = facts[col].fillna(0).astype(int)
    facts["avg_progress"] = facts["avg_progress"].fillna(0).round(1)
    # Health rules: Critical if blocked OR max slip >= 28 (prior lesson D-016b)
    facts["health"] = np.select(
        [
            (facts["blocked_milestones"] > 0) | (facts["max_slip_days"] >= 28),
            facts["delayed_milestones"] > 0,
            facts["avg_progress"] >= 70,
        ],
        ["Critical", "At risk", "On track"],
        default="Watch",
    )
    return facts


def run_etl() -> dict[str, pd.DataFrame]:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    campuses = _read_raw("campuses")
    programs = _read_raw("programs")
    workstreams = _read_raw("workstreams")
    launches = _read_raw("launches")
    launch_workstreams = _read_raw("launch_workstreams")
    milestones_raw = _read_raw("milestones")
    tasks = _read_raw("tasks")

    milestones, quality_issues = clean_milestones(milestones_raw)
    launch_facts = build_launch_facts(
        launches, milestones, tasks, launch_workstreams, workstreams, programs
    )

    outputs = {
        "campuses": campuses,
        "programs": programs,
        "workstreams": workstreams,
        "launches": launches,
        "launch_workstreams": launch_workstreams,
        "milestones": milestones,
        "tasks": tasks,
        "launch_facts": launch_facts,
        "quality_issues": quality_issues,
    }
    for name, df in outputs.items():
        df.to_csv(DATA_PROCESSED / f"{name}.csv", index=False)

    with sqlite3.connect(DB_PATH) as conn:
        for name, df in outputs.items():
            df.to_sql(name, conn, index=False, if_exists="replace")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ms_launch ON milestones(launch_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_campus ON launch_facts(campus_code)")
    return outputs


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    result = run_etl()
    print({k: len(v) for k, v in result.items()})
