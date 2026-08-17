"""
AI SOP-slip risk model.
Sources: S-ML-01 (RandomForest tabular risk), S-PRIOR-01 label lessons (tightened positive class).
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from gatepulse.config import DATA_PROCESSED, MODELS_DIR

FEATURE_COLS_NUM = [
    "avg_complexity",
    "max_complexity",
    "workstream_count",
    "open_tasks",
    "blocked_tasks",
    "open_milestones",
    "blocked_milestones",
    "avg_slip_days",
    "quality_score",
    "effort_hours",
]
FEATURE_COLS_CAT = ["campus_code", "priority", "power_class", "family"]
TARGET = "slip_risk"


def _build_training_frame(facts: pd.DataFrame, quality: pd.DataFrame) -> pd.DataFrame:
    df = facts.merge(quality, on="launch_id", how="left")
    df["quality_score"] = df["quality_score"].fillna(90)
    df[TARGET] = ((df["delayed_milestones"] >= 2) | (df["max_slip_days"] >= 21)).astype(int)
    for c in FEATURE_COLS_NUM:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def train_and_score(seed: int = 42) -> dict:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    facts = pd.read_csv(DATA_PROCESSED / "launch_facts.csv")
    q = pd.read_csv(DATA_PROCESSED / "quality_by_launch.csv")
    df = _build_training_frame(facts, q)

    X = df[FEATURE_COLS_NUM + FEATURE_COLS_CAT]
    y = df[TARGET]
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.35, random_state=seed, stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.35, random_state=seed
        )

    pre = ColumnTransformer(
        [
            ("num", "passthrough", FEATURE_COLS_NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURE_COLS_CAT),
        ]
    )
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=2,
        random_state=seed,
        class_weight="balanced",
    )
    pipe = Pipeline([("pre", pre), ("clf", clf)])
    pipe.fit(X_train, y_train)

    proba_test = pipe.predict_proba(X_test)[:, 1]
    preds_test = (proba_test >= 0.5).astype(int)
    metrics = {
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positive_rate": float(y.mean()),
        "report": classification_report(y_test, preds_test, output_dict=True, zero_division=0),
    }
    try:
        metrics["roc_auc"] = float(roc_auc_score(y_test, proba_test))
    except ValueError:
        metrics["roc_auc"] = None

    all_proba = pipe.predict_proba(X)[:, 1]
    scored = df[
        ["launch_id", "launch_name", "campus_code", "program_id", "priority", "health"]
    ].copy()
    scored["slip_risk_proba"] = np.round(all_proba, 4)
    scored["slip_risk_score"] = (all_proba * 100).round(1)
    scored["slip_risk_label"] = np.where(
        scored["slip_risk_score"] >= 70,
        "High",
        np.where(scored["slip_risk_score"] >= 40, "Medium", "Low"),
    )
    scored["slip_risk_actual"] = y.values

    joblib.dump(pipe, MODELS_DIR / "slip_risk_model.joblib")
    scored.to_csv(DATA_PROCESSED / "launch_risk_scores.csv", index=False)

    # Feature importance for Model Lab UI (D-022)
    try:
        ohe = pipe.named_steps["pre"].named_transformers_["cat"]
        cat_names = list(ohe.get_feature_names_out(FEATURE_COLS_CAT))
        feat_names = FEATURE_COLS_NUM + cat_names
        importances = pipe.named_steps["clf"].feature_importances_
        fi = (
            pd.DataFrame({"feature": feat_names, "importance": importances})
            .sort_values("importance", ascending=False)
            .head(20)
        )
        fi.to_csv(MODELS_DIR / "feature_importance.csv", index=False)
        metrics["top_features"] = fi.head(8).to_dict(orient="records")
    except Exception as exc:  # noqa: BLE001 — UI-facing best effort
        metrics["feature_importance_error"] = str(exc)

    (MODELS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    enriched = facts.merge(
        scored[["launch_id", "slip_risk_score", "slip_risk_label", "slip_risk_proba"]],
        on="launch_id",
        how="left",
    ).merge(q, on="launch_id", how="left")
    enriched.to_csv(DATA_PROCESSED / "launch_facts_scored.csv", index=False)
    return {"metrics": metrics, "scored": scored, "model": pipe}


def score_what_if(row: dict) -> dict:
    """Score a single synthetic launch dict with the saved model (Model Lab)."""
    path = MODELS_DIR / "slip_risk_model.joblib"
    if not path.exists():
        raise FileNotFoundError("Model missing. Run pipeline / Engine Room train step first.")
    pipe = joblib.load(path)
    frame = pd.DataFrame([row])[FEATURE_COLS_NUM + FEATURE_COLS_CAT]
    proba = float(pipe.predict_proba(frame)[0, 1])
    score = round(proba * 100, 1)
    label = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    return {"slip_risk_proba": round(proba, 4), "slip_risk_score": score, "slip_risk_label": label}


def generate_insights(scored: pd.DataFrame, facts: pd.DataFrame) -> list[str]:
    insights = []
    high = scored[scored["slip_risk_label"] == "High"]
    if len(high):
        top = high.sort_values("slip_risk_score", ascending=False).iloc[0]
        insights.append(
            f"Highest deadline-slip risk: {top['launch_name']} "
            f"(score {top['slip_risk_score']:.0f}/100, campus {top['campus_code']})."
        )
    by_campus = scored.groupby("campus_code")["slip_risk_score"].mean().sort_values(ascending=False)
    if len(by_campus):
        insights.append(
            f"Campus with highest average slip risk: {by_campus.index[0]} "
            f"({by_campus.iloc[0]:.1f}/100). Review exams-office capacity there."
        )
    insights.append(
        f"{int((facts['health'] == 'Critical').sum())} programme(s) marked Critical on operational health."
    )
    insights.append(
        f"{int(facts['blocked_milestones'].sum())} blocked gate(s) across campuses "
        "- candidates for process automation."
    )
    if "quality_score" in facts.columns:
        weak = facts[facts["quality_score"] < 80]
        insights.append(
            f"{len(weak)} programme(s) below data-quality threshold (80). "
            "Clean checklist data before SLT."
        )
    return insights


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    out = train_and_score()
    print(
        json.dumps(
            {k: out["metrics"][k] for k in ("n_train", "n_test", "roc_auc", "positive_rate")},
            indent=2,
        )
    )
