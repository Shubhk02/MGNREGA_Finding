# Start Both MGNREGA Backend and Frontend
# This script launches both servers in separate windows

Write-Host "Starting MGNREGA Application..." -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

$projectRoot = "e:\Projects\MGNREGA_Finding\MGNREGA_Finding"

# Check if backend .env exists
if (-not (Test-Path "$projectRoot\backend\.env")) {
    Write-Host "ERROR: backend\.env file not found!" -ForegroundColor Red
    Write-Host "Please configure MongoDB connection in backend\.env" -ForegroundColor Yellow
    exit 1
}

# Check if Python venv exists
if (-not (Test-Path "$projectRoot\.venv\Scripts\python.exe")) {
    Write-Host "ERROR: Python virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Start Backend in new window
Write-Host "Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "$projectRoot\start-backend.ps1"
Start-Sleep -Seconds 3

# Wait for backend to be ready
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "`u2713 Backend is ready!" -ForegroundColor Green
        }
    }
    catch {
        $attempt++
        Write-Host ("  Attempt {0}/{1}..." -f $attempt, $maxAttempts) -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $backendReady) {
    Write-Host "WARNING: Backend may not be ready yet. Check the backend window." -ForegroundColor Yellow
}

# Start Frontend in new window
Write-Host "Starting Frontend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File", "$projectRoot\start-frontend.ps1"

Write-Host "" # blank line
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "MGNREGA Application Started!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "" # blank line
Write-Host "Access the application at:" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3002" -ForegroundColor Cyan
Write-Host "  Backend:  http://127.0.0.1:8000/api/" -ForegroundColor Cyan
Write-Host "" # blank line
Write-Host "Close both terminal windows to stop the servers." -ForegroundColor Yellow
