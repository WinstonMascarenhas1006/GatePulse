# FIELD MANUAL GP–01  
### Recovered from Helion Industrial · Launch Office · Drawer C

---

Someone left this binder open on the Monterrey shift desk.

Inside: how a fictional factory network stops guessing whether a new product will actually hit **Start of Production** — and how you can boot the same machine on your laptop.

You are holding **GatePulse**.

---

## Before the software, a scene

Tuesday. Gate 4 (“Pilot build complete”) is green in one spreadsheet and amber in another.  
Training slides say “done.” The trainer is on leave. MES cutover is “90%.” Nobody agrees what 90% means.

The steering call starts in nine minutes.

GatePulse exists for that exact nine minutes: one pulse for **progress**, **blockers**, **data lies**, and **slip risk** — across Leipzig, Brno, Monterrey, and Penang.

All programs are invented. All rows are synthetic. The panic is realistic.

---

## What you are actually installing

Not a slide deck.  
Not a notebook graveyard.

A small industrial nervous system:

1. Invent a plant’s worth of launch chaos  
2. Wash it until the dates stop being nonsense  
3. Score how dirty the checklist still is  
4. Ask a quiet RandomForest which launches will slip  
5. Serve everything through a custom glass UI that can **re-run the backend live**

The face of the product is a browser.  
The heart is Python.  
They are not strangers — open **Engine** and you’ll see the heart beat.

---

## Boot sequence (do this in order)

```text
clone  →  venv  →  pip  →  pipeline  →  uvicorn  →  browser
```

```powershell
git clone https://github.com/WinstonMascarenhas1006/GatePulse.git
cd GatePulse
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts\run_pipeline.py
uvicorn app.api:app --reload --port 8080
```

Then walk into the room:

**http://localhost:8080**

A guided spotlight will try to introduce itself once.  
If you wave it away, the button **Take tour** brings it back. Escape always works.

---

## Rooms in the building

Walk the corridor like a new hire on day one.

| Door | What happens when you open it |
|------|-------------------------------|
| **Deck** | The quiet boardroom view — KPIs, plant posture, AI mutterings |
| **Engine** | The basement. Buttons that call real pipeline stages. A black terminal that does not flatter you |
| **Data** | Evidence locker. RAW on the left, CLEANED on the right. SQLite if you are nosy |
| **Model** | The oracle’s desk. Feature importance. Sliders. “What if we block two more gates?” |
| **Launches** | One program at a time — gates as a bar horizon, tasks underneath |
| **Exports** | Paper for humans who still live in Excel |

`BE` on a door means: this room shows the backend on purpose.

---

## How the machine thinks (no mythology)

```text
RAW CSVs
   │
   ▼
 ETL wash  ──►  SQLite shelf
   │
   ▼
 launch facts  ──►  quality score
   │                    │
   └──────────►  slip-risk model
                        │
                        ▼
              Deck · labs · Excel brief
```

Training happens on your machine. No cloud key. No rented genius.  
If the holdout score looks awkward, that is the dataset being small — the product does not cosplay as omniscient.

---

## Folder as floor plan

```text
app/web/          glass & switches
app/api.py        the hallway that connects glass to brain
src/gatepulse/    invent · wash · judge · predict · print
scripts/          the ignition key (run_pipeline.py)
docs/             why this exists, and every decision we refused to forget
tests/            the cheap smoke alarms
```

---

## Why Helion, not “a famous car brand’s homework”

This project practices planning analytics, checklist quality, automation, dashboards, and AI prioritization.

It refuses to cosplay as a photocopy of any one employer’s certification desk.  
If an interviewer asks “why launch readiness?” — answer with transfer, not theatre.  
See `docs/SKILL_TRANSFER.md` when you need the careful version.

The long memory of the build lives in `docs/DECISION_LOG.md`.

---

## License plate

MIT.  
Helion Industrial is a ghost company invented for learning.  
No confidential OEM blood was used in these tables.

---

*Close the binder.*  
*Open the Engine.*  
*Run the pipeline.*  
*Then look at the Deck like you have nine minutes left.*
