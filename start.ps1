# Start Citehouse backend + frontend (dev)
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

$BackendCmd = @"
Set-Location '$Root\backend'
& '.\.venv\Scripts\Activate.ps1'
uvicorn main:app --reload --host 127.0.0.1 --port 8000
"@

$FrontendCmd = @"
Set-Location '$Root\frontend'
npm run dev
"@

Write-Host "Starting backend  -> http://127.0.0.1:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd

Write-Host "Starting frontend -> http://localhost:3000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd

Write-Host "Both servers launching in separate windows."
