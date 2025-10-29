# Start MGNREGA Backend Server
# This script starts the FastAPI backend on port 8000

Write-Host "Starting MGNREGA Backend Server..." -ForegroundColor Green

# Navigate to project root
Set-Location "e:\Projects\MGNREGA_Finding\MGNREGA_Finding"

# Check if .env exists in backend
if (-not (Test-Path "backend\.env")) {
    Write-Host "ERROR: backend\.env file not found!" -ForegroundColor Red
    Write-Host "Please ensure MongoDB connection is configured in backend\.env" -ForegroundColor Yellow
    exit 1
}

# Kill any process using port 8000
Write-Host "Checking for existing processes on port 8000..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique

if ($processes) {
    Write-Host "Stopping existing processes on port 8000..." -ForegroundColor Yellow
    $processes | ForEach-Object { 
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue 
    }
    Start-Sleep -Seconds 2
}

# Start the backend server
Write-Host "Starting FastAPI server on http://127.0.0.1:8000..." -ForegroundColor Green
Set-Location "backend"
& "..\\.venv\Scripts\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

# If we get here, server stopped
Write-Host "`nBackend server stopped." -ForegroundColor Yellow
