"""
Shared paths and constants for GatePulse.
D-031: remapped to Northbridge Academies (four campuses), not industrial plants.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_EXPORTS = ROOT / "data" / "exports"
MODELS_DIR = ROOT / "models"
DB_PATH = DATA_PROCESSED / "gatepulse.db"

# Fictional school group
CAMPUSES = {
    "RIV": {
        "name": "Riverside Campus",
        "country": "Germany",
        "region": "City",
        "timezone": "Europe/Berlin",
    },
    "HIL": {
        "name": "Hillcrest Campus",
        "country": "Germany",
        "region": "Suburban",
        "timezone": "Europe/Berlin",
    },
    "HAR": {
        "name": "Harbour Campus",
        "country": "Germany",
        "region": "Coastal",
        "timezone": "Europe/Berlin",
    },
    "OAK": {
        "name": "Oakwood Campus",
        "country": "Germany",
        "region": "Rural",
        "timezone": "Europe/Berlin",
    },
}

PROGRAMS = [
    {"program_id": "TERM-AUT", "name": "Autumn term start", "family": "Curriculum", "power_class": "Secondary"},
    {"program_id": "MOCK-26", "name": "Mock exam series", "family": "Exams", "power_class": "Secondary"},
    {"program_id": "PUB-EX", "name": "Public exam administration", "family": "Exams", "power_class": "Secondary"},
    {"program_id": "INSP-27", "name": "Inspection evidence pack", "family": "Inspection", "power_class": "Primary"},
    {"program_id": "SEND-R", "name": "SEND provision review", "family": "Pastoral", "power_class": "Primary"},
    {"program_id": "RPT-CY", "name": "Parent reporting cycle", "family": "Curriculum", "power_class": "Primary"},
]

WORKSTREAMS = [
    {"ws_code": "TIME", "domain": "Timetabling", "complexity": 4, "typical_days": 40},
    {"ws_code": "STAFF", "domain": "Staffing / cover", "complexity": 5, "typical_days": 35},
    {"ws_code": "PAPER", "domain": "Assessment papers", "complexity": 5, "typical_days": 45},
    {"ws_code": "INVIG", "domain": "Invigilation roster", "complexity": 3, "typical_days": 25},
    {"ws_code": "SEND", "domain": "SEND access arrangements", "complexity": 4, "typical_days": 30},
    {"ws_code": "ITDEV", "domain": "Devices / school MIS", "complexity": 5, "typical_days": 40},
    {"ws_code": "SAFE", "domain": "Safeguarding sign-off", "complexity": 4, "typical_days": 20},
    {"ws_code": "FAC", "domain": "Facilities / rooms", "complexity": 3, "typical_days": 22},
    {"ws_code": "COMMS", "domain": "Parent communications", "complexity": 2, "typical_days": 15},
    {"ws_code": "RES", "domain": "Results processing", "complexity": 4, "typical_days": 28},
]

MILESTONE_TYPES = [
    "Exam / term plan agreed",
    "Teachers and invigilators confirmed",
    "Exam papers and teaching packs ready",
    "Hall rehearsal complete",
    "SLT quality check passed",
    "Parents notified",
    "Exam day / term start",
]

STATUSES = ["Not started", "In progress", "Blocked", "Completed", "Delayed"]
