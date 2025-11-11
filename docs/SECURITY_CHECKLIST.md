# Security Hardening Checklist

Quick reference checklist for SnapMap security implementation and deployment.

## Pre-Deployment Checklist

### Critical (Must Complete Before Production)

- [ ] **Install Security Dependencies**
  ```bash
  pip install cryptography==42.0.5
  pip install python-jose[cryptography]==3.3.0
  pip install passlib[bcrypt]==1.7.4
  ```

- [ ] **Generate Encryption Key**
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
  Add to `.env` as `ENCRYPTION_KEY=...`

- [ ] **Set Environment to Production**
  ```env
  ENVIRONMENT=production
  ```

- [ ] **Configure CORS Origins**
  ```env
  CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
  ```

- [ ] **Disable Debug Mode**
  ```env
  DEBUG_MODE=false
  ```

- [ ] **Secure .env File**
  ```bash
  chmod 600 .env
  echo ".env" >> .gitignore
  ```

- [ ] **Test Security Features**
  - [ ] Rate limiting active
  - [ ] Security headers present
  - [ ] CORS restrictions working
  - [ ] Encryption functional

### High Priority (Complete Within 1 Week)

- [ ] **Update Dependencies**
  ```bash
  pip install -r requirements-updated.txt
  ```

- [ ] **Set Up HTTPS**
  - [ ] SSL certificate obtained
  - [ ] Reverse proxy configured (Nginx/Caddy)
  - [ ] HTTP redirects to HTTPS

- [ ] **Implement Authentication**
  - [ ] Choose auth method (JWT, API Key)
  - [ ] Add authentication middleware
  - [ ] Protect all endpoints
  - [ ] User management system

- [ ] **Configure Logging**
  - [ ] Structured logging enabled
  - [ ] Log security events
  - [ ] Log rotation configured

- [ ] **Remove Debug Code**
  - [ ] Delete all `print()` debug statements
  - [ ] Remove stack traces from errors
  - [ ] Disable API documentation in production

### Medium Priority (Complete Within 2 Weeks)

- [ ] **Implement Authorization (RBAC)**
  - [ ] Define roles
  - [ ] Implement permission checks
  - [ ] Add role management

- [ ] **Set Up Monitoring**
  - [ ] Install monitoring tools
  - [ ] Configure alerts
  - [ ] Set up dashboards

- [ ] **Audit Logging**
  - [ ] Log all security events
  - [ ] Tamper-proof storage
  - [ ] Regular review process

- [ ] **Secrets Management**
  - [ ] Move to secrets manager (AWS/Azure)
  - [ ] Remove secrets from code
  - [ ] Implement key rotation

- [ ] **File Permissions**
  - [ ] Credentials file: 0600
  - [ ] Config files: 0644
  - [ ] Application files: 0755

### Lower Priority (Complete Within 1 Month)

- [ ] **Security Scanning**
  - [ ] Set up automated scanning
  - [ ] Schedule regular scans
  - [ ] Fix identified issues

- [ ] **Penetration Testing**
  - [ ] Schedule pen test
  - [ ] Fix identified vulnerabilities
  - [ ] Re-test after fixes

- [ ] **Incident Response Plan**
  - [ ] Document response procedures
  - [ ] Assign responsibilities
  - [ ] Test response plan

- [ ] **Security Training**
  - [ ] Train development team
  - [ ] Security awareness program
  - [ ] Regular refreshers

---

## Files Modified/Created

### New Security Files

- [x] `app/middleware/security_headers.py` - HTTP security headers
- [x] `app/middleware/rate_limiter.py` - Rate limiting
- [x] `app/middleware/__init__.py` - Middleware exports
- [x] `app/utils/encryption.py` - Credential encryption
- [x] `app/utils/sanitization.py` - Input sanitization
- [x] `requirements-security.txt` - Additional security packages
- [x] `requirements-updated.txt` - Updated dependencies
- [x] `SECURITY_AUDIT.md` - Detailed audit report
- [x] `SECURITY_IMPLEMENTATION_GUIDE.md` - Implementation guide
- [x] `SECURITY_CHECKLIST.md` - This file

### Modified Files

- [x] `backend/main.py` - Added security middleware
- [x] `app/services/xml_transformer.py` - Added XML sanitization
- [x] `app/services/sftp_manager.py` - Added encryption & validation
- [x] `backend/.env.example` - Added security variables

---

## Testing Checklist

### Functional Tests

- [ ] **File Upload**
  - [ ] Upload CSV file (< 100MB)
  - [ ] Upload Excel file
  - [ ] Reject oversized file
  - [ ] Reject invalid file type

- [ ] **Rate Limiting**
  - [ ] Trigger rate limit (429 response)
  - [ ] Verify rate limit headers
  - [ ] Test different endpoints

- [ ] **CORS**
  - [ ] Valid origin accepted
  - [ ] Invalid origin rejected
  - [ ] Preflight requests working

- [ ] **Encryption**
  - [ ] SFTP credentials encrypted
  - [ ] Credentials decrypt correctly
  - [ ] Old credentials migrated

### Security Tests

- [ ] **Injection Attacks**
  - [ ] XML injection blocked
  - [ ] CSV formula injection prevented
  - [ ] SQL injection N/A (no SQL)

- [ ] **SSRF Prevention**
  - [ ] Localhost blocked
  - [ ] Private IPs blocked
  - [ ] Valid hosts allowed

- [ ] **Path Traversal**
  - [ ] Cannot access parent directories
  - [ ] File storage secure
  - [ ] UUID filenames working

- [ ] **Security Headers**
  - [ ] X-Content-Type-Options present
  - [ ] X-Frame-Options present
  - [ ] CSP header present
  - [ ] Other headers present

### Compliance Tests

- [ ] **OWASP Top 10**
  - [ ] A01: Access Control - Pending auth
  - [ ] A02: Cryptographic Failures - FIXED
  - [ ] A03: Injection - FIXED
  - [ ] A04: Insecure Design - IMPROVED
  - [ ] A05: Security Misconfiguration - FIXED
  - [ ] A06: Vulnerable Components - FIXED
  - [ ] A07: Auth Failures - Pending
  - [ ] A08: Data Integrity - IMPROVED
  - [ ] A09: Logging Failures - IMPROVED
  - [ ] A10: SSRF - FIXED

---

## Dependency Updates

### Critical Updates Applied

- [x] `chromadb`: 0.4.22 → 1.1.1
- [x] `sentence-transformers`: 2.2.2 → 5.1.2
- [x] `torch`: 2.1.0 → 2.8.0
- [x] `pandas`: 2.1.4 → 2.2.3
- [x] `scikit-learn`: 1.3.2 → 1.7.1

### New Security Packages Added

- [x] `cryptography==42.0.5`
- [x] `python-jose[cryptography]==3.3.0`
- [x] `passlib[bcrypt]==1.7.4`

---

## Deployment Commands

### Development

```bash
# Install dependencies
pip install -r requirements-updated.txt

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env
echo "ENCRYPTION_KEY=<your_key>" >> .env

# Run server
python backend/main.py
```

### Production

```bash
# Set environment
export ENVIRONMENT=production

# Install production dependencies
pip install -r requirements-updated.txt
pip install gunicorn

# Run with gunicorn
gunicorn backend.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

---

## Security Contacts

- **Security Issues**: security@yourdomain.com
- **General Support**: support@yourdomain.com
- **On-Call**: +1-XXX-XXX-XXXX

---

## Quick Commands Reference

```bash
# Test rate limiting
for i in {1..100}; do curl http://localhost:8000/health; done

# Check security headers
curl -I http://localhost:8000/health

# Run security scan
bandit -r backend/app/

# Check vulnerabilities
safety check

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Test encryption
python -c "from app.utils.encryption import get_credential_encryption; e=get_credential_encryption(); print(e.decrypt(e.encrypt('test')))"
```

---

## Progress Summary

### Completed (8/15)
- Security headers middleware
- Rate limiting
- Credential encryption
- Input sanitization (XML, CSV)
- SFTP host validation
- CORS configuration
- Dependency updates
- Debug mode disabled

### In Progress (0/15)
None

### Pending (7/15)
- Authentication system
- Authorization (RBAC)
- Audit logging
- Secrets management
- Monitoring/alerting
- Virus scanning
- Penetration testing

---

**Last Updated**: 2025-11-07
**Security Audit Date**: 2025-11-07
**Next Review**: After critical fixes deployed
