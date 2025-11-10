# CORS Fix - Clean Restart Script
# This script kills all backend processes and restarts the server cleanly

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  CORS Fix - Backend Clean Restart" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find and kill all Python processes running uvicorn
Write-Host "[1/5] Searching for uvicorn processes..." -ForegroundColor Yellow
$uvicornProcesses = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*uvicorn*" -and $_.Name -eq "python.exe"
}

if ($uvicornProcesses) {
    Write-Host "Found $($uvicornProcesses.Count) uvicorn process(es)" -ForegroundColor Green
    foreach ($proc in $uvicornProcesses) {
        Write-Host "  Killing PID $($proc.ProcessId): $($proc.CommandLine)" -ForegroundColor Gray
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
} else {
    Write-Host "No uvicorn processes found" -ForegroundColor Gray
}

# Step 2: Verify ports 8000 and 8001 are free
Write-Host ""
Write-Host "[2/5] Checking if ports 8000 and 8001 are free..." -ForegroundColor Yellow
$portsInUse = netstat -ano | Select-String -Pattern ":8000\s|:8001\s" | Select-String "LISTENING"

if ($portsInUse) {
    Write-Host "WARNING: Ports still in use:" -ForegroundColor Red
    $portsInUse | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Attempting to kill processes on these ports..." -ForegroundColor Yellow

    # Extract PIDs and kill them
    $portsInUse | ForEach-Object {
        if ($_ -match '\s+(\d+)$') {
            $pid = $matches[1]
            Write-Host "  Killing PID $pid" -ForegroundColor Gray
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2

    # Check again
    $portsInUse = netstat -ano | Select-String -Pattern ":8000\s|:8001\s" | Select-String "LISTENING"
    if ($portsInUse) {
        Write-Host "ERROR: Could not free ports. Please manually kill processes:" -ForegroundColor Red
        $portsInUse | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        exit 1
    }
}
Write-Host "Ports 8000 and 8001 are free" -ForegroundColor Green

# Step 3: Navigate to backend directory
Write-Host ""
Write-Host "[3/5] Navigating to backend directory..." -ForegroundColor Yellow
$backendDir = Split-Path -Parent $PSScriptRoot
if (-not $backendDir) {
    $backendDir = "c:\Code\SnapMap\backend"
}
Set-Location $backendDir
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Green

# Step 4: Verify CORS configuration in main.py
Write-Host ""
Write-Host "[4/5] Verifying CORS configuration..." -ForegroundColor Yellow
$mainPyPath = Join-Path $backendDir "main.py"
if (Test-Path $mainPyPath) {
    $corsConfig = Select-String -Path $mainPyPath -Pattern "localhost:5175" -Context 0,0
    if ($corsConfig) {
        Write-Host "CORS configuration includes localhost:5175: VERIFIED" -ForegroundColor Green
    } else {
        Write-Host "WARNING: localhost:5175 not found in CORS config" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: main.py not found at $mainPyPath" -ForegroundColor Red
    exit 1
}

# Step 5: Start the backend server
Write-Host ""
Write-Host "[5/5] Starting backend server..." -ForegroundColor Yellow
Write-Host "Command: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001" -ForegroundColor Gray
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Server starting... Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
