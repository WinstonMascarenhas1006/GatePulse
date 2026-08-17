"""
GatePulse HTTP API + static custom UI (D-026).
Serves app/web and exposes backend pipeline/data endpoints.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gatepulse.ai_risk import FEATURE_COLS_CAT, FEATURE_COLS_NUM, generate_insights, score_what_if  # noqa: E402
from gatepulse.config import DATA_EXPORTS, DATA_PROCESSED, DATA_RAW, MODELS_DIR  # noqa: E402
from gatepulse.engine import (  # noqa: E402
    PIPELINE_STAGES,
    artifact_inventory,
    lineage_nodes_edges,
    list_sqlite_tables,
    raw_vs_clean_milestones,
    read_sqlite_table,
    run_all_stages,
    run_stage,
)

WEB_DIR = Path(__file__).resolve().parent / "web"

app = FastAPI(title="GatePulse API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class WhatIfBody(BaseModel):
    avg_complexity: float = 3.0
    max_complexity: float = 4.0
    workstream_count: float = 5.0
    open_tasks: float = 10.0
    blocked_tasks: float = 0.0
    open_milestones: float = 2.0
    blocked_milestones: float = 0.0
    avg_slip_days: float = 5.0
    quality_score: float = 85.0
    effort_hours: float = 40.0
    campus_code: str = "RIV"
    priority: str = "P2"
    power_class: str = "Secondary"
    family: str = "Exams"


class StageBody(BaseModel):
    seed: int = Field(default=42, ge=1, le=9999)


def _read_csv(name: str) -> list[dict[str, Any]]:
    path = DATA_PROCESSED / f"{name}.csv"
    if not path.exists():
        raise HTTPException(404, f"Missing {name}.csv — run pipeline first")
    df = pd.read_csv(path)
    return json.loads(df.to_json(orient="records"))


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "product": "GatePulse", "ui": "custom-web", "domain": "schools"}


@app.get("/api/meta")
def meta() -> dict:
    path = DATA_PROCESSED / "last_pipeline_run.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"finished": None, "message": "No pipeline run yet"}


@app.get("/api/overview")
def overview() -> dict:
    facts = pd.read_csv(DATA_PROCESSED / "launch_facts_scored.csv")
    risks = pd.read_csv(DATA_PROCESSED / "launch_risk_scores.csv")
    by_campus = (
        facts.groupby(["campus_code", "health"]).size().reset_index(name="count")
    )
    return {
        "kpis": {
            "launches": int(len(facts)),
            "critical": int((facts["health"] == "Critical").sum()),
            "high_risk": int((facts["slip_risk_label"] == "High").sum()),
            "avg_progress": round(float(facts["avg_progress"].mean()), 1),
            "avg_risk": round(float(facts["slip_risk_score"].mean()), 1),
        },
        "health_by_campus": json.loads(by_campus.to_json(orient="records")),
        "scatter": json.loads(
            facts[
                [
                    "launch_name",
                    "campus_code",
                    "avg_progress",
                    "slip_risk_score",
                    "avg_complexity",
                    "health",
                ]
            ].to_json(orient="records")
        ),
        "insights": generate_insights(risks, facts),
    }


@app.get("/api/launches")
def launches() -> list:
    return _read_csv("launch_facts_scored")


@app.get("/api/launches/{launch_id}/milestones")
def launch_milestones(launch_id: str) -> list:
    df = pd.read_csv(DATA_PROCESSED / "milestones.csv")
    out = df[df["launch_id"] == launch_id].sort_values("sequence")
    return json.loads(out.to_json(orient="records"))


@app.get("/api/launches/{launch_id}/tasks")
def launch_tasks(launch_id: str) -> list:
    df = pd.read_csv(DATA_PROCESSED / "tasks.csv")
    out = df[df["launch_id"] == launch_id]
    return json.loads(out.to_json(orient="records"))


@app.get("/api/quality/issues")
def quality_issues() -> list:
    return _read_csv("quality_issues")


@app.get("/api/data/raw-vs-clean")
def raw_vs_clean() -> dict:
    raw_s, clean_s, issues = raw_vs_clean_milestones()
    return {
        "raw": json.loads(raw_s.to_json(orient="records")),
        "clean": json.loads(clean_s.to_json(orient="records")),
        "issues": json.loads(issues.to_json(orient="records")),
        "raw_path": str(DATA_RAW / "milestones.csv"),
        "clean_path": str(DATA_PROCESSED / "milestones.csv"),
    }


@app.get("/api/sqlite/tables")
def sqlite_tables() -> list:
    return list_sqlite_tables()


@app.get("/api/sqlite/{table}")
def sqlite_table(table: str, limit: int = 100) -> list:
    try:
        df = read_sqlite_table(table, limit)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return json.loads(df.to_json(orient="records"))


@app.get("/api/model/metrics")
def model_metrics() -> dict:
    path = MODELS_DIR / "metrics.json"
    if not path.exists():
        raise HTTPException(404, "Run AI stage first")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/model/feature-importance")
def feature_importance() -> list:
    path = MODELS_DIR / "feature_importance.csv"
    if not path.exists():
        raise HTTPException(404, "Feature importance missing")
    return json.loads(pd.read_csv(path).to_json(orient="records"))


@app.get("/api/model/risks")
def risks() -> list:
    return _read_csv("launch_risk_scores")


@app.post("/api/model/what-if")
def what_if(body: WhatIfBody) -> dict:
    row = body.model_dump()
    for c in FEATURE_COLS_NUM + FEATURE_COLS_CAT:
        if c not in row:
            raise HTTPException(400, f"Missing {c}")
    try:
        return score_what_if(row)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/api/pipeline/stages")
def stages() -> list:
    return PIPELINE_STAGES


@app.get("/api/pipeline/lineage")
def lineage() -> dict:
    nodes, edges = lineage_nodes_edges()
    return {"nodes": nodes, "edges": edges}


@app.get("/api/pipeline/artifacts")
def artifacts() -> list:
    inv = artifact_inventory()
    return json.loads(inv.to_json(orient="records"))


@app.post("/api/pipeline/run/{stage_id}")
def pipeline_run_stage(stage_id: str, body: StageBody | None = None) -> dict:
    seed = body.seed if body else 42
    result = run_stage(stage_id, seed=seed)
    return {
        "name": result.name,
        "ok": result.ok,
        "detail": result.detail,
        "elapsed_s": result.elapsed_s,
        "logs": result.logs,
    }


@app.post("/api/pipeline/run-all")
def pipeline_run_all(body: StageBody | None = None) -> dict:
    seed = body.seed if body else 42
    results = run_all_stages(seed=seed)
    return {
        "ok": all(r.ok for r in results),
        "results": [
            {
                "name": r.name,
                "ok": r.ok,
                "detail": r.detail,
                "elapsed_s": r.elapsed_s,
                "logs": r.logs,
            }
            for r in results
        ],
    }


@app.get("/api/exports")
def list_exports() -> list:
    DATA_EXPORTS.mkdir(parents=True, exist_ok=True)
    return [
        {"name": f.name, "kb": round(f.stat().st_size / 1024, 1)}
        for f in sorted(DATA_EXPORTS.glob("*"))
        if f.is_file()
    ]


@app.post("/api/exports/refresh")
def refresh_exports() -> dict:
    from gatepulse.report import export_all

    return export_all()


@app.get("/api/exports/download/{filename}")
def download_export(filename: str):
    path = DATA_EXPORTS / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(path, filename=filename)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")
