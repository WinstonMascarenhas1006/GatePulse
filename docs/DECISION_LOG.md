# GatePulse — Decision & Change Log

**Product:** GatePulse (NPI / SOP Launch Readiness Intelligence)  
**Rule:** Log every decision, change, revision, micro-choice, and **idea source**.

---

## Idea sources registry (living)

| Source ID | Source | How it was used |
|-----------|--------|-----------------|
| S-USER-01 | User request (Aug 2026): build CV project for Mercedes trainee JD (data analysis & AI in vehicle certification) | Original skill targets only (analysis, dashboards, automation, AI, planning, QA) |
| S-USER-02 | User feedback (Aug 2026): exact JD-clone project would look AI-generated / tailored | **Primary reason for domain pivot** away from homologation KR/JP/AU |
| S-JD-01 | Public Mercedes-Benz careers posting MER00047F2 (skills themes, not process copy) | Extracted transferable skills; deliberately did **not** copy markets, department name, or certification workflow wording |
| S-PRIOR-01 | Earlier local scaffold `CertIQ-Homologation` (same session) | Reused technical pattern: generate→ETL→quality→ML→Streamlit→exports; discarded domain branding |
| S-MFG-01 | Public Stage-Gate / NPI practice (Cooper Stage-Gate concepts; general manufacturing launch gates) | Gate names & launch-readiness framing |
| S-MFG-02 | Common SOP (Start of Production) readiness checklists used in industry articles/training (generic, non-confidential) | Milestone chain: tooling, quality freeze, logistics, training, pilot build, SOP sign-off |
| S-BI-01 | Typical ops analytics dashboards (Power BI / Tableau gallery patterns: KPI strip, drill-down, risk heat) | Dashboard IA |
| S-ML-01 | Classic tabular risk classification (scikit-learn RandomForest tutorials / industry delay prediction patterns) | Offline delay-risk model without API keys |
| S-DQ-01 | Data-quality dimensions (completeness, validity, consistency) from general DQ literature | Dirty-data injection + cleaning rules |
| S-USER-04 | User: not satisfied with UI; change entire UI alignments | Full layout realignment D-025 |
| S-USER-03 | User request: make frontend and backend both visible in the frontend | Dual UI: Command deck + Engine Room / Data Lab / Model Lab |
| S-DESIGN-01 | User frontend rules (avoid purple/cream AI clichés; expressive fonts; atmospheric background) | Streamlit visual direction |

---

## Entries

### D-001 | 2026-08-16 | DECISION | Domain pivot (critical)
- **Choice:** Abandon CertIQ “vehicle homologation KR/JP/AU” product. Build **GatePulse** = New Product Introduction / Start-of-Production **launch readiness** analytics for a fictional industrial OEM.
- **Why:** S-USER-02 — a project that mirrors the JD domain word-for-word is easy to flag as generated-for-application. Launch readiness still proves the same skills without cloning certification/homologation.
- **Aligns with JD skills (indirect):** project planning & tracking, scheduling/progress, management reports, data QA, dashboards, process automation, AI scoring, international collab, Excel/BI toolchain mindset.
- **Does NOT copy:** Homologation Korea/Japan/Australia, type-approval authorities, certificate packages, Mercedes series names, department titles.
- **Sources:** S-USER-02, S-JD-01, S-MFG-01, S-MFG-02, S-PRIOR-01
- **Alternatives rejected:** (1) Keep CertIQ and only rename UI — still too close. (2) Random unrelated Kaggle clone — weak skill transfer. (3) Supplier audit-only tool — viable but less “planning + AI launch risk” story.

### D-002 | 2026-08-16 | DECISION | New product naming
- **Choice:** **GatePulse** — “NPI Launch Readiness Intelligence”
- **Why:** Neutral, memorable, suggests gates/milestones + live pulse/monitoring; no OEM trademark.
- **Sources:** Naming brainstorm guided by S-USER-02 constraint
- **Alternatives:** ReadyGate, LaunchIQ, SOP Watch — LaunchIQ rejected (too “AI product” sounding); SOP Watch too niche acronym-first.

### D-003 | 2026-08-16 | DECISION | Fictional company & plants
- **Choice:** Fictional OEM **Helion Industrial** (material-handling / light industrial equipment). Plants: **Leipzig (DE), Brno (CZ), Monterrey (MX), Penang (MY)**.
- **Why:** International network without copying Sindelfingen / KR-JP-AU certification geography from the JD.
- **Sources:** S-USER-02; geography chosen as common manufacturing hubs (public knowledge), not from the JD location list.
- **Alternatives:** Real OEM names — rejected (trademark / fake-experience risk). Tuscaloosa/Kecskemét set — rejected (too automotive-OEM coded).

### D-004 | 2026-08-16 | DECISION | Program catalog (synthetic)
- **Choice:** Fictional NPI programs: Atlas Conveyor Gen3, Orbit Sorter X, Nexus AGV Dock, Pulse Pack Station, Harbor Reach Truck, Vector Battery Mule.
- **Why:** Industrial equipment story supports “complex multi-gate launch” without sounding like car homologation.
- **Sources:** Invented for demo; pattern inspired by S-MFG-01 NPI programs.

### D-005 | 2026-08-16 | DECISION | Workstream catalog (not “regulations”)
- **Choice:** Launch workstreams with complexity scores: Tooling, Quality Freeze, Supplier Readiness, Logistics/Pack, Training, IT/MES Cutover, Pilot Build, HSE Sign-off, Cost Gate, Spare-Parts Setup.
- **Why:** Replaces certification requirement codes; still yields complexity features for ML.
- **Sources:** S-MFG-02 checklist themes (generic public practice), not JD requirement wording.

### D-006 | 2026-08-16 | DECISION | Milestone chain
- **Choice:** Concept freeze → Tooling release → Pilot build complete → Quality gate passed → Logistics ready → Training complete → SOP authorization.
- **Why:** Classic launch sequence; interview-explainable; maps to planning/progress JD skills without authority/certificate steps.
- **Sources:** S-MFG-01, S-MFG-02

### D-007 | 2026-08-16 | DECISION | Keep technical architecture
- **Choice:** Reuse proven pipeline shape from S-PRIOR-01: Python generate → ETL/SQLite → quality scores → RandomForest risk → Streamlit/Plotly → Excel/Markdown exports.
- **Why:** Already verified working; pivot is domain/product, not a rewrite of engineering for its own sake.
- **Sources:** S-PRIOR-01, S-ML-01, S-BI-01, S-DQ-01

### D-008 | 2026-08-16 | DECISION | New repository path
- **Choice:** `E:\project\GatePulse` (new git root). Do not keep shipping under folder name `CertIQ-Homologation`.
- **Why:** Folder/repo title alone would expose the old JD-clone framing on GitHub/CV links.
- **Sources:** S-USER-02

### D-009 | 2026-08-16 | MICRO | Package name
- **Choice:** Python package `gatepulse` (not `certiq`).
- **Why:** Consistency with product rename.
- **Sources:** D-002

### D-010 | 2026-08-16 | DECISION | CV positioning language
- **Choice:** Describe as “NPI / production launch readiness analytics for multi-plant industrial programs.” In interviews, if asked about automotive certification interest: explain **transfer** (gates, evidence, deadlines, data quality, international plants) — do not claim homologation experience you do not have.
- **Why:** Honest + still relevant to S-JD-01 skill themes.
- **Sources:** S-USER-02, S-JD-01

### D-011 | 2026-08-16 | MICRO | Logging continuation
- **Choice:** This file is the canonical log; every later edit appends D-0xx with sources.
- **Sources:** S-USER-01 logging rule (carried forward explicitly by user: “rules remain same… including source”)

### D-012 | 2026-08-16 | DECISION | Dirty-data QA demo retained
- **Choice:** Keep intentional invalid dates / null progress / typo statuses in generator, cleaned in ETL.
- **Why:** Proves data-quality skill without needing certification-domain examples.
- **Sources:** S-DQ-01, S-PRIOR-01 lesson

### D-013 | 2026-08-16 | MICRO | Guaranteed Blocked gates
- **Choice:** After generation, force up to 4 in-flight milestones to Blocked.
- **Why:** Learned from prior scaffold that sparse RNG can yield zero blocked rows (empty insight).
- **Sources:** S-PRIOR-01 (D-019 lesson)

### D-014 | 2026-08-16 | MICRO | Health & label thresholds
- **Choice:** Critical if blocked OR max slip ≥ 28 days; ML positive if delayed_milestones ≥ 2 OR max slip ≥ 21.
- **Why:** Carry forward balance/readability lessons from prior run.
- **Sources:** S-PRIOR-01

### D-015 | 2026-08-16 | DECISION | Visual identity
- **Choice:** Deep graphite + warm sand accents; Fraunces + Source Sans 3 (not Inter/Roboto; not purple gradient).
- **Why:** Distinct portfolio look; follows user design constraints.
- **Sources:** S-DESIGN-01

### D-016 | 2026-08-16 | DECISION | Docs package for applications
- **Choice:** README + charter + CV bullets + skill-transfer note + report outline + this log with source registry.
- **Why:** User needs report/CV material and explicit anti-clone rationale.
- **Sources:** S-USER-01, S-USER-02

### D-017 | 2026-08-16 | MICRO | Archive old repo
- **Choice:** Leave `E:\project\CertIQ-Homologation` as archived prior attempt; do not use it on CV.
- **Why:** Avoid accidental submission of the JD-clone version.
- **Sources:** S-USER-02

### D-018 | 2026-08-16 | CHANGE | Implementation complete for v1
- **Choice:** Shipped package `gatepulse`, Streamlit app, pipeline, tests, exports.
- **Sources:** S-PRIOR-01 engineering pattern adapted to D-001 domain

---

## Implementation chronology
1. Logged pivot + source registry (D-001…D-011)
2. Created `E:\project\GatePulse` git root; migrated agent workspace
3. Wrote config/domain constants (plants, programs, workstreams, gates)
4. Implemented generate → etl → quality → ai_risk → report
5. Built Streamlit UI + pipeline script + tests + docs
6. Verification run (append results after execute)

### D-019 | 2026-08-16 | DECISION | Verification gate passed
- **Choice:** Accept v1 after pipeline + pytest + Streamlit bind.
- **Results:** 16 launches, 112 milestones, 225 tasks, 7 quality issues; tests 3 passed; ROC-AUC on tiny holdout ≈ 0.44 (honestly weak — document small-N limitation rather than hide it); dashboard on port 8502.
- **Sources:** S-USER-01 success criteria; S-ML-01 honesty about metrics
- **Micro-note:** Low AUC is preferable to a fake “perfect model” story for interviews.

### D-020 | 2026-08-16 | DECISION | Frontend must expose backend
- **Choice:** Redesign Streamlit so the UI is both **command deck** (results) and **engine room** (pipeline, ETL, DQ, model internals runnable/visible).
- **Why:** User asked that front and back end both be visible in the frontend — a results-only BI page hides the real project.
- **Sources:** S-USER-03 (user message); S-BI-01 extended into “ops + platform” dual view; MLOps demo patterns (visible pipelines)
- **Pages planned:** Overview · Engine Room · Data Lab · Model Lab · Launches · Exports

### D-021 | 2026-08-16 | MICRO | Engine Room interaction
- **Choice:** Run each pipeline stage from the UI with a live log panel (not only CLI).
- **Why:** Makes backend callable and observable without leaving the browser.
- **Sources:** S-USER-03; Streamlit status/progress patterns

### D-022 | 2026-08-16 | MICRO | Data Lab + Model Lab
- **Choice:** Side-by-side raw vs cleaned rows; SQLite table browser; feature-importance chart; what-if slip-risk scorer using saved model.
- **Why:** Shows ETL and ML as first-class UI objects, not hidden scripts.
- **Sources:** S-DQ-01, S-ML-01, S-USER-03

### D-023 | 2026-08-16 | CHANGE | Engine Room UI shipped
- **Choice:** Added `gatepulse.engine` staged runner + rebuilt Streamlit with Overview / Engine Room / Data Lab / Model Lab / Launches / Exports; Sankey lineage; live terminal log; raw vs clean; SQLite browser; feature importance; what-if scorer.
- **Verification:** Pipeline OK; feature_importance.csv written; what-if returns scores; Streamlit on :8502.
- **Sources:** S-USER-03, D-020..D-022

### D-024 | 2026-08-16 | MICRO | Source registry add
- **Choice:** Register **S-USER-03** = user request to make frontend and backend both visible inside the frontend.
- **Impact:** Dual-layer navigation labels (“front” / “back”) in sidebar.

*End of dual-visibility UI session. Append D-025+ later.*

### D-028 | 2026-08-16 | REVISION | Fix stretched UI feel
- **Choice:** Tighten custom web layout: narrower content rail (960px), capped hero type, fixed chart stage heights with contain, denser KPI cells, stop full-bleed stretch on ultrawide.
- **Why:** User: “kind of weird stretched feels.”
- **Sources:** S-USER-06

### D-025 | 2026-08-16 | REVISION | Full UI realignment
- **Choice:** Replace streamlit layout/CSS with a new alignment system: fixed content max-width, brand hero strip, 12-col style section rhythm, left-rail stage strip in Engine Room, split panes with equal gutters, monospace meta row, fewer stacked cards.
- **Why:** User not satisfied with UI alignments; request full change.
- **Sources:** S-USER-04 (this message); S-DESIGN-01

### D-026 | 2026-08-16 | DECISION | Replace Streamlit as primary UI
- **Choice:** Abandon Streamlit-as-main-UI. Ship a custom HTML/CSS/JS control surface served by FastAPI, calling the same gatepulse backend.
- **Why:** User: "change entire project ui" — Streamlit restyles still felt like the same app.
- **Sources:** S-USER-05; S-USER-03; S-DESIGN-01
- **Visual direction:** Light technical studio (cool paper + ink + coral accent; Syne + Manrope) — deliberately unlike prior dark Streamlit skins.

### D-027 | 2026-08-16 | MICRO | Source registry
- **Choice:** Register S-USER-05 = demand for entire project UI replacement (not CSS tweaks).

### D-028 | 2026-08-16 | REVISION | Fix stretched UI feel
- **Choice:** Narrow content rail (~920px), smaller hero type, fixed chart stages, denser KPIs, centered shell.
- **Why:** User: weird stretched feels.
- **Sources:** S-USER-06


### D-029 | 2026-08-16 | REVISION | Fix empty/misaligned Deck from screenshot
- **Choice:** Rebuild shell to full-bleed edge-aligned layout: nav flush with content, hero as 2-col with live status panel filling right void, denser KPI+chart packing, wider usable rail (~1080px) without sparse emptiness.
- **Why:** User screenshot showed large empty right margin, left-only hero, centered nav vs left content mismatch.
- **Sources:** S-USER-07 (screenshot feedback)


### D-030 | 2026-08-16 | DECISION | First-time product tour
- **Choice:** Add Driver.js walkthrough (CDN) with spotlight, Next/Back/Skip/Finish, progress, Escape, localStorage gatepulse_tour_v1, and Restart tour control.
- **Why:** Beginners would not know how to navigate Deck/Engine/Data/Model.
- **Sources:** S-USER-08 (onboarding tour spec)

