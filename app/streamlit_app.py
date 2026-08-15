"""
GatePulse UI — realigned layout system (D-025).
Sources: S-USER-04, S-DESIGN-01, S-USER-03 (dual front/back visibility).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gatepulse.ai_risk import FEATURE_COLS_NUM, generate_insights, score_what_if  # noqa: E402
from gatepulse.config import DATA_EXPORTS, DATA_PROCESSED, DATA_RAW, MODELS_DIR, PLANTS  # noqa: E402
from gatepulse.engine import (  # noqa: E402
    PIPELINE_STAGES,
    artifact_inventory,
    lineage_nodes_edges,
    list_sqlite_tables,
    raw_vs_clean_milestones,
    read_sqlite_table,
    run_stage,
)
from gatepulse.report import export_all  # noqa: E402

st.set_page_config(
    page_title="GatePulse",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Alignment system: 1200px content rail, 24px gutter, sticky brand masthead,
# left-label / right-canvas pages, equal metric cells, mono meta baseline.
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --gp-ink: #e8f0f4;
  --gp-muted: #8aa0ad;
  --gp-sand: #e2b86a;
  --gp-teal: #5eb0c8;
  --gp-line: rgba(232,240,244,0.12);
  --gp-panel: rgba(8, 16, 22, 0.55);
  --gp-gutter: 1.25rem;
  --gp-max: 1180px;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  color: var(--gp-ink);
}

.stApp {
  background:
    linear-gradient(105deg, rgba(14,28,36,0.92) 0%, rgba(14,28,36,0.55) 42%, rgba(14,28,36,0.88) 100%),
    radial-gradient(ellipse 80% 50% at 80% -10%, #2a4a3a 0%, transparent 55%),
    radial-gradient(ellipse 60% 40% at 0% 100%, #1a3344 0%, transparent 50%),
    #0a1218;
}

/* Tighten Streamlit's default sprawl */
.block-container {
  max-width: var(--gp-max) !important;
  padding-top: 1.1rem !important;
  padding-bottom: 3rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
}

section[data-testid="stSidebar"] {
  background: #070e13;
  border-right: 1px solid var(--gp-line);
}
section[data-testid="stSidebar"] .block-container {
  padding-top: 1.5rem !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
  font-family: 'DM Sans', sans-serif !important;
}

h1, h2, h3 { font-family: 'Instrument Serif', serif !important; font-weight: 400 !important; letter-spacing: -0.02em; }
[data-testid="stHeader"] { background: transparent; }

/* Masthead */
.gp-mast {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: end;
  gap: var(--gp-gutter);
  padding-bottom: 1rem;
  margin-bottom: 1.35rem;
  border-bottom: 1px solid var(--gp-line);
}
.gp-brand {
  font-family: 'Instrument Serif', serif;
  font-size: clamp(2.4rem, 4vw, 3.4rem);
  line-height: 0.95;
  color: #f4efe6;
  margin: 0;
}
.gp-brand em {
  font-style: italic;
  color: var(--gp-sand);
}
.gp-kicker {
  margin: 0.55rem 0 0;
  color: var(--gp-muted);
  font-size: 0.95rem;
  max-width: 34rem;
  line-height: 1.45;
}
.gp-meta {
  text-align: right;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--gp-muted);
  line-height: 1.7;
}
.gp-chip {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 0.2rem 0.45rem;
  margin-left: 0.35rem;
  border: 1px solid var(--gp-line);
}
.gp-chip.fe { color: var(--gp-sand); border-color: rgba(226,184,106,0.45); }
.gp-chip.be { color: var(--gp-teal); border-color: rgba(94,176,200,0.45); }

/* Section title row: label left, rule fills */
.gp-section {
  display: grid;
  grid-template-columns: 9.5rem 1fr;
  gap: var(--gp-gutter);
  align-items: start;
  margin: 1.6rem 0 0.85rem;
}
.gp-section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gp-sand);
  padding-top: 0.35rem;
}
.gp-section-body h2 {
  margin: 0 0 0.35rem !important;
  font-size: 1.55rem !important;
  color: #f4efe6;
}
.gp-section-body p {
  margin: 0;
  color: var(--gp-muted);
  font-size: 0.92rem;
}

/* KPI band — equal cells, shared baseline */
.gp-kpi {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  border: 1px solid var(--gp-line);
  background: var(--gp-panel);
}
.gp-kpi > div {
  padding: 0.9rem 1rem;
  border-right: 1px solid var(--gp-line);
}
.gp-kpi > div:last-child { border-right: none; }
.gp-kpi .lbl {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--gp-muted);
}
.gp-kpi .val {
  font-family: 'Instrument Serif', serif;
  font-size: 1.85rem;
  margin-top: 0.25rem;
  color: #f4efe6;
}

/* Panels */
.gp-panel {
  border: 1px solid var(--gp-line);
  background: var(--gp-panel);
  padding: 1rem 1.1rem;
  min-height: 100%;
}
.gp-panel h3 {
  margin: 0 0 0.75rem !important;
  font-size: 1.25rem !important;
}
.gp-insight {
  border-left: 2px solid var(--gp-sand);
  padding: 0.45rem 0 0.45rem 0.75rem;
  margin: 0.55rem 0;
  color: var(--gp-ink);
  font-size: 0.92rem;
  line-height: 1.4;
}

.gp-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--gp-gutter);
}
.gp-split-33 {
  display: grid;
  grid-template-columns: 0.9fr 1.6fr;
  gap: var(--gp-gutter);
  align-items: start;
}
.gp-split-rail {
  display: grid;
  grid-template-columns: 13.5rem 1fr;
  gap: var(--gp-gutter);
  align-items: start;
}

.gp-rail-item {
  border-left: 2px solid rgba(94,176,200,0.35);
  padding: 0.55rem 0 0.55rem 0.7rem;
  margin-bottom: 0.35rem;
}
.gp-rail-item strong {
  display: block;
  font-size: 0.88rem;
  color: #f4efe6;
}
.gp-rail-item span {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  color: var(--gp-muted);
}

.terminal {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  background: #05090c;
  border: 1px solid rgba(94,176,200,0.28);
  padding: 0.9rem 1rem;
  max-height: 260px;
  overflow-y: auto;
  white-space: pre-wrap;
  color: #9ec9da;
  line-height: 1.55;
}

div[data-testid="stMetric"] {
  background: transparent;
  border: none;
  padding: 0;
}
div[data-testid="stMetric"] label { color: var(--gp-muted) !important; }

/* Buttons flush to alignment */
.stButton > button {
  border-radius: 2px !important;
  border: 1px solid rgba(226,184,106,0.45) !important;
  background: rgba(226,184,106,0.08) !important;
  color: #f4efe6 !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: rgba(226,184,106,0.22) !important;
}

@media (max-width: 900px) {
  .gp-kpi { grid-template-columns: repeat(2, 1fr); }
  .gp-split, .gp-split-33, .gp-split-rail, .gp-section, .gp-mast {
    grid-template-columns: 1fr;
  }
  .gp-meta { text-align: left; margin-top: 0.75rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8f0f4", family="DM Sans"),
    margin=dict(l=8, r=8, t=48, b=8),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
)


@st.cache_data(show_spinner=False)
def _cached_tables() -> dict[str, pd.DataFrame]:
    required = [
        "launch_facts_scored",
        "milestones",
        "tasks",
        "quality_issues",
        "launch_risk_scores",
        "plants",
        "workstreams",
    ]
    if any(not (DATA_PROCESSED / f"{r}.csv").exists() for r in required):
        return {}
    return {r: pd.read_csv(DATA_PROCESSED / f"{r}.csv") for r in required}


def load_tables() -> dict[str, pd.DataFrame]:
    return _cached_tables()


def masthead(title_em: str, kicker: str, layer: str) -> None:
    meta = ""
    meta_path = DATA_PROCESSED / "last_pipeline_run.json"
    if meta_path.exists():
        try:
            m = json.loads(meta_path.read_text(encoding="utf-8"))
            meta = m.get("finished") or m.get("last_stage") or ""
        except Exception:  # noqa: BLE001
            meta = ""
    chip = (
        '<span class="gp-chip fe">frontend</span>'
        if layer == "fe"
        else '<span class="gp-chip be">backend</span>'
        if layer == "be"
        else '<span class="gp-chip fe">front</span><span class="gp-chip be">back</span>'
    )
    st.markdown(
        f"""
        <div class="gp-mast">
          <div>
            <p class="gp-brand">Gate<em>Pulse</em></p>
            <p class="gp-kicker"><strong style="color:#f4efe6">{title_em}</strong> — {kicker}</p>
          </div>
          <div class="gp-meta">
            HELION INDUSTRIAL · DEMO{chip}<br/>
            LAST BACKEND PULSE<br/>{meta or "—"}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(label: str, title: str, blurb: str = "") -> None:
    blurb_html = f"<p>{blurb}</p>" if blurb else ""
    st.markdown(
        f"""
        <div class="gp-section">
          <div class="gp-section-label">{label}</div>
          <div class="gp-section-body">
            <h2>{title}</h2>
            {blurb_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_band(facts: pd.DataFrame) -> None:
    cells = [
        ("Launches", f"{len(facts)}"),
        ("Critical", f"{int((facts['health']=='Critical').sum())}"),
        ("High risk", f"{int((facts['slip_risk_label']=='High').sum())}"),
        ("Avg progress", f"{facts['avg_progress'].mean():.0f}%"),
        ("Avg risk", f"{facts['slip_risk_score'].mean():.0f}"),
    ]
    inner = "".join(
        f'<div><div class="lbl">{a}</div><div class="val">{b}</div></div>' for a, b in cells
    )
    st.markdown(f'<div class="gp-kpi">{inner}</div>', unsafe_allow_html=True)


def style_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOT_LAYOUT)
    return fig


def page_overview(data: dict[str, pd.DataFrame]) -> None:
    facts = data["launch_facts_scored"]
    risks = data["launch_risk_scores"]
    masthead("Command deck", "Manager-facing portfolio pulse across plants.", "fe")
    kpi_band(facts)

    section("01 · Health", "Plant posture", "Backend facts rendered as a frontend composition.")
    left, right = st.columns((1.45, 1), gap="large")
    with left:
        fig = px.bar(
            facts.groupby(["plant_code", "health"]).size().reset_index(name="count"),
            x="plant_code",
            y="count",
            color="health",
            color_discrete_map={
                "On track": "#3d8b6e",
                "Watch": "#e2b86a",
                "At risk": "#d17a3a",
                "Critical": "#c44b4b",
            },
        )
        fig.update_layout(title=None, xaxis_title=None, yaxis_title="Launches", bargap=0.25)
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with right:
        st.markdown('<div class="gp-panel"><h3>AI read-out</h3>', unsafe_allow_html=True)
        for line in generate_insights(risks, facts):
            st.markdown(f'<div class="gp-insight">{line}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    section("02 · Risk map", "Progress versus slip risk", "Bubble size = workstream complexity from backend features.")
    scatter = px.scatter(
        facts,
        x="avg_progress",
        y="slip_risk_score",
        color="plant_code",
        size="avg_complexity",
        hover_name="launch_name",
        color_discrete_sequence=["#e2b86a", "#5eb0c8", "#3d8b6e", "#c97b63"],
    )
    scatter.update_layout(xaxis_title="Progress %", yaxis_title="AI slip-risk score")
    st.plotly_chart(style_fig(scatter), use_container_width=True)


def _lineage_figure() -> go.Figure:
    nodes, edges = lineage_nodes_edges()
    labels = [n["label"] for n in nodes]
    idx = {n["id"]: i for i, n in enumerate(nodes)}
    colors = ["#5eb0c8" if n["layer"] != "frontend" else "#e2b86a" for n in nodes]
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(label=labels, color=colors, pad=18, thickness=14, line=dict(width=0)),
            link=dict(
                source=[idx[e["source"]] for e in edges],
                target=[idx[e["target"]] for e in edges],
                value=[1] * len(edges),
                label=[e["label"] for e in edges],
                color="rgba(226,184,106,0.22)",
            ),
        )
    )
    return style_fig(fig)


def page_engine_room() -> None:
    masthead("Engine room", "Run backend stages from the browser. Logs stream into the canvas.", "be")
    seed = st.sidebar.number_input("Seed", min_value=1, max_value=9999, value=42, step=1)

    section("01 · Lineage", "How data moves", "Blue = backend nodes · sand = frontend sink.")
    st.plotly_chart(_lineage_figure(), use_container_width=True)

    section("02 · Stages", "Execute pipeline", "Left rail = stage index. Right canvas = actions + terminal.")
    rail, canvas = st.columns((0.85, 2.4), gap="large")
    with rail:
        for stage in PIPELINE_STAGES:
            st.markdown(
                f"""
                <div class="gp-rail-item">
                  <strong>{stage['title']}</strong>
                  <span>{stage['writes']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with canvas:
        st.markdown(f'<div class="gp-panel">', unsafe_allow_html=True)
        btn_cols = st.columns(len(PIPELINE_STAGES))
        for col, stage in zip(btn_cols, PIPELINE_STAGES):
            with col:
                if st.button(stage["id"], key=f"run_{stage['id']}", use_container_width=True):
                    log_box = st.empty()
                    lines: list[str] = []

                    def _cb(msg: str, _lines=lines, _box=log_box) -> None:
                        _lines.append(msg)
                        _box.markdown(
                            '<div class="terminal">' + "<br/>".join(_lines[-50:]) + "</div>",
                            unsafe_allow_html=True,
                        )

                    with st.spinner(stage["id"]):
                        result = run_stage(stage["id"], log=_cb, seed=int(seed))
                    st.cache_data.clear()
                    if result.ok:
                        st.success(f"{stage['id']} · {result.elapsed_s:.2f}s")
                    else:
                        st.error(result.detail.get("error", "failed"))

        if st.button("Run full pipeline 1 → 5", type="primary", use_container_width=True):
            log_box = st.empty()
            lines = []

            def _cb(msg: str, _lines=lines, _box=log_box) -> None:
                _lines.append(msg)
                _box.markdown(
                    '<div class="terminal">' + "<br/>".join(_lines[-60:]) + "</div>",
                    unsafe_allow_html=True,
                )

            with st.spinner("Full refresh"):
                results = [run_stage(s["id"], log=_cb, seed=int(seed)) for s in PIPELINE_STAGES]
            st.cache_data.clear()
            st.write({r.name: round(r.elapsed_s, 2) for r in results if r.ok or True})
        st.markdown("</div>", unsafe_allow_html=True)

    section("03 · Artifacts", "Files the backend wrote", "Proof on disk — not only charts.")
    inv = artifact_inventory()
    if len(inv):
        st.dataframe(inv, use_container_width=True, hide_index=True, height=280)
    else:
        st.warning("No artifacts yet.")


def page_data_lab(data: dict[str, pd.DataFrame]) -> None:
    masthead("Data lab", "ETL X-ray: raw beside cleaned, then SQLite.", "be")
    section("01 · Diff", "Raw versus cleaned milestones", "Equal columns · shared header baseline.")

    raw_s, clean_s, issues = raw_vs_clean_milestones()
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown(
            f'<div class="gp-panel"><h3>RAW <span class="gp-chip be">backend</span></h3>'
            f'<p style="color:#8aa0ad;font-family:JetBrains Mono,monospace;font-size:0.7rem;margin:0 0 0.75rem">'
            f'{DATA_RAW / "milestones.csv"}</p></div>',
            unsafe_allow_html=True,
        )
        st.dataframe(raw_s, use_container_width=True, hide_index=True, height=320)
    with b:
        st.markdown(
            f'<div class="gp-panel"><h3>CLEANED <span class="gp-chip fe">to UI</span></h3>'
            f'<p style="color:#8aa0ad;font-family:JetBrains Mono,monospace;font-size:0.7rem;margin:0 0 0.75rem">'
            f'{DATA_PROCESSED / "milestones.csv"}</p></div>',
            unsafe_allow_html=True,
        )
        st.dataframe(clean_s, use_container_width=True, hide_index=True, height=320)

    section("02 · Store", "SQLite browser", "Frontend queries backend DB directly.")
    tables = list_sqlite_tables()
    if not tables:
        st.warning("Run ETL first.")
    else:
        c1, c2 = st.columns((1.2, 3.2), gap="large")
        with c1:
            name = st.selectbox("Table", tables)
            limit = st.slider("Rows", 20, 500, 100, 20)
        with c2:
            st.dataframe(read_sqlite_table(name, limit), use_container_width=True, hide_index=True, height=360)

    section("03 · Quality", "Repair log", "Issues detected during ETL.")
    issues_df = data.get("quality_issues", pd.DataFrame())
    if len(issues_df):
        left, right = st.columns((1, 1.4), gap="large")
        with left:
            fig = px.pie(
                issues_df,
                names="issue_type",
                color_discrete_sequence=["#e2b86a", "#5eb0c8", "#c44b4b"],
            )
            fig.update_layout(title=None)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        with right:
            st.dataframe(issues_df, use_container_width=True, hide_index=True, height=320)
    else:
        st.success("No open quality issues.")


def page_model_lab(data: dict[str, pd.DataFrame]) -> None:
    masthead("Model lab", "Inspect the trained slip-risk model and score what-ifs.", "be")
    facts = data["launch_facts_scored"]
    metrics_path = MODELS_DIR / "metrics.json"
    fi_path = MODELS_DIR / "feature_importance.csv"

    section("01 · Holdout", "Training snapshot", "Honest small-N metrics from backend artifact.")
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        cells = [
            ("Train", str(metrics.get("n_train"))),
            ("Test", str(metrics.get("n_test"))),
            ("ROC-AUC", f"{metrics['roc_auc']:.3f}" if metrics.get("roc_auc") is not None else "n/a"),
            ("Pos rate", f"{metrics.get('positive_rate', 0)*100:.0f}%"),
            ("Model", "joblib" if (MODELS_DIR / "slip_risk_model.joblib").exists() else "—"),
        ]
        inner = "".join(
            f'<div><div class="lbl">{a}</div><div class="val">{b}</div></div>' for a, b in cells
        )
        st.markdown(f'<div class="gp-kpi">{inner}</div>', unsafe_allow_html=True)
    else:
        st.warning("Run AI stage in Engine Room.")

    section("02 · X-ray", "Importance · what-if", "Controls left-aligned · chart fills remaining width.")
    left, right = st.columns((1, 1.55), gap="large")
    with left:
        st.markdown('<div class="gp-panel"><h3>What-if controls</h3>', unsafe_allow_html=True)
        avg = facts[FEATURE_COLS_NUM].mean(numeric_only=True)
        plant = st.selectbox("Plant", sorted(PLANTS.keys()))
        priority = st.selectbox("Priority", ["P1", "P2", "P3"])
        family = st.selectbox(
            "Family",
            sorted(facts["family"].dropna().unique().tolist()) if "family" in facts.columns else ["AGV"],
        )
        power_class = st.selectbox(
            "Power",
            sorted(facts["power_class"].dropna().unique().tolist())
            if "power_class" in facts.columns
            else ["DC"],
        )
        row = {c: float(avg.get(c, 0)) for c in FEATURE_COLS_NUM}
        row["avg_complexity"] = st.slider("Complexity", 1.0, 5.0, float(avg.get("avg_complexity", 3)), 0.1)
        row["open_tasks"] = st.slider("Open tasks", 0, 40, int(avg.get("open_tasks", 10)))
        row["blocked_milestones"] = st.slider(
            "Blocked gates", 0, 6, int(avg.get("blocked_milestones", 0))
        )
        row["avg_slip_days"] = st.slider("Avg slip days", 0.0, 30.0, float(avg.get("avg_slip_days", 5)), 0.5)
        row["quality_score"] = st.slider("Quality score", 40, 100, int(avg.get("quality_score", 85)))
        row.update(
            {"plant_code": plant, "priority": priority, "family": family, "power_class": power_class}
        )
        if st.button("Score with model", type="primary", use_container_width=True):
            try:
                out = score_what_if(row)
                st.markdown(
                    f'<div class="gp-insight">Score <strong>{out["slip_risk_score"]}</strong> / 100 · '
                    f'{out["slip_risk_label"]} · p={out["slip_risk_proba"]}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(str(exc))
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if fi_path.exists():
            fi = pd.read_csv(fi_path)
            fig = px.bar(
                fi.head(12).sort_values("importance"),
                x="importance",
                y="feature",
                orientation="h",
                color_discrete_sequence=["#5eb0c8"],
            )
            fig.update_layout(title=None, xaxis_title="Importance", yaxis_title=None, height=520)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        else:
            st.info("Feature importance appears after AI stage.")

    section("03 · Portfolio", "Scored launches", "Backend output table consumed by the deck.")
    st.dataframe(
        data["launch_risk_scores"].sort_values("slip_risk_score", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


def page_launches(data: dict[str, pd.DataFrame]) -> None:
    facts = data["launch_facts_scored"]
    milestones = data["milestones"]
    tasks = data["tasks"]
    masthead("Launches", "Drill from portfolio table into gate timeline.", "fe")

    section("01 · Filter", "Working set", "Filters live in the sidebar — table stays full-bleed.")
    plants = ["All"] + sorted(facts["plant_code"].unique().tolist())
    plant = st.sidebar.selectbox("Plant", plants)
    health = st.sidebar.multiselect(
        "Health", sorted(facts["health"].unique()), default=sorted(facts["health"].unique())
    )
    view = facts[facts["health"].isin(health)]
    if plant != "All":
        view = view[view["plant_code"] == plant]

    st.dataframe(
        view[
            [
                "launch_id",
                "launch_name",
                "plant_code",
                "priority",
                "sop_target",
                "avg_progress",
                "health",
                "slip_risk_score",
                "slip_risk_label",
                "quality_score",
                "planner",
            ]
        ].sort_values("slip_risk_score", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=300,
    )

    section("02 · Timeline", "Gate progress", "One launch · horizontal bars aligned to status color.")
    lid = st.selectbox("Launch", view["launch_id"].tolist())
    ms = milestones[milestones["launch_id"] == lid].sort_values("sequence")
    fig = go.Figure(
        go.Bar(
            x=ms["progress_pct"],
            y=ms["milestone_type"],
            orientation="h",
            marker_color=[
                "#c44b4b"
                if s == "Blocked"
                else "#d17a3a"
                if s == "Delayed"
                else "#3d8b6e"
                if s == "Completed"
                else "#5eb0c8"
                for s in ms["status"]
            ],
            text=ms["status"],
            textposition="auto",
        )
    )
    fig.update_layout(xaxis_title="Progress %", yaxis_title=None, height=400)
    st.plotly_chart(style_fig(fig), use_container_width=True)

    section("03 · Tasks", "Work items", "Same launch scope.")
    st.dataframe(tasks[tasks["launch_id"] == lid], use_container_width=True, hide_index=True, height=280)


def page_exports(_data: dict[str, pd.DataFrame]) -> None:
    masthead("Exports", "Backend writers · frontend downloads.", "fe")
    section("01 · Generate", "Steering pack", "Excel + Markdown executive brief.")
    if st.button("Refresh exports", type="primary"):
        st.json(export_all())
        st.success("Wrote export files.")

    section("02 · Files", "Download", "Aligned file list.")
    DATA_EXPORTS.mkdir(parents=True, exist_ok=True)
    files = sorted(DATA_EXPORTS.glob("*"))
    if not files:
        st.warning("No exports yet.")
        return
    for f in files:
        c1, c2 = st.columns((3.2, 1), gap="large")
        with c1:
            st.markdown(
                f"<p style='margin:0.55rem 0;font-family:JetBrains Mono,monospace;font-size:0.85rem'>"
                f"{f.name} · {f.stat().st_size/1024:.1f} KB</p>",
                unsafe_allow_html=True,
            )
        with c2:
            st.download_button("Download", data=f.read_bytes(), file_name=f.name, key=f"dl_{f.name}")


def main() -> None:
    st.sidebar.markdown("## GatePulse")
    st.sidebar.caption("Aligned command surface")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Overview",
            "Engine Room",
            "Data Lab",
            "Model Lab",
            "Launches",
            "Exports",
        ],
        label_visibility="collapsed",
    )

    needs_data = page != "Engine Room"
    data = load_tables() if needs_data else {}
    if needs_data and not data:
        st.warning("No processed data. Open Engine Room and run the full pipeline.")
        page_engine_room()
        return

    routes = {
        "Overview": lambda: page_overview(data),
        "Engine Room": page_engine_room,
        "Data Lab": lambda: page_data_lab(data),
        "Model Lab": lambda: page_model_lab(data),
        "Launches": lambda: page_launches(data),
        "Exports": lambda: page_exports(data),
    }
    routes[page]()


if __name__ == "__main__":
    main()
