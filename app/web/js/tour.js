/**
 * GatePulse first-time walkthrough (Driver.js).
 * Decision D-030 · Source S-USER-08
 */
(function () {
  const STORAGE_KEY = "gatepulse_tour_v1";
  const DRIVER_CDN_JS = "https://cdn.jsdelivr.net/npm/driver.js@1.3.5/dist/driver.js.iife.js";
  const DRIVER_CDN_CSS = "https://cdn.jsdelivr.net/npm/driver.js@1.3.5/dist/driver.css";

  function loadCss(href) {
    if (document.querySelector(`link[href="${href}"]`)) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (window.driver && window.driver.js) {
        resolve();
        return;
      }
      const existing = document.querySelector(`script[src="${src}"]`);
      if (existing) {
        existing.addEventListener("load", () => resolve());
        if (window.driver && window.driver.js) resolve();
        return;
      }
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = () => resolve();
      s.onerror = () => reject(new Error("Failed to load Driver.js"));
      document.head.appendChild(s);
    });
  }

  function go(view) {
    if (typeof window.gatepulseShowView === "function") {
      window.gatepulseShowView(view);
    }
  }

  function markDone() {
    try {
      localStorage.setItem(STORAGE_KEY, "done");
    } catch (_) {
      /* private mode */
    }
  }

  function isDone() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "done";
    } catch (_) {
      return false;
    }
  }

  function buildSteps() {
    return [
      {
        element: "#tour-brand",
        popover: {
          title: "Welcome to GatePulse",
          description:
            "This app tracks exam, term-start, and inspection readiness across four school campuses. " +
            "The dark strip is just the brand rail — the real work happens in the pages on the right.",
          side: "right",
          align: "start",
        },
        onHighlightStarted: () => go("deck"),
      },
      {
        element: "#main-nav",
        popover: {
          title: "How to navigate",
          description:
            "Use these tabs to move around. " +
            "<strong>Deck</strong> = manager view. Labels with <em>BE</em> open backend tools " +
            "(Engine, Data, Model). Campuses and Exports are day-to-day pages.",
          side: "bottom",
          align: "start",
        },
        onHighlightStarted: () => go("deck"),
      },
      {
        element: "#tour-help",
        popover: {
          title: "Stuck later?",
          description:
            "Click <strong>Take tour</strong> anytime to replay this guide. " +
            "We only auto-start once — your choice is remembered in this browser.",
          side: "bottom",
          align: "end",
        },
      },
      {
        element: "#tour-hero-copy",
        popover: {
          title: "Command Deck",
          description:
            "This is the frontend “steering” screen. It explains what you are looking at " +
            "and summarizes campus programme health for SLT meetings — no coding required here.",
          side: "bottom",
          align: "start",
        },
        onHighlightStarted: () => go("deck"),
      },
      {
        element: "#tour-kpi",
        popover: {
          title: "Live KPIs",
          description:
            "These numbers come from the backend pipeline (programmes, critical count, AI risk, progress). " +
            "If they look empty, open <strong>Engine</strong> and run the full pipeline first.",
          side: "left",
          align: "start",
        },
      },
      {
        element: "#tour-health",
        popover: {
          title: "Campus health chart",
          description:
            "Stacked bars by campus (Riverside, Hillcrest, Harbour, Oakwood). " +
            "Colors mean status: green = on track, yellow = watch, orange = at risk, red = critical.",
          side: "bottom",
          align: "start",
        },
      },
      {
        element: "#tour-insights",
        popover: {
          title: "AI read-out",
          description:
            "Short plain-language tips generated from the risk model — " +
            "which programme is riskiest, which campus needs attention, data-quality warnings.",
          side: "left",
          align: "start",
        },
      },
      {
        element: '#main-nav [data-nav="engine"]',
        popover: {
          title: "Engine = backend controls",
          description:
            "Next we visit Engine. This is where you run the Python pipeline from the browser " +
            "(generate data → clean it → score quality → train AI → export reports).",
          side: "bottom",
          align: "start",
        },
      },
      {
        element: "#stage-rail",
        popover: {
          title: "Pipeline stages",
          description:
            "Click any stage to run just that backend step. Watch the black terminal for logs — " +
            "that proves the UI is calling real Python code, not fake demo buttons.",
          side: "right",
          align: "start",
        },
        onHighlightStarted: () => go("engine"),
      },
      {
        element: "#btn-run-all",
        popover: {
          title: "One-click refresh",
          description:
            "Prefer simplicity? Hit <strong>Run full pipeline</strong> to execute steps 1→5. " +
            "Then jump back to Deck — KPIs and charts will update.",
          side: "bottom",
          align: "start",
        },
        onHighlightStarted: () => go("engine"),
      },
      {
        element: "#tour-raw",
        popover: {
          title: "Data lab — raw vs cleaned",
          description:
            "Left table = messy source files. Right table = after ETL cleaning. " +
            "This is how you check what the backend fixed (bad dates, missing progress, typos).",
          side: "bottom",
          align: "start",
        },
        onHighlightStarted: () => go("datalab"),
      },
      {
        element: "#tour-whatif",
        popover: {
          title: "Model lab — try the AI",
          description:
            "Move the sliders and click <strong>Score with backend model</strong>. " +
            "You are calling the saved RandomForest model live — great for demos and learning.",
          side: "right",
          align: "start",
        },
        onHighlightStarted: () => go("modellab"),
      },
      {
        element: '#main-nav [data-nav="deck"]',
        popover: {
          title: "You are ready",
          description:
            "Suggested path: <strong>Engine → Run full pipeline</strong>, then explore Deck, Data, and Model. " +
            "Press Escape anytime to close a tour. Click Take tour in the header to restart.",
          side: "bottom",
          align: "start",
        },
        onHighlightStarted: () => go("deck"),
      },
    ];
  }

  function createDriver() {
    const factory = window.driver.js.driver;
    return factory({
      showProgress: true,
      animate: true,
      overlayColor: "rgba(10, 14, 18, 0.72)",
      stagePadding: 8,
      stageRadius: 4,
      smoothScroll: true,
      allowClose: true,
      overlayClickBehavior: "close",
      nextBtnText: "Next",
      prevBtnText: "Back",
      doneBtnText: "Get Started",
      progressText: "Step {{current}} of {{total}}",
      showButtons: ["next", "previous", "close"],
      steps: buildSteps(),
      onDestroyed: function () {
        markDone();
        go("deck");
      },
      onPopoverRender: function (popover) {
        const closeBtn = popover.wrapper.querySelector(".driver-popover-close-btn");
        if (closeBtn) {
          closeBtn.setAttribute("aria-label", "Skip tour");
          closeBtn.title = "Skip tour (Esc)";
        }
      },
    });
  }

  let driverObj = null;

  async function ensureReady() {
    loadCss(DRIVER_CDN_CSS);
    await loadScript(DRIVER_CDN_JS);
    if (!window.driver || !window.driver.js) {
      throw new Error("Driver.js global missing");
    }
  }

  async function startTour(opts = {}) {
    const { force = false } = opts;
    if (!force && isDone()) return;
    await ensureReady();
    // Small delay so view DOM (tables/charts) exists after navigation hooks
    await new Promise((r) => setTimeout(r, 120));
    go("deck");
    await new Promise((r) => setTimeout(r, 80));
    driverObj = createDriver();
    driverObj.drive();
  }

  function bindHelp() {
    const btn = document.getElementById("tour-help");
    if (!btn) return;
    btn.addEventListener("click", () => {
      startTour({ force: true }).catch((err) => console.error(err));
    });
  }

  // Escape is handled by Driver.js when allowClose is true; add backup while tour active
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && driverObj && driverObj.isActive && driverObj.isActive()) {
      driverObj.destroy();
    }
  });

  window.gatepulseTour = {
    start: () => startTour({ force: true }),
    startIfNeeded: () => startTour({ force: false }),
    reset: () => {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (_) {
        /* ignore */
      }
    },
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindHelp);
  } else {
    bindHelp();
  }
})();
