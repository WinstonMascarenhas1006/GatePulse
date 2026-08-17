/* GatePulse custom UI client — talks to FastAPI backend */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const state = {
  launches: [],
  charts: {},
};

async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res;
}

function destroyChart(key) {
  if (state.charts[key]) {
    state.charts[key].destroy();
    delete state.charts[key];
  }
}

function renderTable(tableEl, rows, preferredCols) {
  const thead = tableEl.querySelector("thead");
  const tbody = tableEl.querySelector("tbody");
  thead.innerHTML = "";
  tbody.innerHTML = "";
  if (!rows || !rows.length) {
    tbody.innerHTML = "<tr><td>No rows</td></tr>";
    return;
  }
  const cols = preferredCols || Object.keys(rows[0]);
  thead.innerHTML = `<tr>${cols.map((c) => `<th>${c}</th>`).join("")}</tr>`;
  tbody.innerHTML = rows
    .map(
      (r) =>
        `<tr>${cols.map((c) => `<td>${r[c] ?? ""}</td>`).join("")}</tr>`
    )
    .join("");
}

function setKpis(el, items) {
  el.innerHTML = items
    .map(([lbl, val], i) => {
      const span = i === items.length - 1 && items.length % 2 === 1 ? " span" : "";
      return `<div class="kpi${span}"><div class="lbl">${lbl}</div><div class="val">${val}</div></div>`;
    })
    .join("");
}

function showView(name) {
  $$(".view").forEach((v) => v.classList.remove("is-active"));
  $$(".nav-btn").forEach((b) => b.classList.toggle("is-active", b.dataset.nav === name));
  const view = $(`#view-${name}`);
  if (view) view.classList.add("is-active");
  if (name === "deck") loadDeck();
  if (name === "engine") loadEngine();
  if (name === "datalab") loadDataLab();
  if (name === "modellab") loadModelLab();
  if (name === "launches") loadLaunches();
  if (name === "exports") loadExports();
}

window.gatepulseShowView = showView;

async function loadMeta() {
  try {
    const meta = await api("/api/meta");
    $("#meta-pulse").textContent = meta.finished || meta.last_stage || "no run yet";
  } catch {
    $("#meta-pulse").textContent = "offline";
  }
}

const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
};

async function loadDeck() {
  const data = await api("/api/overview");
  setKpis($("#kpi-strip"), [
    ["Programmes", data.kpis.launches],
    ["Critical", data.kpis.critical],
    ["High risk", data.kpis.high_risk],
    ["Avg progress", `${data.kpis.avg_progress}%`],
    ["Avg risk", data.kpis.avg_risk],
  ]);
  $("#insight-list").innerHTML = data.insights.map((t) => `<li>${t}</li>`).join("");

  const campuses = [...new Set(data.health_by_campus.map((r) => r.campus_code))];
  const healths = [...new Set(data.health_by_campus.map((r) => r.health))];
  const palette = {
    "On track": "#1f7a54",
    Watch: "#c48a2a",
    "At risk": "#d1672b",
    Critical: "#c23434",
  };
  destroyChart("health");
  state.charts.health = new Chart($("#chart-health"), {
    type: "bar",
    data: {
      labels: campuses,
      datasets: healths.map((h) => ({
        label: h,
        backgroundColor: palette[h] || "#888",
        data: campuses.map((p) => {
          const hit = data.health_by_campus.find((r) => r.campus_code === p && r.health === h);
          return hit ? hit.count : 0;
        }),
      })),
    },
    options: {
      ...chartDefaults,
      plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } } },
      scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } } },
    },
  });

  destroyChart("scatter");
  state.charts.scatter = new Chart($("#chart-scatter"), {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Programmes",
          data: data.scatter.map((r) => ({
            x: r.avg_progress,
            y: r.slip_risk_score,
          })),
          backgroundColor: "rgba(255,77,46,0.55)",
          pointRadius: 5,
        },
      ],
    },
    options: {
      ...chartDefaults,
      plugins: { legend: { display: false } },
      scales: {
        x: { title: { display: true, text: "Progress %" }, min: 0, max: 100 },
        y: { title: { display: true, text: "Slip risk" }, min: 0, max: 100 },
      },
    },
  });
}

async function loadEngine() {
  const stages = await api("/api/pipeline/stages");
  const rail = $("#stage-rail");
  rail.innerHTML = stages
    .map(
      (s) => `
      <button type="button" class="stage-btn" data-stage="${s.id}">
        <strong>${s.title}</strong>
        <small>${s.writes}</small>
      </button>`
    )
    .join("");
  $$(".stage-btn", rail).forEach((btn) => {
    btn.onclick = () => runStage(btn.dataset.stage);
  });

  const lin = await api("/api/pipeline/lineage");
  const box = $("#lineage");
  box.innerHTML = lin.nodes
    .map((n, i) => {
      const node = `<span class="lin-node ${n.layer === "frontend" ? "fe" : "be"}">${n.label}</span>`;
      return i < lin.nodes.length - 1 ? node + '<span class="lin-arrow">→</span>' : node;
    })
    .join("");

  const arts = await api("/api/pipeline/artifacts");
  renderTable($("#artifacts-table"), arts);
}

function appendLog(lines) {
  const term = $("#terminal");
  const stamp = lines.join("\n");
  term.textContent = (term.textContent + "\n" + stamp).trim();
  term.scrollTop = term.scrollHeight;
}

async function runStage(id) {
  const seed = Number($("#seed").value || 42);
  appendLog([`> run ${id} (seed=${seed})`]);
  try {
    const out = await api(`/api/pipeline/run/${id}`, {
      method: "POST",
      body: JSON.stringify({ seed }),
    });
    appendLog(out.logs || []);
    appendLog([out.ok ? `OK ${out.elapsed_s.toFixed(2)}s` : `FAIL ${JSON.stringify(out.detail)}`]);
    await loadMeta();
    if (id === "export" || id === "ai") loadEngine();
  } catch (err) {
    appendLog([String(err.message || err)]);
  }
}

$("#btn-run-all").onclick = async () => {
  const seed = Number($("#seed").value || 42);
  appendLog([`> run-all (seed=${seed})`]);
  try {
    const out = await api("/api/pipeline/run-all", {
      method: "POST",
      body: JSON.stringify({ seed }),
    });
    (out.results || []).forEach((r) => appendLog(r.logs || []));
    appendLog([out.ok ? "FULL PIPELINE OK" : "FULL PIPELINE HAD FAILURES"]);
    await loadMeta();
    await loadEngine();
  } catch (err) {
    appendLog([String(err.message || err)]);
  }
};

async function loadDataLab() {
  const diff = await api("/api/data/raw-vs-clean");
  $("#raw-path").textContent = "raw milestones";
  $("#clean-path").textContent = "cleaned milestones";
  renderTable($("#raw-table"), diff.raw);
  renderTable($("#clean-table"), diff.clean);
  renderTable($("#issues-table"), diff.issues);

  const tables = await api("/api/sqlite/tables");
  const sel = $("#sql-table");
  sel.innerHTML = tables.map((t) => `<option value="${t}">${t}</option>`).join("");
  $("#btn-sql").onclick = async () => {
    const rows = await api(`/api/sqlite/${sel.value}?limit=120`);
    renderTable($("#sql-data"), rows);
  };
  if (tables.length) $("#btn-sql").click();

  const issues = diff.issues || [];
  const counts = {};
  issues.forEach((i) => {
    counts[i.issue_type] = (counts[i.issue_type] || 0) + 1;
  });
  destroyChart("quality");
  state.charts.quality = new Chart($("#chart-quality"), {
    type: "doughnut",
    data: {
      labels: Object.keys(counts),
      datasets: [
        {
          data: Object.values(counts),
          backgroundColor: ["#ff4d2e", "#101820", "#5c6b78", "#1f7a54"],
        },
      ],
    },
    options: { ...chartDefaults, plugins: { legend: { position: "bottom", labels: { boxWidth: 10 } } } },
  });
}

function buildWhatIfForm() {
  const fields = [
    ["campus_code", "select", ["RIV", "HIL", "HAR", "OAK"]],
    ["priority", "select", ["P1", "P2", "P3"]],
    ["family", "select", ["Curriculum", "Exams", "Pastoral", "Inspection"]],
    ["power_class", "select", ["Primary", "Secondary"]],
    ["avg_complexity", "range", { min: 1, max: 5, step: 0.1, value: 3.5 }],
    ["open_tasks", "range", { min: 0, max: 40, step: 1, value: 12 }],
    ["blocked_milestones", "range", { min: 0, max: 6, step: 1, value: 1 }],
    ["avg_slip_days", "range", { min: 0, max: 30, step: 0.5, value: 8 }],
    ["quality_score", "range", { min: 40, max: 100, step: 1, value: 78 }],
  ];
  const form = $("#whatif-form");
  form.innerHTML = fields
    .map(([name, type, conf]) => {
      if (type === "select") {
        return `<label>${name}<select name="${name}">${conf
          .map((v) => `<option value="${v}">${v}</option>`)
          .join("")}</select></label>`;
      }
      return `<label>${name}<input type="range" name="${name}" min="${conf.min}" max="${conf.max}" step="${conf.step}" value="${conf.value}" /></label>`;
    })
    .join("");
}

async function loadModelLab() {
  buildWhatIfForm();
  try {
    const metrics = await api("/api/model/metrics");
    setKpis($("#model-kpis"), [
      ["Train", metrics.n_train],
      ["Test", metrics.n_test],
      ["ROC-AUC", metrics.roc_auc != null ? metrics.roc_auc.toFixed(3) : "n/a"],
      ["Pos rate", `${Math.round((metrics.positive_rate || 0) * 100)}%`],
      ["Model", "joblib"],
    ]);
  } catch {
    setKpis($("#model-kpis"), [["Status", "Run AI stage"]]);
  }

  try {
    const fi = await api("/api/model/feature-importance");
    const top = fi.slice(0, 12).reverse();
    destroyChart("fi");
    state.charts.fi = new Chart($("#chart-fi"), {
      type: "bar",
      data: {
        labels: top.map((r) => r.feature),
        datasets: [
          {
            data: top.map((r) => r.importance),
            backgroundColor: "#ff4d2e",
          },
        ],
      },
      options: {
        ...chartDefaults,
        indexAxis: "y",
        plugins: { legend: { display: false } },
      },
    });
  } catch {
    /* ignore until trained */
  }

  const risks = await api("/api/model/risks");
  renderTable($("#risk-table"), risks, [
    "launch_name",
    "campus_code",
    "slip_risk_score",
    "slip_risk_label",
    "priority",
    "health",
  ]);
}

$("#btn-whatif").onclick = async () => {
  const form = $("#whatif-form");
  const fd = new FormData(form);
  const body = {
    max_complexity: 5,
    workstream_count: 6,
    blocked_tasks: 1,
    open_milestones: 3,
    effort_hours: 40,
  };
  fd.forEach((v, k) => {
    body[k] = Number.isNaN(Number(v)) || ["campus_code", "priority", "family", "power_class"].includes(k)
      ? v
      : Number(v);
  });
  try {
    const out = await api("/api/model/what-if", { method: "POST", body: JSON.stringify(body) });
    $("#whatif-out").textContent = `${out.slip_risk_score} / 100 · ${out.slip_risk_label}`;
  } catch (err) {
    $("#whatif-out").textContent = String(err.message || err);
  }
};

async function loadLaunches() {
  state.launches = await api("/api/launches");
  const campuses = [...new Set(state.launches.map((l) => l.campus_code))];
  const pf = $("#campus-filter");
  pf.innerHTML =
    `<option value="All">All campuses</option>` +
    campuses.map((p) => `<option value="${p}">${p}</option>`).join("");

  const redraw = () => {
    const campus = pf.value;
    const rows =
      campus === "All" ? state.launches : state.launches.filter((l) => l.campus_code === campus);
    renderTable($("#launches-table"), rows, [
      "launch_id",
      "launch_name",
      "campus_code",
      "priority",
      "avg_progress",
      "health",
      "slip_risk_score",
      "quality_score",
    ]);
    const sel = $("#launch-select");
    sel.innerHTML = rows.map((r) => `<option value="${r.launch_id}">${r.launch_name}</option>`).join("");
    if (rows.length) loadLaunchDetail(rows[0].launch_id);
  };
  pf.onchange = redraw;
  $("#launch-select").onchange = (e) => loadLaunchDetail(e.target.value);
  redraw();
}

async function loadLaunchDetail(id) {
  const ms = await api(`/api/launches/${id}/milestones`);
  const tasks = await api(`/api/launches/${id}/tasks`);
  renderTable($("#tasks-table"), tasks, ["task_name", "assignee", "status", "due_date", "effort_hours"]);
  destroyChart("gates");
  const colors = ms.map((m) =>
    m.status === "Blocked"
      ? "#c23434"
      : m.status === "Delayed"
        ? "#d1672b"
        : m.status === "Completed"
          ? "#1f7a54"
          : "#101820"
  );
  state.charts.gates = new Chart($("#chart-gates"), {
    type: "bar",
    data: {
      labels: ms.map((m) => m.milestone_type),
      datasets: [{ data: ms.map((m) => m.progress_pct), backgroundColor: colors }],
    },
    options: {
      ...chartDefaults,
      indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: { x: { max: 100, title: { display: true, text: "Progress %" } } },
    },
  });
}

async function loadExports() {
  const files = await api("/api/exports");
  $("#file-list").innerHTML = files
    .map(
      (f) => `
      <li>
        <span>${f.name} · ${f.kb} KB</span>
        <a href="/api/exports/download/${encodeURIComponent(f.name)}">Download</a>
      </li>`
    )
    .join("") || "<li>No files yet</li>";
}

$("#btn-exports").onclick = async () => {
  await api("/api/exports/refresh", { method: "POST", body: "{}" });
  await loadExports();
};

$$("[data-nav]").forEach((el) => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    showView(el.dataset.nav);
  });
});

(async function boot() {
  await loadMeta();
  showView("deck");
  // First-time onboarding (skipped if localStorage says done)
  if (window.gatepulseTour && typeof window.gatepulseTour.startIfNeeded === "function") {
    setTimeout(() => {
      window.gatepulseTour.startIfNeeded().catch((err) => console.error(err));
    }, 450);
  }
})().catch((err) => {
  console.error(err);
  $("#kpi-strip").innerHTML =
    `<div class="kpi"><div class="lbl">Error</div><div class="val" style="font-size:1rem">Run pipeline then refresh</div></div>`;
});
