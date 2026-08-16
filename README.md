# GatePulse

**NPI / SOP launch readiness intelligence** for a fictional industrial OEM (Helion Industrial).

Working portfolio project: synthetic multi-plant launch data → ETL + data-quality checks → interactive dashboards → offline AI slip-risk scoring → steering exports.

## Plain-English what it does
Factories launching new products need gate reviews (tooling ready? pilot build done? training done?). GatePulse tracks those launches across plants, cleans messy checklist data, shows managers what’s at risk, and scores which launches may miss SOP.

**The UI shows both layers:**
- **Command deck** (Overview / Launches) = manager frontend
- **Engine Room / Data Lab / Model Lab** = backend pipeline, ETL X-ray, SQLite, model feature importance, what-if scoring — all runnable from the browser

**First-time tour:** Driver.js walkthrough auto-starts once (spotlight + Next/Back/Skip). Replay anytime via **Take tour** in the header. Completion is stored in `localStorage` (`gatepulse_tour_v1`).


## Why this domain (important)
An earlier idea mirrored a specific automotive *certification* job posting too closely. That risks looking application-generated. GatePulse keeps the **same analytical skills** (planning data, QA, dashboards, automation, AI prioritization, international ops) but in a **different story**: industrial NPI launch readiness — not type approval / homologation.

See `docs/DECISION_LOG.md` (sources S-USER-02, S-JD-01) and `docs/SKILL_TRANSFER.md`.

## Quick start (custom UI — primary)
```powershell
cd E:\project\GatePulse
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts\run_pipeline.py
uvicorn app.api:app --reload --port 8080
```
Open **http://localhost:8080** — this is the real UI (HTML/CSS/JS on FastAPI), not Streamlit.

Optional legacy Streamlit skin: `streamlit run app/streamlit_app.py` (kept only for history).

## Layout
```
app/api.py              # FastAPI (primary UI server)
app/web/                # Custom HTML/CSS/JS UI
app/streamlit_app.py    # Legacy only
src/gatepulse/          # backend: generate, etl, quality, ai_risk, report, engine
scripts/run_pipeline.py
data/ raw | processed | exports
docs/
tests/
```

## License
MIT — portfolio / demo use. Fictional company and data only.
