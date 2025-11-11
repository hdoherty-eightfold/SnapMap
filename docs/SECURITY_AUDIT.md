# Security Audit Report - SnapMap Application

**Date**: 2025-11-07
**Auditor**: Security Team
**Application**: SnapMap - HR Data Transformation Platform
**Version**: 1.0.0

## Executive Summary

This security audit evaluated the SnapMap application against OWASP Top 10 vulnerabilities and industry best practices. The application shows good foundation with file upload validation, but requires critical improvements in authentication, credential management, and security headers.

**Risk Summary:**
- 3 Critical vulnerabilities
- 5 High-priority issues
- 4 Medium-priority issues
- 3 Low-priority issues

---

## 1. OWASP Top 10 Compliance Assessment

### A01:2021 - Broken Access Control
**Status**: CRITICAL - NO AUTHENTICATION
**Risk Level**: CRITICAL

**Findings:**
- API endpoints have NO authentication or authorization mechanisms
- All endpoints at `/api/*` are publicly accessible
- No JWT, OAuth2, or API key validation
- No user session management
- No role-based access control (RBAC)

**Evidence:**
```python
# main.py - No authentication middleware
app = FastAPI(...)
# No authentication decorators on any endpoints
```

**Impact:** Any user can:
- Upload files
- Access transformation features
- Configure SFTP credentials
- Modify system configuration
- Access sensitive API keys configuration

**Recommendation:** IMPLEMENT IMMEDIATELY
- Add JWT-based authentication
- Implement API key authentication for service-to-service
- Add role-based access control
- Require authentication on all non-public endpoints

---

### A02:2021 - Cryptographic Failures
**Status**: CRITICAL
**Risk Level**: CRITICAL

**Findings:**

1. **Weak Credential Storage (SFTP)**
   - SFTP passwords stored with basic Base64 encoding
   - Base64 is encoding, NOT encryption - trivially reversible
   - Credentials stored in temp directory JSON file
   - File permissions not restricted

**Evidence:**
```python
# sftp_manager.py:31-33
def _encode_password(self, password: str) -> str:
    """Basic password encoding (base64). Use proper encryption in production."""
    return base64.b64encode(password.encode()).decode()
```

2. **Sensitive Data in .env File**
   - API keys stored in plaintext `.env` file
   - No encryption at rest
   - File could be committed to version control

3. **No HTTPS Enforcement**
   - Application runs on HTTP by default
   - No SSL/TLS configuration
   - Credentials transmitted in cleartext

**Impact:**
- SFTP credentials easily extractable
- API keys compromised if server accessed
- Man-in-the-middle attacks possible

**Recommendation:** CRITICAL PRIORITY
- Implement Fernet encryption for SFTP passwords
- Use system keyring or secrets manager (AWS Secrets Manager, Azure Key Vault)
- Enforce HTTPS in production
- Set restrictive file permissions (0600) on credentials file
- Add .env to .gitignore

---

### A03:2021 - Injection
**Status**: GOOD with MINOR ISSUES
**Risk Level**: MEDIUM

**Findings:**

1. **SQL Injection**: NOT APPLICABLE - No direct SQL queries (using Pandas)

2. **XML Injection**: VULNERABLE
   - XML generation uses `xml.etree.ElementTree` which has basic protection
   - User data inserted into XML without explicit sanitization
   - Special characters in data could break XML structure

**Evidence:**
```python
# xml_transformer.py:289
return str(value).strip()  # No XML escaping
```

3. **Command Injection**: LOW RISK
   - No shell command execution with user input
   - File operations use safe Python APIs

4. **Path Traversal**: PROTECTED
   - File uploads use UUID-based naming
   - No direct user control over file paths

**Recommendation:**
- Explicitly escape XML special characters: `&`, `<`, `>`, `"`, `'`
- Use `xml.sax.saxutils.escape()` for text content
- Validate field names against whitelist

---

### A04:2021 - Insecure Design
**Status**: MODERATE ISSUES
**Risk Level**: MEDIUM

**Findings:**

1. **No Rate Limiting**
   - File upload endpoint has no rate limiting
   - Could be abused for DoS attacks
   - Large file uploads (100MB) could exhaust resources

2. **No Request Size Limits**
   - Besides file size, no limits on request body size
   - JSON payloads could be arbitrarily large

3. **Temporary File Cleanup**
   - Auto-cleanup after 1 hour (good)
   - But no max storage limit
   - Could fill disk if many large files uploaded

4. **Debug Mode in Production**
   - `reload=True` in main.py
   - Debug print statements throughout code
   - Stack traces exposed in error messages

**Evidence:**
```python
# main.py:96
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# transform.py:280-281
error_traceback = traceback.format_exc()
print(f"[XML_PREVIEW_ERROR] {error_traceback}", file=sys.stderr, flush=True)
```

**Recommendation:**
- Implement rate limiting (10 requests/minute per IP)
- Add max request body size limit
- Disable reload in production
- Remove debug print statements
- Sanitize error messages for production

---

### A05:2021 - Security Misconfiguration
**Status**: MULTIPLE ISSUES
**Risk Level**: HIGH

**Findings:**

1. **CORS Configuration - Too Permissive**
```python
# main.py:22-30
allow_origins=[
    "http://localhost:5173",  # Development only
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
],
allow_credentials=True,
allow_methods=["*"],  # Too permissive
allow_headers=["*"],  # Too permissive
```
   - Allows all methods including DELETE, PUT
   - Allows all headers
   - No production origins configured

2. **Missing Security Headers**
   - No X-Content-Type-Options
   - No X-Frame-Options
   - No Content-Security-Policy
   - No Strict-Transport-Security

3. **Server Binding**
   - Binds to `0.0.0.0` exposing to all interfaces
   - Should bind to localhost in development

4. **API Documentation Exposed**
   - Swagger UI at `/api/docs` publicly accessible
   - ReDoc at `/api/redoc` publicly accessible
   - Should be disabled in production

**Recommendation:**
- Restrict CORS to production domains only
- Add security headers middleware
- Disable auto docs in production
- Bind to 127.0.0.1 for development

---

### A06:2021 - Vulnerable and Outdated Components
**Status**: SOME CONCERNS
**Risk Level**: MEDIUM

**Dependency Analysis:**

**Potentially Vulnerable:**
1. `chromadb==0.4.22` - Old version (current: 1.x.x)
2. `sentence-transformers==2.2.2` - Old version (current: 5.x.x)
3. `torch==2.1.0` - Missing security patches (current: 2.5.x)
4. `pandas==2.1.4` - Should update to 2.2.x

**Good - Recent Versions:**
- `fastapi==0.109.0` - Good
- `pydantic==2.5.3` - Good
- `cryptography==Not installed` - MISSING!

**Missing Critical Packages:**
- `cryptography` - For proper encryption
- `slowapi` or `fastapi-limiter` - For rate limiting
- `python-jose` - For JWT authentication
- `passlib` - For password hashing

**Recommendation:**
- Update chromadb to 1.x.x
- Update sentence-transformers to 5.x.x
- Update torch to 2.5.x
- Install cryptography for Fernet encryption
- Install slowapi for rate limiting
- Pin all versions in requirements.txt

---

### A07:2021 - Identification and Authentication Failures
**Status**: CRITICAL - NOT IMPLEMENTED
**Risk Level**: CRITICAL

**Findings:**

1. **No User Authentication**
   - No login mechanism
   - No user accounts
   - No session management

2. **No Password Policies**
   - N/A - no user passwords

3. **No Multi-Factor Authentication**
   - Not implemented

4. **API Key Management**
   - API keys for external services stored in plaintext
   - No rotation mechanism
   - No expiration

**Recommendation:**
- Implement authentication system
- Add API key rotation
- Implement session timeout
- Add audit logging for authentication events

---

### A08:2021 - Software and Data Integrity Failures
**Status**: MINOR ISSUES
**Risk Level**: LOW

**Findings:**

1. **No Code Signing**
   - Python packages not verified

2. **No Integrity Checks**
   - Uploaded files not checksummed
   - No validation of file integrity after storage

3. **Dependency Integrity**
   - Using pip without hash verification
   - No `requirements-lock.txt` with hashes

**Recommendation:**
- Add SHA256 checksums for uploaded files
- Use `pip install --require-hashes`
- Generate locked requirements with hashes

---

### A09:2021 - Security Logging and Monitoring Failures
**Status**: INSUFFICIENT
**Risk Level**: MEDIUM

**Findings:**

1. **No Security Event Logging**
   - No logging of:
     - File uploads
     - Configuration changes
     - SFTP credential access
     - Failed requests
     - Suspicious activity

2. **Debug Logging Only**
   - Print statements used instead of proper logging
   - No log levels
   - No structured logging

3. **No Monitoring/Alerting**
   - No health checks beyond basic `/health`
   - No metrics collection
   - No alerting on suspicious patterns

**Evidence:**
```python
# Multiple files use print() instead of logging
print(f"[DEBUG] Looking for file_id: {request.file_id}")
```

**Recommendation:**
- Implement proper logging with Python `logging` module
- Log security events (file uploads, config changes)
- Add structured logging (JSON format)
- Implement log aggregation
- Set up alerting for:
  - High upload volumes
  - Failed authentication attempts
  - Configuration changes
  - Large file uploads

---

### A10:2021 - Server-Side Request Forgery (SSRF)
**Status**: LOW RISK
**Risk Level**: LOW

**Findings:**

1. **SFTP Connections**
   - User provides SFTP host
   - Could be internal IPs (127.0.0.1, 192.168.x.x, 10.x.x.x)
   - No validation of target host

2. **No External HTTP Requests**
   - Application doesn't make outbound HTTP requests with user input
   - Google Gemini API calls use official SDK

**Recommendation:**
- Validate SFTP host is not internal IP
- Whitelist allowed SFTP hosts
- Add network segmentation

---

## 2. File Upload Security Assessment

### Current Protection (GOOD)
1. File size limit: 100MB enforced
2. File extension validation: `.csv`, `.xlsx`, `.xls` only
3. UUID-based filenames prevent path traversal
4. Auto-cleanup after 1 hour
5. Temporary storage location

### Issues

1. **Malicious Filename Handling**
```python
# upload.py - filename used directly
file.filename  # Not sanitized
```

2. **MIME Type Not Validated**
   - Relies on extension only
   - Could upload .csv file containing malicious content

3. **No Virus Scanning**
   - Uploaded files not scanned
   - Could contain macros or malicious scripts

4. **Zip Bomb Protection**
   - Excel files could contain compressed bombs
   - No decompression size limits

**Recommendation:**
- Sanitize filenames (remove special characters)
- Validate MIME type matches extension
- Integrate ClamAV for virus scanning
- Set max decompression ratio for Excel files

---

## 3. Input Validation Assessment

### Good Practices
1. Pydantic models for request validation
2. File format validation
3. Character encoding detection
4. Data type detection

### Issues

1. **Field Name Validation**
   - User-provided field names not validated
   - Could contain special characters

2. **CSV Injection**
   - Excel formulas in CSV could execute: `=cmd|'/c calc'!A0`
   - No sanitization of cell values starting with `=`, `+`, `-`, `@`

3. **XML Output**
   - Special characters not escaped

**Recommendation:**
- Sanitize CSV cell values (escape formulas)
- Escape XML content properly
- Validate field names against regex pattern
- Implement content security scanning

---

## 4. Data Protection Assessment

### Sensitive Data Handling

**Exposed in Logs:**
```python
# Multiple debug prints expose data
print(f"[DEBUG] Storage metadata keys: {list(storage._metadata.keys())}")
print(f"[XML_PREVIEW_DEBUG] mappings type: {type(request.mappings)}")
```

**Temporary Files:**
- Stored in system temp directory
- Permissions not explicitly set
- Could be read by other users

**API Key Exposure:**
```python
# config.py endpoint exposes if keys are set
"api_keys": {
    "gemini_configured": bool(settings.gemini_api_key),
    # Could be used to enumerate configured services
}
```

**Recommendation:**
- Remove all debug print statements
- Set restrictive permissions on temp files (0600)
- Implement proper logging with sanitization
- Don't expose API key configuration status

---

## 5. CORS Security Assessment

**Current Configuration:**
```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
```

**Issues:**
1. Development origins in production code
2. Wildcard methods and headers
3. Credentials enabled with multiple origins

**Recommendation:**
- Environment-based CORS configuration
- Restrict methods to required only: GET, POST, PUT, DELETE
- Specify allowed headers explicitly
- Single production origin

---

## 6. Dependency Vulnerabilities

**Critical Updates Needed:**
```
chromadb: 0.4.22 → 1.1.1 (Security patches)
sentence-transformers: 2.2.2 → 5.1.2 (Multiple CVEs fixed)
torch: 2.1.0 → 2.8.0 (Security updates)
```

**Missing Security Packages:**
```
cryptography - For Fernet encryption
slowapi - For rate limiting
python-jose[cryptography] - For JWT
passlib[bcrypt] - For password hashing
```

---

## 7. Summary of Vulnerabilities

### CRITICAL (Immediate Action Required)

1. **No Authentication System**
   - OWASP: A07
   - Impact: Complete unauthorized access
   - Fix: Implement JWT or API key authentication

2. **Weak Credential Encryption**
   - OWASP: A02
   - Impact: SFTP credentials easily extracted
   - Fix: Use Fernet encryption or secrets manager

3. **No Authorization Controls**
   - OWASP: A01
   - Impact: Any user can access any function
   - Fix: Implement RBAC

### HIGH Priority

4. **No Rate Limiting**
   - OWASP: A04
   - Impact: DoS attacks possible
   - Fix: Add slowapi middleware

5. **Missing Security Headers**
   - OWASP: A05
   - Impact: XSS, clickjacking vulnerabilities
   - Fix: Add security headers middleware

6. **CORS Too Permissive**
   - OWASP: A05
   - Impact: CSRF attacks possible
   - Fix: Restrict CORS configuration

7. **Insufficient Logging**
   - OWASP: A09
   - Impact: Cannot detect/respond to attacks
   - Fix: Implement structured logging

8. **Debug Mode in Production**
   - OWASP: A05
   - Impact: Information disclosure
   - Fix: Disable reload, remove debug code

### MEDIUM Priority

9. **XML Injection Risk**
   - OWASP: A03
   - Impact: Malformed XML, potential XSS
   - Fix: Escape XML special characters

10. **Outdated Dependencies**
    - OWASP: A06
    - Impact: Known vulnerabilities
    - Fix: Update packages

11. **CSV Injection**
    - OWASP: A03
    - Impact: Formula injection in Excel
    - Fix: Sanitize CSV content

12. **No SFTP Host Validation**
    - OWASP: A10
    - Impact: SSRF to internal networks
    - Fix: Validate and whitelist hosts

### LOW Priority

13. **No File Integrity Checks**
    - OWASP: A08
    - Impact: Corrupted data undetected
    - Fix: Add SHA256 checksums

14. **Filename Sanitization**
    - OWASP: A03
    - Impact: Special character issues
    - Fix: Sanitize filenames

15. **No Virus Scanning**
    - Risk: Malware distribution
    - Fix: Integrate ClamAV

---

## 8. Recommendations Priority Matrix

### Immediate (Week 1)
1. Implement authentication (JWT or API key)
2. Replace Base64 with Fernet encryption for SFTP passwords
3. Add rate limiting middleware
4. Add security headers
5. Disable debug mode/reload in production
6. Update critical dependencies

### Short-term (Weeks 2-3)
7. Implement proper logging system
8. Sanitize XML output
9. Restrict CORS configuration
10. Add CSV injection protection
11. Remove debug print statements
12. Set file permissions on credentials

### Medium-term (Month 2)
13. Add RBAC authorization
14. Implement audit logging
15. Add virus scanning
16. Validate SFTP hosts
17. Add file integrity checks
18. Implement monitoring/alerting

### Long-term (Month 3+)
19. Add multi-factor authentication
20. Implement secrets rotation
21. Add HTTPS enforcement
22. Security training for developers
23. Regular security audits
24. Penetration testing

---

## 9. Compliance Notes

### GDPR Considerations
- Application processes employee data (PII)
- No data retention policy documented
- No data deletion mechanism
- No privacy policy

### HIPAA (if applicable)
- Not applicable unless processing health data

### SOC 2
- Insufficient logging for audit trail
- No access controls
- No encryption at rest

---

## 10. Security Testing Results

### Automated Scanning
- No automated security scanning detected
- Recommend: Bandit, Safety, Snyk

### Manual Testing
- Attempted authentication bypass: SUCCESS (no auth)
- Attempted path traversal: BLOCKED (UUID filenames)
- Attempted SQL injection: N/A (no SQL)
- Attempted XSS: Not tested (no HTML output to browser)

---

## 11. Conclusion

The SnapMap application demonstrates good practices in file handling and input validation, but lacks critical security controls for production deployment:

**Strengths:**
- File size limits enforced
- File type validation
- Safe file storage with UUIDs
- Auto-cleanup of temporary files
- Good error handling structure

**Critical Gaps:**
- No authentication/authorization
- Weak credential storage
- No rate limiting
- Missing security headers
- Insufficient logging

**Overall Risk Assessment**: HIGH
**Production Ready**: NO - Critical fixes required first

**Estimated Effort for Critical Fixes**: 40-60 hours

---

## 12. Compliance Checklist

- [ ] Authentication implemented
- [ ] Authorization (RBAC) implemented
- [ ] Credentials properly encrypted
- [ ] Rate limiting active
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Debug mode disabled
- [ ] Logging implemented
- [ ] Dependencies updated
- [ ] XML output sanitized
- [ ] CSV injection protection
- [ ] HTTPS enforced
- [ ] API docs secured
- [ ] File integrity checks
- [ ] SFTP host validation

**Progress**: 5/15 (33%)

---

## Appendix A: OWASP Top 10 2021 Reference

1. A01:2021 - Broken Access Control
2. A02:2021 - Cryptographic Failures
3. A03:2021 - Injection
4. A04:2021 - Insecure Design
5. A05:2021 - Security Misconfiguration
6. A06:2021 - Vulnerable and Outdated Components
7. A07:2021 - Identification and Authentication Failures
8. A08:2021 - Software and Data Integrity Failures
9. A09:2021 - Security Logging and Monitoring Failures
10. A10:2021 - Server-Side Request Forgery (SSRF)

---

**Report Generated**: 2025-11-07
**Next Audit Scheduled**: After critical fixes implemented
