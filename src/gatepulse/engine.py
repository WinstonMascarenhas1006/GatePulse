"""
Staged pipeline API for Engine Room UI.
Decision D-021: each backend stage callable with log lines for the frontend.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd

from gatepulse.ai_risk import generate_insights, train_and_score
from gatepulse.config import DATA_PROCESSED, DATA_RAW, DB_PATH, MODELS_DIR, ROOT
from gatepulse.etl import run_etl
from gatepulse.generate_data import generate_all
from gatepulse.quality import run_quality
from gatepulse.report import export_all

LogFn = Callable[[str], None]


@dataclass
class StageResult:
    name: str
    ok: bool
    detail: dict
    elapsed_s: float
    logs: list[str] = field(default_factory=list)


PIPELINE_STAGES = [
    {
        "id": "generate",
        "title": "1 · Generate",
        "layer": "BACKEND",
        "blurb": "Synthetic NPI launches, gates, tasks (source of truth for demo).",
        "writes": "data/raw/*.csv",
    },
    {
        "id": "etl",
        "title": "2 · ETL",
        "layer": "BACKEND",
        "blurb": "Clean invalid dates/statuses, build launch facts, load SQLite.",
        "writes": "data/processed/* + gatepulse.db",
    },
    {
        "id": "quality",
        "title": "3 · Data quality",
        "layer": "BACKEND",
        "blurb": "Score completeness/validity; per-launch quality index.",
        "writes": "quality_by_launch.csv",
    },
    {
        "id": "ai",
        "title": "4 · AI risk",
        "layer": "BACKEND",
        "blurb": "Train RandomForest slip-risk; export scores + feature importance.",
        "writes": "models/* + launch_risk_scores.csv",
    },
    {
        "id": "export",
        "title": "5 · Export",
        "layer": "BACKEND",
        "blurb": "Excel steering pack + Markdown executive brief.",
        "writes": "data/exports/*",
    },
]


def _log(logs: list[str], fn: LogFn | None, msg: str) -> None:
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    logs.append(line)
    if fn:
        fn(line)


def run_stage(stage_id: str, log: LogFn | None = None, seed: int = 42) -> StageResult:
    logs: list[str] = []
    t0 = time.perf_counter()
    try:
        if stage_id == "generate":
            _log(logs, log, "Calling gatepulse.generate_data.generate_all ...")
            tables = generate_all(seed=seed)
            detail = {k: len(v) for k, v in tables.items()}
            _log(logs, log, f"Wrote raw tables: {detail}")
        elif stage_id == "etl":
            _log(logs, log, "Calling gatepulse.etl.run_etl ...")
            out = run_etl()
            detail = {k: len(v) for k, v in out.items()}
            _log(logs, log, f"Processed + SQLite at {DB_PATH.name}: {detail}")
        elif stage_id == "quality":
            _log(logs, log, "Calling gatepulse.quality.run_quality ...")
            summary, per = run_quality()
            detail = {"summary": summary, "scored_launches": len(per)}
            _log(logs, log, f"Quality summary: {summary}")
        elif stage_id == "ai":
            _log(logs, log, "Calling gatepulse.ai_risk.train_and_score ...")
            ai = train_and_score(seed=seed)
            metrics = {
                k: ai["metrics"].get(k) for k in ("n_train", "n_test", "roc_auc", "positive_rate")
            }
            detail = {"metrics": metrics, "scored_rows": len(ai["scored"])}
            _log(logs, log, f"Model metrics: {metrics}")
        elif stage_id == "export":
            _log(logs, log, "Calling gatepulse.report.export_all ...")
            paths = export_all()
            detail = paths
            _log(logs, log, f"Exports: {paths}")
        else:
            raise ValueError(f"Unknown stage: {stage_id}")

        # Refresh pipeline meta when full-ish progress happens
        if stage_id in {"ai", "export"} and (DATA_PROCESSED / "launch_facts_scored.csv").exists():
            facts = pd.read_csv(DATA_PROCESSED / "launch_facts_scored.csv")
            risks = pd.read_csv(DATA_PROCESSED / "launch_risk_scores.csv")
            meta = {
                "finished": datetime.now().isoformat(timespec="seconds"),
                "last_stage": stage_id,
                "insights": generate_insights(risks, facts),
                "project_root": str(ROOT),
            }
            (DATA_PROCESSED / "last_pipeline_run.json").write_text(
                json.dumps(meta, indent=2), encoding="utf-8"
            )

        elapsed = time.perf_counter() - t0
        _log(logs, log, f"Stage '{stage_id}' OK in {elapsed:.2f}s")
        return StageResult(stage_id, True, detail, elapsed, logs)
    except Exception as exc:  # noqa: BLE001
        elapsed = time.perf_counter() - t0
        _log(logs, log, f"Stage '{stage_id}' FAILED: {exc}")
        return StageResult(stage_id, False, {"error": str(exc)}, elapsed, logs)


def run_all_stages(log: LogFn | None = None, seed: int = 42) -> list[StageResult]:
    return [run_stage(s["id"], log=log, seed=seed) for s in PIPELINE_STAGES]


def lineage_nodes_edges() -> tuple[list[dict], list[dict]]:
    """Graph payload for Plotly/Sankey-style lineage in UI."""
    nodes = [
        {"id": "raw", "label": "RAW CSVs", "layer": "storage"},
        {"id": "etl", "label": "ETL cleaner", "layer": "backend"},
        {"id": "sqlite", "label": "SQLite", "layer": "storage"},
        {"id": "facts", "label": "Launch facts", "layer": "backend"},
        {"id": "dq", "label": "Quality scorer", "layer": "backend"},
        {"id": "ml", "label": "AI slip-risk", "layer": "backend"},
        {"id": "export", "label": "Excel / Brief", "layer": "backend"},
        {"id": "ui", "label": "Streamlit UI", "layer": "frontend"},
    ]
    edges = [
        {"source": "raw", "target": "etl", "label": "read"},
        {"source": "etl", "target": "sqlite", "label": "load"},
        {"source": "etl", "target": "facts", "label": "aggregate"},
        {"source": "facts", "target": "dq", "label": "score"},
        {"source": "facts", "target": "ml", "label": "features"},
        {"source": "dq", "target": "ml", "label": "quality_score"},
        {"source": "ml", "target": "export", "label": "risks"},
        {"source": "facts", "target": "ui", "label": "KPIs"},
        {"source": "ml", "target": "ui", "label": "scores"},
        {"source": "dq", "target": "ui", "label": "issues"},
        {"source": "export", "target": "ui", "label": "download"},
        {"source": "sqlite", "target": "ui", "label": "SQL lab"},
    ]
    return nodes, edges


def list_sqlite_tables() -> list[str]:
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return [r[0] for r in rows]


def read_sqlite_table(name: str, limit: int = 200) -> pd.DataFrame:
    if name not in list_sqlite_tables():
        raise ValueError(f"Unknown table: {name}")
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f'SELECT * FROM "{name}" LIMIT {int(limit)}', conn)


def raw_vs_clean_milestones(sample: int = 12) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw_path = DATA_RAW / "milestones.csv"
    clean_path = DATA_PROCESSED / "milestones.csv"
    issues_path = DATA_PROCESSED / "quality_issues.csv"
    if not raw_path.exists() or not clean_path.exists():
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    raw = pd.read_csv(raw_path)
    clean = pd.read_csv(clean_path)
    issues = pd.read_csv(issues_path) if issues_path.exists() else pd.DataFrame()
    if len(issues):
        ids = issues["record_id"].head(sample).tolist()
        raw_s = raw[raw["milestone_id"].isin(ids)]
        clean_s = clean[clean["milestone_id"].isin(ids)]
    else:
        raw_s = raw.head(sample)
        clean_s = clean.head(sample)
    return raw_s, clean_s, issues


def artifact_inventory() -> pd.DataFrame:
    rows = []
    for label, path in [
        ("raw/", DATA_RAW),
        ("processed/", DATA_PROCESSED),
        ("exports/", ROOT / "data" / "exports"),
        ("models/", MODELS_DIR),
    ]:
        if not path.exists():
            continue
        for f in sorted(path.glob("*")):
            if f.is_file():
                rows.append(
                    {
                        "zone": label,
                        "file": f.name,
                        "kb": round(f.stat().st_size / 1024, 1),
                        "layer": "BACKEND artifact",
                    }
                )
    return pd.DataFrame(rows)
