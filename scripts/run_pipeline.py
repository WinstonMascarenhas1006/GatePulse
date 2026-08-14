"""One-command GatePulse pipeline."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gatepulse.ai_risk import generate_insights, train_and_score  # noqa: E402
from gatepulse.config import DATA_PROCESSED, ROOT as PROJECT_ROOT  # noqa: E402
from gatepulse.etl import run_etl  # noqa: E402
from gatepulse.generate_data import generate_all  # noqa: E402
from gatepulse.quality import run_quality  # noqa: E402
from gatepulse.report import export_all  # noqa: E402


def main() -> None:
    started = datetime.now()
    print("=== GatePulse pipeline ===")
    print("[1/5] Generating synthetic NPI launch data...")
    tables = generate_all(seed=42)
    print("      ", {k: len(v) for k, v in tables.items()})

    print("[2/5] Running ETL + SQLite load...")
    etl_out = run_etl()
    print("      ", {k: len(v) for k, v in etl_out.items()})

    print("[3/5] Scoring data quality...")
    q_summary, _ = run_quality()
    print("      ", q_summary)

    print("[4/5] Training AI slip-risk model...")
    ai = train_and_score(seed=42)
    metrics = {k: ai["metrics"][k] for k in ("n_train", "n_test", "roc_auc", "positive_rate")}
    print("      ", metrics)

    print("[5/5] Exporting steering pack...")
    paths = export_all()
    print("      ", paths)

    import pandas as pd

    facts = pd.read_csv(DATA_PROCESSED / "launch_facts_scored.csv")
    risks = pd.read_csv(DATA_PROCESSED / "launch_risk_scores.csv")
    insights = generate_insights(risks, facts)
    run_meta = {
        "started": started.isoformat(timespec="seconds"),
        "finished": datetime.now().isoformat(timespec="seconds"),
        "row_counts": {k: len(v) for k, v in etl_out.items()},
        "quality": q_summary,
        "ai_metrics": metrics,
        "exports": paths,
        "insights": insights,
        "project_root": str(PROJECT_ROOT),
    }
    meta_path = DATA_PROCESSED / "last_pipeline_run.json"
    meta_path.write_text(json.dumps(run_meta, indent=2), encoding="utf-8")
    print("=== Done ===")
    print(f"Meta: {meta_path}")
    for line in insights:
        print(f"INSIGHT: {line}")


if __name__ == "__main__":
    main()
