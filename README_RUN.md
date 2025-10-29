# MGNREGA Dashboard - Quick Start Guide

## Prerequisites

1. **Python 3.12+** with virtual environment at `.venv/`
2. **Node.js 22+** with Yarn installed
3. **MongoDB Atlas** connection string in `backend/.env`

## Running the Application

### Option 1: Start Everything (Recommended)

Open PowerShell in the project root and run:

```powershell
.\start-all.ps1
```

This will:
- Start the backend server on http://127.0.0.1:8000
- Start the frontend dev server on http://localhost:3002
- Open both in separate terminal windows

### Option 2: Start Services Individually

#### Backend Only
```powershell
.\start-backend.ps1
```
- Starts FastAPI server on port 8000
- Auto-reloads on code changes
- API docs at http://127.0.0.1:8000/docs

#### Frontend Only
```powershell
.\start-frontend.ps1
```
- Starts React dev server on port 3002
- Opens in browser (if BROWSER env is not set to 'none')
- Hot-reloads on code changes

### Option 3: Manual Start

#### Backend
```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend
```powershell
cd frontend
$env:REACT_APP_BACKEND_URL='http://localhost:8000'
$env:PORT='3002'
yarn start
```

## First Time Setup

### 1. Install Python Dependencies
```powershell
.venv\Scripts\pip install -r backend\requirements.txt
```

### 2. Install Frontend Dependencies
```powershell
cd frontend
yarn install
```

### 3. Configure Backend Environment

Create `backend/.env`:
```properties
MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/?appName=MGNREGAStorage"
DB_NAME="mgnrega"
REDIS_URL="redis://localhost:6379"
CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002"
```

### 4. Configure Frontend Environment

Create `frontend/.env.local`:
```properties
REACT_APP_BACKEND_URL=http://localhost:8000
BROWSER=none
```

## Accessing the Application

- **Dashboard**: http://localhost:3002
- **Backend API**: http://127.0.0.1:8000/api/
- **API Documentation**: http://127.0.0.1:8000/docs
- **Districts Endpoint**: http://127.0.0.1:8000/api/districts?state_code=UP

## Troubleshooting

### Port Already in Use
```powershell
# Kill process on port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }

# Kill process on port 3002
Get-NetTCPConnection -LocalPort 3002 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

### Backend Won't Start
- Check MongoDB connection string in `backend/.env`
- Ensure Python virtual environment is activated
- Check `backend/requirements.txt` dependencies are installed

### Frontend Shows "Failed to load districts"
- Verify backend is running at http://127.0.0.1:8000
- Check CORS settings in `backend/.env`
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)

### CORS Errors
- Ensure `backend/.env` includes your frontend port in `CORS_ORIGINS`
- Backend and frontend must use consistent hostnames (localhost vs 127.0.0.1)
- Current config supports both localhost and 127.0.0.1 on ports 3000-3002

## Stopping the Application

- Press `Ctrl+C` in each terminal window
- Or close the terminal windows
- Or use the port kill commands above

## Development Notes

- Backend auto-reloads on Python file changes
- Frontend hot-reloads on React file changes  
- Backend seeds 50 UP districts automatically on first run
- Mock data is generated for performance metrics
- No external MGNREGA API calls in current implementation
