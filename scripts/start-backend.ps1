# Start Backend Server Script
Set-Location "e:\Projects\MGNREGA_Finding\MGNREGA_Finding\backend"
& "E:\Projects\MGNREGA_Finding\MGNREGA_Finding\.venv\Scripts\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8000
