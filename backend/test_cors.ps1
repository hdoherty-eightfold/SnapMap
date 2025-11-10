# CORS Testing Script
# Tests if CORS is properly configured and working

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  CORS Configuration Test" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8001"
$origin = "http://localhost:5175"

# Test 1: Server health check
Write-Host "[Test 1] Server health check..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -ErrorAction Stop
    Write-Host "Server is running: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Server is not responding" -ForegroundColor Red
    Write-Host "Please start the backend server first" -ForegroundColor Red
    exit 1
}

# Test 2: Simple CORS request (with Origin header)
Write-Host ""
Write-Host "[Test 2] Simple CORS request..." -ForegroundColor Yellow
Write-Host "Testing: GET $baseUrl/health with Origin: $origin" -ForegroundColor Gray
try {
    $headers = @{
        "Origin" = $origin
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -Headers $headers -ErrorAction Stop

    $allowOrigin = $response.Headers["Access-Control-Allow-Origin"]
    $allowCreds = $response.Headers["Access-Control-Allow-Credentials"]

    if ($allowOrigin -eq $origin) {
        Write-Host "PASS: Access-Control-Allow-Origin = $allowOrigin" -ForegroundColor Green
    } elseif ($allowOrigin -eq "*") {
        Write-Host "PASS: Access-Control-Allow-Origin = * (wildcard)" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Access-Control-Allow-Origin = $allowOrigin (expected: $origin)" -ForegroundColor Red
    }

    if ($allowCreds -eq "true") {
        Write-Host "PASS: Access-Control-Allow-Credentials = true" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Request failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Preflight OPTIONS request
Write-Host ""
Write-Host "[Test 3] Preflight OPTIONS request..." -ForegroundColor Yellow
Write-Host "Testing: OPTIONS $baseUrl/api/entities" -ForegroundColor Gray
try {
    $headers = @{
        "Origin" = $origin
        "Access-Control-Request-Method" = "GET"
        "Access-Control-Request-Headers" = "content-type"
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/api/entities" -Method OPTIONS -Headers $headers -ErrorAction Stop

    $allowOrigin = $response.Headers["Access-Control-Allow-Origin"]
    $allowMethods = $response.Headers["Access-Control-Allow-Methods"]
    $allowHeaders = $response.Headers["Access-Control-Allow-Headers"]

    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green

    if ($allowOrigin -eq $origin -or $allowOrigin -eq "*") {
        Write-Host "PASS: Access-Control-Allow-Origin = $allowOrigin" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Access-Control-Allow-Origin = $allowOrigin" -ForegroundColor Red
    }

    if ($allowMethods) {
        Write-Host "PASS: Access-Control-Allow-Methods = $allowMethods" -ForegroundColor Green
    }

    if ($allowHeaders) {
        Write-Host "PASS: Access-Control-Allow-Headers = $allowHeaders" -ForegroundColor Green
    }

} catch {
    Write-Host "ERROR: Preflight request failed" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red

    # Try to read the response body
    try {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    } catch {
        Write-Host "Could not read response body" -ForegroundColor Gray
    }
}

# Test 4: Actual API endpoint
Write-Host ""
Write-Host "[Test 4] Actual API endpoint..." -ForegroundColor Yellow
Write-Host "Testing: GET $baseUrl/api/entities with Origin: $origin" -ForegroundColor Gray
try {
    $headers = @{
        "Origin" = $origin
    }
    $response = Invoke-WebRequest -Uri "$baseUrl/api/entities" -Method GET -Headers $headers -ErrorAction Stop

    $allowOrigin = $response.Headers["Access-Control-Allow-Origin"]

    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green

    if ($allowOrigin -eq $origin -or $allowOrigin -eq "*") {
        Write-Host "PASS: Access-Control-Allow-Origin = $allowOrigin" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Access-Control-Allow-Origin = $allowOrigin" -ForegroundColor Red
    }

} catch {
    Write-Host "WARNING: API endpoint failed (may be normal if endpoint requires data)" -ForegroundColor Yellow
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If all tests PASS, CORS is configured correctly." -ForegroundColor Green
Write-Host "If Test 3 (Preflight) FAILS, the frontend will not work." -ForegroundColor Yellow
Write-Host ""
Write-Host "Expected origins in backend CORS config:" -ForegroundColor Gray
Write-Host "  - http://localhost:5173" -ForegroundColor Gray
Write-Host "  - http://localhost:5174" -ForegroundColor Gray
Write-Host "  - http://localhost:5175" -ForegroundColor Gray
Write-Host "  - http://localhost:3000" -ForegroundColor Gray
Write-Host ""
