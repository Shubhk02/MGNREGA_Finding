# Start MGNREGA Frontend Development Server
# This script starts the React frontend on port 3002

Write-Host "Starting MGNREGA Frontend Development Server..." -ForegroundColor Green

# Navigate to frontend directory
Set-Location "e:\Projects\MGNREGA_Finding\MGNREGA_Finding\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    yarn install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
}

# Kill any process using port 3002
Write-Host "Checking for existing processes on port 3002..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique

if ($processes) {
    Write-Host "Stopping existing processes on port 3002..." -ForegroundColor Yellow
    $processes | ForEach-Object { 
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue 
    }
    Start-Sleep -Seconds 2
}

# Set environment variables
$env:REACT_APP_BACKEND_URL = "http://localhost:8000"
$env:PORT = "3002"
$env:BROWSER = "none"

# Start the dev server
Write-Host "Starting React dev server on http://localhost:3002..." -ForegroundColor Green
Write-Host "Backend API URL: $env:REACT_APP_BACKEND_URL" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server.`n" -ForegroundColor Yellow

yarn start

# If we get here, server stopped
Write-Host "`nFrontend server stopped." -ForegroundColor Yellow
