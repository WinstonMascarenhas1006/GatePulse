"""
Shared paths and constants for GatePulse.
Decisions: D-003 plants, D-004 programs, D-005 workstreams, D-006 milestones.
Sources: S-MFG-01, S-MFG-02, S-USER-02.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_EXPORTS = ROOT / "data" / "exports"
MODELS_DIR = ROOT / "models"
DB_PATH = DATA_PROCESSED / "gatepulse.db"

# Fictional OEM plants (not JD markets)
PLANTS = {
    "LEJ": {"name": "Leipzig", "country": "Germany", "region": "EU", "timezone": "Europe/Berlin"},
    "BRQ": {"name": "Brno", "country": "Czechia", "region": "EU", "timezone": "Europe/Prague"},
    "MTY": {"name": "Monterrey", "country": "Mexico", "region": "Americas", "timezone": "America/Monterrey"},
    "PEN": {"name": "Penang", "country": "Malaysia", "region": "APAC", "timezone": "Asia/Kuala_Lumpur"},
}

PROGRAMS = [
    {"program_id": "ATL-G3", "name": "Atlas Conveyor Gen3", "family": "Conveyor", "power_class": "AC"},
    {"program_id": "ORB-X", "name": "Orbit Sorter X", "family": "Sortation", "power_class": "AC"},
    {"program_id": "NX-AGV", "name": "Nexus AGV Dock", "family": "AGV", "power_class": "DC"},
    {"program_id": "PLS-PK", "name": "Pulse Pack Station", "family": "Packaging", "power_class": "AC"},
    {"program_id": "HBR-RT", "name": "Harbor Reach Truck", "family": "Lift", "power_class": "DC"},
    {"program_id": "VCT-BM", "name": "Vector Battery Mule", "family": "AGV", "power_class": "DC"},
]

# Launch workstreams (complexity drives ML features) — not regulatory codes
WORKSTREAMS = [
    {"ws_code": "TOOL", "domain": "Tooling", "complexity": 4, "typical_days": 60},
    {"ws_code": "QFREEZE", "domain": "Quality Freeze", "complexity": 5, "typical_days": 45},
    {"ws_code": "SUPPLY", "domain": "Supplier Readiness", "complexity": 4, "typical_days": 50},
    {"ws_code": "LOG", "domain": "Logistics / Pack", "complexity": 3, "typical_days": 35},
    {"ws_code": "TRAIN", "domain": "Operator Training", "complexity": 2, "typical_days": 25},
    {"ws_code": "MES", "domain": "IT / MES Cutover", "complexity": 5, "typical_days": 55},
    {"ws_code": "PILOT", "domain": "Pilot Build", "complexity": 5, "typical_days": 40},
    {"ws_code": "HSE", "domain": "HSE Sign-off", "complexity": 3, "typical_days": 20},
    {"ws_code": "COST", "domain": "Cost Gate", "complexity": 3, "typical_days": 30},
    {"ws_code": "SPARES", "domain": "Spare-Parts Setup", "complexity": 2, "typical_days": 22},
]

MILESTONE_TYPES = [
    "Concept freeze",
    "Tooling release",
    "Pilot build complete",
    "Quality gate passed",
    "Logistics ready",
    "Training complete",
    "SOP authorization",
]

STATUSES = ["Not started", "In progress", "Blocked", "Completed", "Delayed"]
