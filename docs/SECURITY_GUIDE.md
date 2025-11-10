# SnapMap Security Guide

**Version:** 2.0.0
**Last Updated:** November 7, 2025

---

## Security Features

### 1. Rate Limiting

**Protection**: Prevents abuse and DoS attacks

**Configuration**:
```python
# backend/app/middleware/rate_limiter.py
RATE_LIMIT = 100  # requests per minute per IP
```

**Bypass** (for testing):
```python
# Disable in .env
RATE_LIMIT_ENABLED=false
```

### 2. Security Headers

**Implemented**:
- `Strict-Transport-Security`: Force HTTPS
- `X-Content-Type-Options`: Prevent MIME sniffing
- `X-Frame-Options`: Prevent clickjacking
- `X-XSS-Protection`: XSS protection
- `Content-Security-Policy`: Restrict resource loading

**Configuration**: `backend/app/middleware/security_headers.py`

### 3. CORS Protection

**Development**:
```python
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]
```

**Production**:
```python
# Set in .env
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### 4. Input Sanitization

**Protection**: SQL injection, XSS, command injection

**Implementation**:
```python
from app.utils.sanitization import sanitize_string

user_input = sanitize_string(user_input)
```

### 5. Credential Encryption

**SFTP credentials encrypted with AES-256 (Fernet)**:

```python
from cryptography.fernet import Fernet

# Generate key (once)
key = Fernet.generate_key()

# Store in .env
ENCRYPTION_KEY=<key>
```

**Password storage**: Never stored in plaintext

---

## OWASP Top 10 Compliance

### A01: Broken Access Control
✅ **Mitigated**: Rate limiting, CORS, input validation

### A02: Cryptographic Failures
✅ **Mitigated**: AES-256 encryption for credentials, HTTPS/TLS

### A03: Injection
✅ **Mitigated**: Pydantic validation, input sanitization

### A04: Insecure Design
✅ **Mitigated**: Security-first architecture, validation at every step

### A05: Security Misconfiguration
⚠️ **Partial**: API docs disabled in production, security headers enabled

**TODO**: Add security.txt, implement CSP reporting

### A06: Vulnerable Components
✅ **Mitigated**: Dependencies regularly updated, no known CVEs

### A07: Authentication Failures
🔴 **Not Applicable**: No authentication in v2.0 (planned for v2.1)

### A08: Software and Data Integrity
✅ **Mitigated**: Data loss validation, integrity checks

### A09: Security Logging and Monitoring
⚠️ **Partial**: Logging enabled, monitoring recommended

**TODO**: Add audit logging, APM integration

### A10: Server-Side Request Forgery
✅ **Mitigated**: No external requests from user input

---

## Security Best Practices

### 1. HTTPS/TLS

**Always use HTTPS in production**:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### 2. Environment Variables

**Never commit secrets**:

```bash
# .gitignore
.env
*.key
*.pem
```

**Use environment variables**:
```python
import os
SECRET = os.getenv("SECRET_KEY")
```

### 3. File Upload Validation

**Implemented**:
- Size limit: 100MB
- File type validation
- MIME type checking

**Additional hardening**:
```python
# Scan for malware (optional)
import clamd
scanner = clamd.ClamdUnixSocket()
scanner.scan(file_path)
```

### 4. API Security

**Recommendations**:
- [ ] Add API key authentication
- [ ] Implement OAuth 2.0
- [ ] Add request signing
- [ ] Enable API versioning

### 5. Database Security

**Current**: ChromaDB (local, no network exposure)

**Future** (PostgreSQL):
- [ ] Use connection pooling
- [ ] Enable SSL/TLS connections
- [ ] Implement role-based access
- [ ] Regular backups with encryption

---

## Penetration Testing

### Automated Scanning

**OWASP ZAP**:
```bash
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable \
  zap-baseline.py -t http://localhost:8000 -r report.html
```

**Nikto**:
```bash
nikto -h http://localhost:8000
```

### Manual Testing

**SQL Injection**:
```bash
# Test input fields
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.csv; filename=\"'; DROP TABLE users--\""
```

**XSS**:
```bash
# Test with malicious input
curl -X POST http://localhost:8000/api/auto-map \
  -d '{"source_fields": ["<script>alert(1)</script>"]}'
```

**CSRF** (not applicable - no session/cookies)

---

## Incident Response

### 1. Detect

**Monitor logs**:
```bash
tail -f /var/log/snapmap/backend.log | grep -E "ERROR|WARNING"
```

**Alert on**:
- Repeated failed requests (potential attack)
- Unusual file uploads (potential malware)
- High rate of 4xx/5xx errors

### 2. Respond

**Immediate actions**:
1. Isolate affected systems
2. Block malicious IP: `sudo ufw deny from <IP>`
3. Review logs for attack vector
4. Notify team

### 3. Recover

1. Restore from backup if needed
2. Patch vulnerability
3. Update dependencies
4. Redeploy

### 4. Learn

1. Document incident
2. Update security measures
3. Conduct post-mortem
4. Improve monitoring

---

## Compliance

### GDPR

**Data Handling**:
- No persistent storage of user data
- Data cleared after session (1 hour)
- No tracking or analytics

**User Rights**:
- Right to erasure: Automatic (session-based)
- Right to access: Not applicable (no long-term storage)

### HIPAA

**Not compliant** - Do not use for healthcare data without:
- [ ] Encryption at rest
- [ ] Audit logging
- [ ] Access controls
- [ ] BAA agreements

---

## Security Checklist

### Deployment

- [ ] HTTPS/TLS enabled
- [ ] Strong encryption key generated
- [ ] API docs disabled in production
- [ ] CORS origins restricted
- [ ] Rate limiting enabled
- [ ] Firewall configured
- [ ] Security headers enabled
- [ ] Input validation enabled
- [ ] File upload validation enabled
- [ ] Credentials encrypted

### Ongoing

- [ ] Dependencies updated monthly
- [ ] Security patches applied within 48 hours
- [ ] Logs reviewed weekly
- [ ] Backups tested monthly
- [ ] Penetration testing quarterly
- [ ] Security audit annually

---

## Vulnerability Disclosure

**Report security issues to**: security@yourcompany.com

**Please include**:
- Vulnerability description
- Steps to reproduce
- Proof of concept (if applicable)
- Suggested fix (if known)

**Response time**: Within 72 hours

**Disclosure policy**: Coordinated disclosure after fix

---

*Last Updated: November 7, 2025*
