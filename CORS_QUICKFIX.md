# CORS Issue - Quick Fix Guide

## Problem
Frontend on `localhost:5175` cannot connect to backend on `localhost:8001` due to CORS errors.

## Quick Fix (Choose One)

### Option 1: Automated Fix (Recommended)
Run the automated restart script:

```powershell
cd c:\Code\SnapMap\backend
.\fix_cors_restart.ps1
```

This script will:
1. Kill all existing backend processes
2. Verify ports are free
3. Verify CORS configuration
4. Start fresh backend server on port 8001

### Option 2: Manual Fix

1. Kill all backend processes:
```powershell
Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -like "*uvicorn*"} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

2. Verify ports are free:
```powershell
netstat -ano | findstr ":8000 :8001"
```

3. Start backend server:
```bash
cd c:\Code\SnapMap\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Verify Fix

Run the CORS test script:
```powershell
cd c:\Code\SnapMap\backend
.\test_cors.ps1
```

All tests should PASS, especially Test 3 (Preflight OPTIONS request).

## Alternative: Temporary Wildcard CORS (Development Only)

If the issue persists, edit `c:\Code\SnapMap\backend\main.py`:

```python
# Change this line:
allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
],

# To this (TEMPORARILY):
allow_origins=["*"],  # WARNING: Development only!
```

Then restart the server.

## Root Cause

The backend process was not properly reloading after CORS configuration changes. A full restart is required to apply the updated CORS middleware settings.

## Detailed Analysis

See `c:\Code\SnapMap\docs\incident-cors-analysis.md` for complete root cause analysis and technical details.
