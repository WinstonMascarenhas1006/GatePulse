# Start GatePulse custom UI
Set-Location $PSScriptRoot\..
if (-not (Test-Path .\.venv\Scripts\python.exe)) {
  python -m venv .venv
  .\.venv\Scripts\pip install -r requirements.txt
}
.\.venv\Scripts\python scripts\run_pipeline.py
.\.venv\Scripts\uvicorn app.api:app --host 127.0.0.1 --port 8080
