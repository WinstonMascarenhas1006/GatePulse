# Run GatePulse (Windows)
Set-Location $PSScriptRoot\..
if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  python -m venv .venv
  .\.venv\Scripts\pip install -r requirements.txt
}
.\.venv\Scripts\python scripts\run_pipeline.py
.\.venv\Scripts\streamlit run app\streamlit_app.py
