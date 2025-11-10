# CORS Incident - Root Cause Analysis

**Date**: 2025-11-05
**Severity**: HIGH
**Status**: IDENTIFIED - READY FOR RESOLUTION
**Reporter**: DevOps Incident Response

---

## Executive Summary

The CORS error "No 'Access-Control-Allow-Origin' header is present" is occurring because the backend CORS middleware is NOT responding with the required `Access-Control-Allow-Origin` header for preflight OPTIONS requests from `http://localhost:5175`. While the CORS configuration in `backend/main.py` correctly includes port 5175, the FastAPI CORS middleware is rejecting the origin with "Disallowed CORS origin" error.

---

## Incident Timeline

1. Backend CORS configuration was updated to include ports 5173, 5174, 5175, and 3000
2. Backend server restarted multiple times
3. CORS errors persist on frontend (localhost:5175) when trying to connect to backend (localhost:8001)
4. Multiple zombie processes detected on port 8000

---

## Root Cause Analysis

### Critical Finding: CORS Preflight Request Failure

Testing revealed that:

1. **Simple GET requests work** - When testing with `curl` using `Origin: http://localhost:5175` header, the backend responds WITHOUT the `Access-Control-Allow-Origin` header but doesn't reject it
2. **Preflight OPTIONS requests fail** - The CORS middleware explicitly returns "Disallowed CORS origin" (400 Bad Request) for OPTIONS requests

```bash
# Test output showing the issue:
curl -X OPTIONS -H "Origin: http://localhost:5175" \
  -H "Access-Control-Request-Method: GET" \
  http://localhost:8001/api/schema/source

< HTTP/1.1 400 Bad Request
< vary: Origin
< access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
< access-control-max-age: 600
< access-control-allow-credentials: true
Disallowed CORS origin
```

### Why This is Happening

The issue is that the FastAPI CORSMiddleware is configured correctly in the code at `c:\Code\SnapMap\backend\main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server (alternative port)
        "http://localhost:5175",  # Vite dev server (alternative port)
        "http://localhost:3000",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**However**, the running backend process (PID 68900) on port 8001 may have been started from a different directory or is not reflecting the current code changes despite using `--reload` flag.

---

## Evidence Collected

### Process Information

**Backend Process on Port 8001:**
- **PID**: 68900
- **Command**: `"C:\Program Files\Python312\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 8001`
- **Started**: 2025-11-04 22:47:52 (over 15 hours ago)
- **Note**: The process was started with `--reload` but may not be properly reloading after CORS changes

**Zombie Processes on Port 8000:**
- PID 40572 - Status: Cannot be found (likely stale netstat cache)
- PID 63548 - Status: Cannot be found (likely stale netstat cache)
- PID 51680 - Status: Cannot be found (likely stale netstat cache)

**Frontend Process:**
- **Port**: 5175
- **PID**: 70424 (Node.js)
- **Browser**: PID 18604 (Chrome)

### Network Configuration

**Frontend Environment** (`c:\Code\SnapMap\frontend\.env`):
```
VITE_API_URL=http://localhost:8001/api
```

**API Client Configuration** (`c:\Code\SnapMap\frontend\src\services\api.ts`):
```typescript
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```
This correctly uses port 8001 from the .env file.

### Test Results

1. **Health endpoint test** (Simple request):
   - Response: 200 OK
   - CORS headers: `access-control-allow-credentials: true`
   - **Missing**: `Access-Control-Allow-Origin` header

2. **Preflight OPTIONS test** (CORS preflight):
   - Response: 400 Bad Request
   - Error: "Disallowed CORS origin"
   - Headers sent: `access-control-allow-methods`, `access-control-allow-credentials`
   - **Missing**: `Access-Control-Allow-Origin` header

---

## Why CORS is Failing

The FastAPI CORSMiddleware has specific behavior for preflight requests:

1. When a browser sends an OPTIONS preflight request with `Origin: http://localhost:5175`
2. The middleware checks if the origin is in the `allow_origins` list
3. **The middleware is rejecting the origin** even though it's in the configuration
4. This suggests one of the following:
   - The running process is using an old version of the code
   - The middleware is not properly initialized
   - There's a caching issue with uvicorn's auto-reload

---

## Impact Assessment

**Severity**: HIGH
- Frontend completely unable to make API calls
- All application functionality blocked
- User experience: Complete application failure

**Affected Components**:
- Frontend application (localhost:5175)
- All API endpoints on backend (localhost:8001)
- File upload, schema loading, auto-mapping, transformation features

---

## Recommended Action Plan

### Immediate Fix (5 minutes)

1. **Kill all backend processes**:
   ```powershell
   # Kill process on port 8001
   Stop-Process -Id 68900 -Force

   # Verify port is free
   netstat -ano | findstr ":8001"
   ```

2. **Restart backend from correct directory**:
   ```bash
   cd c:\Code\SnapMap\backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

3. **Verify CORS is working**:
   ```bash
   # Test preflight request
   curl -X OPTIONS \
     -H "Origin: http://localhost:5175" \
     -H "Access-Control-Request-Method: GET" \
     -v http://localhost:8001/api/entities

   # Should return 200 OK with Access-Control-Allow-Origin header
   ```

4. **Test from frontend**:
   - Open browser console
   - Navigate to application
   - Check for CORS errors
   - Verify API calls succeed

### Alternative Fix: Wildcard CORS (Development Only)

If the issue persists, temporarily use wildcard CORS for debugging:

```python
# In backend/main.py, change allow_origins to:
allow_origins=["*"]  # WARNING: Development only!
```

Then restart the server.

### Long-term Prevention

1. **Add startup verification script**:
   Create `c:\Code\SnapMap\backend\verify_cors.py` to check CORS on startup

2. **Add health endpoint with CORS info**:
   ```python
   @app.get("/api/cors-check")
   async def cors_check():
       return {
           "allowed_origins": [
               "http://localhost:5173",
               "http://localhost:5174",
               "http://localhost:5175",
               "http://localhost:3000"
           ],
           "status": "configured"
       }
   ```

3. **Add process management script**:
   Create a startup script that:
   - Kills any existing processes on ports 8000/8001
   - Starts fresh backend server
   - Verifies CORS is working

4. **Monitor for zombie processes**:
   ```bash
   # Add to startup script
   netstat -ano | findstr ":8000 :8001"
   ```

---

## Technical Deep Dive

### FastAPI CORS Middleware Behavior

The FastAPI CORSMiddleware (from Starlette) handles CORS in two phases:

1. **Preflight (OPTIONS request)**:
   - Checks if `Origin` header matches `allow_origins`
   - If match: responds with CORS headers and 200 OK
   - If no match: responds with 400 Bad Request and "Disallowed CORS origin"

2. **Actual request (GET/POST/etc.)**:
   - Adds `Access-Control-Allow-Origin` header if origin matches
   - Processes the request normally

Our test showed that the preflight phase is failing, which prevents the browser from making the actual request.

### Why Auto-reload Might Not Work

Uvicorn's `--reload` flag watches for file changes, but:
- May not detect changes in some circumstances
- Can have issues with Windows file system watching
- Does not reload if the process is started from wrong directory
- Module imports are cached and may not refresh properly

---

## Monitoring Queries

### Check if CORS is working:
```bash
curl -v -X OPTIONS \
  -H "Origin: http://localhost:5175" \
  -H "Access-Control-Request-Method: GET" \
  http://localhost:8001/api/entities 2>&1 | grep "Access-Control-Allow-Origin"
```

Should output: `< access-control-allow-origin: http://localhost:5175`

### Check for zombie processes:
```bash
netstat -ano | findstr "LISTENING" | findstr ":8000 :8001"
```

Should show only one process per port.

### Verify backend is running from correct directory:
```bash
wmic process where "ProcessId=<PID>" get CommandLine
```

---

## Post-Incident Action Items

1. Create automated startup/shutdown scripts for development
2. Add CORS verification to CI/CD pipeline
3. Document proper server restart procedure
4. Add monitoring for zombie processes
5. Consider using Docker for local development to avoid port conflicts
6. Add CORS status to application health check endpoint

---

## Files Modified/Created

- None (diagnosis only)
- Created: `c:\Code\SnapMap\backend\check_cors.py` (diagnostic tool)
- Created: `c:\Code\SnapMap\docs\incident-cors-analysis.md` (this document)

---

## Conclusion

The CORS configuration in the code is correct, but the running backend process is not properly enforcing it. The most likely cause is that the uvicorn process needs to be completely restarted (not just auto-reloaded) to pick up the CORS middleware configuration changes.

**Next Step**: Execute the "Immediate Fix" action plan to resolve the issue.
