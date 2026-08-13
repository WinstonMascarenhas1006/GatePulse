"""
Synthetic NPI launch-readiness dataset.
Sources: S-MFG-01/02 (gate concepts), S-DQ-01 (dirty rows), S-PRIOR-01 (generator pattern).
Decisions: D-003..D-006, D-014-style dirty data carried as D-012.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from gatepulse.config import (
    DATA_RAW,
    MILESTONE_TYPES,
    PLANTS,
    PROGRAMS,
    STATUSES,
    WORKSTREAMS,
)


def _rng(seed: int = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def generate_all(seed: int = 42, as_of: datetime | None = None) -> dict[str, pd.DataFrame]:
    as_of = as_of or datetime(2026, 8, 16)
    rng = _rng(seed)
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    plants = pd.DataFrame([{"plant_code": k, **v} for k, v in PLANTS.items()])
    programs = pd.DataFrame(PROGRAMS)
    workstreams = pd.DataFrame(WORKSTREAMS)

    # Each program launches at 2-4 plants
    launch_rows = []
    lid = 2000
    planners = ["E. Novak", "R. Mendoza", "A. Lim", "T. Berger", "S. Kowalski", "N. Hassan"]
    for p in PROGRAMS:
        n_plants = int(rng.integers(2, 5))
        chosen_plants = list(rng.choice(list(PLANTS.keys()), size=n_plants, replace=False))
        for plant in chosen_plants:
            lid += 1
            sop = as_of + timedelta(days=int(rng.integers(60, 400)))
            launch_rows.append(
                {
                    "launch_id": f"L-{lid}",
                    "program_id": p["program_id"],
                    "plant_code": plant,
                    "launch_name": f"{p['name']} @ {PLANTS[plant]['name']}",
                    "planner": rng.choice(planners),
                    "priority": rng.choice(["P1", "P2", "P3"], p=[0.30, 0.50, 0.20]),
                    "sop_target": sop.date().isoformat(),
                    "created_on": (as_of - timedelta(days=int(rng.integers(20, 180)))).date().isoformat(),
                }
            )
    launches = pd.DataFrame(launch_rows)

    plant_ws_bias = {
        "LEJ": ["TOOL", "QFREEZE", "MES", "PILOT", "COST", "TRAIN"],
        "BRQ": ["SUPPLY", "LOG", "PILOT", "HSE", "SPARES", "TRAIN"],
        "MTY": ["TOOL", "SUPPLY", "LOG", "QFREEZE", "TRAIN", "HSE"],
        "PEN": ["MES", "SPARES", "LOG", "COST", "PILOT", "SUPPLY"],
    }
    dc_extra = ["MES", "HSE"]

    launch_ws = []
    milestones = []
    tasks = []
    mid = 6000
    tid = 9000

    for _, launch in launches.iterrows():
        prog = programs.loc[programs["program_id"] == launch["program_id"]].iloc[0]
        base = list(plant_ws_bias[launch["plant_code"]])
        if prog["power_class"] == "DC":
            base = list(dict.fromkeys(base + dc_extra))
        n_ws = int(rng.integers(4, min(8, len(base) + 1)))
        chosen = list(rng.choice(base, size=n_ws, replace=False))

        ws_meta = workstreams[workstreams["ws_code"].isin(chosen)]
        avg_complexity = float(ws_meta["complexity"].mean()) if len(ws_meta) else 3.0
        base_slip_prob = min(0.55, 0.08 * avg_complexity + (0.10 if launch["priority"] == "P1" else 0.04))

        for code in chosen:
            launch_ws.append(
                {
                    "launch_id": launch["launch_id"],
                    "ws_code": code,
                    "mandatory": True,
                    "owner_team": rng.choice(
                        ["Launch Office", "Manufacturing Eng", "Quality", "Logistics", "IT"]
                    ),
                }
            )

        cursor = datetime.fromisoformat(launch["created_on"]) + timedelta(days=5)
        for i, mtype in enumerate(MILESTONE_TYPES):
            mid += 1
            planned = cursor + timedelta(days=int(rng.integers(8, 26)))
            will_slip = rng.random() < base_slip_prob
            slip_days = int(rng.integers(5, 35)) if will_slip else int(rng.integers(0, 4))
            actual = planned + timedelta(days=slip_days)

            if actual.date() > as_of.date():
                if planned.date() > as_of.date():
                    status = "Not started"
                    actual_out = None
                    progress = 0
                else:
                    status = "Delayed" if slip_days >= 14 and will_slip else "In progress"
                    actual_out = None
                    progress = int(rng.integers(15, 85))
            else:
                status = "Completed"
                actual_out = actual.date().isoformat()
                progress = 100

            if status in ("In progress", "Delayed") and rng.random() < 0.10:
                status = "Blocked"

            milestones.append(
                {
                    "milestone_id": f"M-{mid}",
                    "launch_id": launch["launch_id"],
                    "sequence": i + 1,
                    "milestone_type": mtype,
                    "planned_date": planned.date().isoformat(),
                    "actual_date": actual_out,
                    "status": status,
                    "progress_pct": progress,
                    "slip_days": slip_days if status != "Not started" else 0,
                    "is_delayed_flag": int(slip_days >= 14 and status != "Not started"),
                }
            )
            cursor = planned

            for _ in range(int(rng.integers(1, 4))):
                tid += 1
                t_status = rng.choice(STATUSES, p=[0.15, 0.35, 0.08, 0.32, 0.10])
                if status == "Completed":
                    t_status = "Completed"
                elif status == "Not started":
                    t_status = "Not started"
                tasks.append(
                    {
                        "task_id": f"T-{tid}",
                        "milestone_id": f"M-{mid}",
                        "launch_id": launch["launch_id"],
                        "task_name": rng.choice(
                            [
                                "Update launch checklist",
                                "Confirm supplier capacity",
                                "Align plant steering deck",
                                "Close open quality findings",
                                "Book pilot-build slot",
                                "Validate MES master data",
                                "Translate work instructions",
                                "Prepare gate review slides",
                            ]
                        ),
                        "assignee": rng.choice(planners + ["Extern"]),
                        "status": t_status,
                        "due_date": (planned + timedelta(days=int(rng.integers(-5, 10)))).date().isoformat(),
                        "effort_hours": int(rng.integers(2, 24)),
                    }
                )

    launch_workstreams = pd.DataFrame(launch_ws)
    milestones_df = pd.DataFrame(milestones)
    tasks_df = pd.DataFrame(tasks)

    # Guarantee visible Blocked cohort (lesson from prior scaffold D-019)
    blockable = milestones_df.index[milestones_df["status"].isin(["In progress", "Delayed"])]
    if len(blockable):
        n_block = min(4, len(blockable))
        chosen_block = rng.choice(blockable, size=n_block, replace=False)
        milestones_df.loc[chosen_block, "status"] = "Blocked"

    # Intentional dirty rows for QA demo (S-DQ-01)
    dirty_idx = rng.choice(len(milestones_df), size=max(3, len(milestones_df) // 16), replace=False)
    milestones_df = milestones_df.copy()
    for i in dirty_idx:
        kind = rng.choice(["null_progress", "bad_date", "orphan_status"])
        if kind == "null_progress":
            milestones_df.loc[milestones_df.index[i], "progress_pct"] = np.nan
        elif kind == "bad_date":
            milestones_df.loc[milestones_df.index[i], "planned_date"] = "2026-99-99"
        else:
            milestones_df.loc[milestones_df.index[i], "status"] = "Unkown"

    tables = {
        "plants": plants,
        "programs": programs,
        "workstreams": workstreams,
        "launches": launches,
        "launch_workstreams": launch_workstreams,
        "milestones": milestones_df,
        "tasks": tasks_df,
    }
    for name, df in tables.items():
        df.to_csv(DATA_RAW / f"{name}.csv", index=False)

    meta = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "as_of": as_of.date().isoformat(),
        "seed": seed,
        "row_counts": {k: len(v) for k, v in tables.items()},
        "notes": "Synthetic GatePulse data for Helion Industrial demo. Fictional OEM.",
    }
    (DATA_RAW / "generation_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return tables


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    out = generate_all()
    for k, v in out.items():
        print(f"{k}: {len(v)} rows")
