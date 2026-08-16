<p align="center">
  <img src="docs/assets/gatepulse-banner.png" alt="GatePulse — launch readiness control surface" width="100%" />
</p>

<p align="center">
  <strong>GATEPULSE</strong><br/>
  <em>See the launch. Trust the pipeline.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/stack-Python%20·%20FastAPI%20·%20sklearn-E8452D?style=flat-square&labelColor=101820" alt="stack" />
  <img src="https://img.shields.io/badge/data-100%25%20synthetic-101820?style=flat-square&labelColor=E8452D" alt="synthetic" />
  <img src="https://img.shields.io/badge/UI-Deck%20%2B%20Engine%20under%20glass-101820?style=flat-square" alt="ui" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="license" />
</p>

---

## The map

Four plants. One pulse.

<p align="center">
  <img src="docs/assets/gatepulse-plants.png" alt="Helion plant network: Leipzig, Brno, Monterrey, Penang" width="920" />
</p>

| Code | Plant | Role in the demo |
|:----:|:------|:-----------------|
| **LEJ** | Leipzig | EU launch office gravity |
| **BRQ** | Brno | Supplier / pilot pressure |
| **MTY** | Monterrey | Americas cutover heat |
| **PEN** | Penang | APAC logistics & MES |

Everything on this map is fictional. The coordination problem is not.

---

## The nerve

<p align="center">
  <img src="docs/assets/gatepulse-pipeline.png" alt="GatePulse pipeline: RAW → WASH → STORE → SCORE → RISK → DECK" width="920" />
</p>

```text
 RAW checklists ──► ETL wash ──► SQLite
                         │
                         ▼
                   launch facts ──► quality score
                         │               │
                         └────► slip-risk model ──► Deck / labs / Excel
```

| Stage | You feel it as… |
|:-----:|:----------------|
| **RAW** | Messy milestone CSVs (bad dates, missing %, typo statuses) |
| **WASH** | Cleaner that repairs + logs every fix |
| **STORE** | SQLite you can browse in **Data** |
| **SCORE** | Portfolio quality index |
| **RISK** | Offline RandomForest SOP-slip score |
| **DECK** | Browser glass — charts, insights, exports |

---

## The glass (UI rooms)

```text
┌────────┬──────────────────────────────────────────────┐
│  GP    │  Deck   Engine   Data   Model   Launches …   │
│  rail  ├──────────────────────────────────────────────┤
│        │                                              │
│        │   ┌──────────────┐  ┌─────────────────────┐  │
│        │   │  headline    │  │  dark KPI pulse     │  │
│        │   └──────────────┘  └─────────────────────┘  │
│        │   ┌────────────────┐ ┌──────────────────┐    │
│        │   │ plant health   │ │ AI read-out      │    │
│        │   └────────────────┘ └──────────────────┘    │
│        │                                              │
└────────┴──────────────────────────────────────────────┘
         ▲                              ▲
    brand spine                   command canvas
```

| Open this | Look for this |
|:----------|:--------------|
| **Deck** | KPIs · plant bars · AI tips · scatter risk map |
| **Engine** | Stage buttons · live terminal · artifact list |
| **Data** | RAW ‖ CLEAN split · SQLite · quality pie |
| **Model** | Holdout metrics · feature bars · what-if levers |
| **Launches** | One program → gate bars → tasks |
| **Exports** | Excel + Markdown steering pack |

> First visit gets a **spotlight tour**.  
> Missed it? Top-right → **Take tour**. Esc closes.

---

## Ignition

<p align="center">

| ① | ② | ③ | ④ | ⑤ |
|:-:|:-:|:-:|:-:|:-:|
| clone | venv | pip | pipeline | open glass |

</p>

```powershell
git clone https://github.com/WinstonMascarenhas1006/GatePulse.git
cd GatePulse
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts\run_pipeline.py
uvicorn app.api:app --reload --port 8080
```

<p align="center"><strong>→ http://localhost:8080</strong></p>

Demo choreography (90 seconds):

```text
Engine  →  Run full pipeline  →  watch terminal
   ↓
Deck    →  KPIs refresh
   ↓
Data    →  RAW vs CLEAN
   ↓
Model   →  move a slider → Score
```

---

## System sketch

```mermaid
flowchart TB
  subgraph FACE["FACE · app/web"]
    D[Deck]
    E[Engine]
    L[Data / Model / Launches]
  end

  subgraph NERVE["NERVE · app/api.py"]
    API[FastAPI]
  end

  subgraph BRAIN["BRAIN · src/gatepulse"]
    G[generate]
    T[etl]
    Q[quality]
    A[ai_risk]
    R[report]
  end

  D --> API
  E --> API
  L --> API
  API --> G & T & Q & A & R
  G --> T --> Q --> A --> R
```

```text
app/web/           face
app/api.py         nerve
src/gatepulse/     brain
scripts/           ignition keys
docs/assets/       pictures for this page
docs/              decisions · CV · transfer notes
tests/             smoke alarms
```

---

## AI without the fog machine

```text
features ──► RandomForest ──► score 0–100 ──► High / Medium / Low
                    │
                    ├── feature importance chart
                    └── what-if scorer (Model room)
```

Runs offline. No API key. Small-N metrics stay honest on screen.

---

## Why this story exists

Skills practiced: planning data · checklist QA · automation · dashboards · AI prioritization · multi-plant ops.

Story chosen: **NPI / SOP launch readiness** — not a photocopy of any single certification job ad.

Careful interview wording → [`docs/SKILL_TRANSFER.md`](docs/SKILL_TRANSFER.md)  
Build memory → [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md)  
CV lines → [`docs/CV_BULLETS.md`](docs/CV_BULLETS.md)

---

<p align="center">
  <img src="docs/assets/gatepulse-banner.png" alt="" width="60%" />
</p>

<p align="center">
  <sub>MIT · Helion Industrial is fictional · synthetic data only</sub><br/>
  <b>See the launch.</b> <i>Trust the pipeline.</i>
</p>
