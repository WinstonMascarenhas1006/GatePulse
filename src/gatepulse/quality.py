"""Data quality scoring. Source: S-DQ-01."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from gatepulse.config import DATA_PROCESSED

RULE_WEIGHTS = {
    "invalid_date": 12,
    "missing_value": 8,
    "invalid_category": 10,
}


def score_quality(quality_issues: pd.DataFrame, milestones: pd.DataFrame) -> dict:
    n = max(len(milestones), 1)
    penalty = 0
    if len(quality_issues):
        for issue_type, w in RULE_WEIGHTS.items():
            penalty += int((quality_issues["issue_type"] == issue_type).sum()) * w
    overall = max(0, 100 - int(penalty / n * 100))

    per_launch = []
    if len(quality_issues):
        joined = quality_issues.merge(
            milestones[["milestone_id", "launch_id"]],
            left_on="record_id",
            right_on="milestone_id",
            how="left",
        )
        for lid, grp in milestones.groupby("launch_id"):
            iss = joined[joined["launch_id"] == lid]
            p = 0
            for issue_type, w in RULE_WEIGHTS.items():
                p += int((iss["issue_type"] == issue_type).sum()) * w
            per_launch.append(
                {"launch_id": lid, "quality_score": max(0, 100 - p * 5), "issue_count": len(iss)}
            )
    else:
        for lid in milestones["launch_id"].unique():
            per_launch.append({"launch_id": lid, "quality_score": 100, "issue_count": 0})

    summary = {
        "overall_quality_score": overall,
        "issue_count": len(quality_issues),
        "milestone_rows": len(milestones),
        "issues_by_type": quality_issues["issue_type"].value_counts().to_dict()
        if len(quality_issues)
        else {},
    }
    return {"summary": summary, "per_launch": pd.DataFrame(per_launch)}


def run_quality() -> tuple[dict, pd.DataFrame]:
    issues = pd.read_csv(DATA_PROCESSED / "quality_issues.csv")
    milestones = pd.read_csv(DATA_PROCESSED / "milestones.csv")
    result = score_quality(issues, milestones)
    result["per_launch"].to_csv(DATA_PROCESSED / "quality_by_launch.csv", index=False)
    return result["summary"], result["per_launch"]


if __name__ == "__main__":
    import json
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    summary, _ = run_quality()
    print(json.dumps(summary, indent=2))
