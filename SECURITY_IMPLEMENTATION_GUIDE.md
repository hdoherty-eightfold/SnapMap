# Security Implementation Guide

This guide provides instructions for deploying the security hardening fixes for SnapMap.

## Overview of Changes

The following security enhancements have been implemented:

1. **Security Headers Middleware** - Adds protective HTTP headers
2. **Rate Limiting Middleware** - Prevents abuse and DoS attacks
3. **Credential Encryption** - Fernet encryption for SFTP passwords
4. **Input Sanitization** - XML and CSV injection prevention
5. **CORS Configuration** - Environment-based origin restrictions
6. **SFTP Host Validation** - Prevents SSRF attacks
7. **Updated Dependencies** - Security patches applied

---

## Installation Steps

### 1. Update Dependencies

Install the new security-related packages:

```bash
cd backend
pip install cryptography==42.0.5
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
```

Or install all updated dependencies:

```bash
pip install -r requirements-updated.txt
```

### 2. Generate Encryption Key

Generate a Fernet encryption key for credential storage:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output (e.g., `xQv9z8y6w5v4u3t2s1r0q9p8o7n6m5l4k3j2i1h0=`)

### 3. Configure Environment Variables

Update your `.env` file:

```bash
# Copy example if needed
cp .env.example .env
```

Add these new variables to `.env`:

```env
# Environment
ENVIRONMENT=development  # Change to 'production' for prod

# Security - Encryption Key
ENCRYPTION_KEY=paste_your_generated_key_here

# Production CORS Origins (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 4. Update Existing SFTP Credentials (If Any)

If you have existing SFTP credentials stored, they need to be re-encrypted:

```bash
python -c "
from app.services.sftp_manager import get_sftp_manager
manager = get_sftp_manager()
print(f'Credentials loaded: {len(manager._credentials)}')
# Credentials will be automatically re-encrypted on next save
"
```

### 5. Set File Permissions (Linux/Mac Only)

```bash
chmod 600 .env
chmod 600 /tmp/snapmap_sftp/credentials.json  # If exists
```

### 6. Test the Application

Start the server:

```bash
# Development
python main.py

# Or with uvicorn
uvicorn main:app --reload
```

Verify security features are active:

```bash
# Test rate limiting (should get 429 after many requests)
for i in {1..100}; do curl http://localhost:8000/api/upload; done

# Test security headers
curl -I http://localhost:8000/health
# Should see: X-Content-Type-Options, X-Frame-Options, etc.
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Environment mode | `development` | No |
| `ENCRYPTION_KEY` | Fernet encryption key | Auto-generated | Yes |
| `CORS_ORIGINS` | Allowed origins (prod) | localhost | No |
| `MAX_FILE_SIZE_MB` | Max upload size | `100` | No |
| `DEBUG_MODE` | Debug mode | `false` | No |

### Rate Limits

Different endpoints have different limits:

- **Upload endpoints**: 10 req/min, 100 req/hour
- **Transform endpoints**: 30 req/min, 500 req/hour
- **Other endpoints**: 60 req/min, 1000 req/hour

Modify in `app/middleware/rate_limiter.py` if needed.

### Security Headers

The following headers are automatically added:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy: default-src 'self'; ...`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), ...`

---

## Production Deployment

### Before Going to Production

1. **Set Environment to Production**:
   ```env
   ENVIRONMENT=production
   ```

2. **Configure CORS Origins**:
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
   ```

3. **Disable Debug Mode**:
   ```env
   DEBUG_MODE=false
   ```

4. **Use HTTPS**: Deploy behind reverse proxy (Nginx, Caddy) with SSL

5. **Secure .env File**:
   ```bash
   chmod 600 .env
   chown app_user:app_group .env
   ```

6. **Use Production Server**:
   ```bash
   # Install gunicorn (Unix)
   pip install gunicorn

   # Run with gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

### Production Checklist

- [ ] `ENVIRONMENT=production` set
- [ ] `ENCRYPTION_KEY` generated and secured
- [ ] `CORS_ORIGINS` configured for production domains
- [ ] `DEBUG_MODE=false`
- [ ] API documentation disabled (automatic in production)
- [ ] HTTPS configured (reverse proxy)
- [ ] File permissions restricted
- [ ] Dependencies updated
- [ ] Rate limiting tested
- [ ] Security headers verified
- [ ] SFTP host validation enabled
- [ ] Monitoring/logging configured

---

## Security Features Details

### 1. Rate Limiting

**What it does**: Limits requests per IP address to prevent abuse

**How it works**:
- Tracks requests per IP in memory
- Different limits for different endpoints
- Returns HTTP 429 when limit exceeded

**Response when limited**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded: 10 requests per minute",
    "retry_after": 60
  },
  "status": 429
}
```

### 2. Credential Encryption

**What it does**: Encrypts SFTP passwords using Fernet (AES-128)

**Key management**:
- Key stored in `ENCRYPTION_KEY` environment variable
- Never hardcode the key
- Use secrets manager in production (AWS Secrets Manager, Azure Key Vault)

**Migration from old format**:
- Automatically handles old base64-encoded passwords
- Re-encrypts on next save

### 3. Input Sanitization

**XML Injection Prevention**:
- Escapes special characters: `&`, `<`, `>`, `"`, `'`
- Example: `<script>` becomes `&lt;script&gt;`

**CSV Injection Prevention**:
- Detects formula prefixes: `=`, `+`, `-`, `@`
- Prefixes with single quote to force text interpretation
- Example: `=1+1` becomes `'=1+1`

**SFTP Host Validation**:
- Blocks localhost: `127.0.0.1`, `localhost`
- Blocks private IPs: `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`
- Blocks link-local: `169.254.x.x`

### 4. Security Headers

**X-Content-Type-Options**: Prevents MIME sniffing attacks
**X-Frame-Options**: Prevents clickjacking
**Content-Security-Policy**: Prevents XSS attacks
**Referrer-Policy**: Controls referrer information leakage

### 5. CORS Configuration

**Development**:
- Allows localhost origins only
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: Content-Type, Authorization, X-Requested-With

**Production**:
- Only allows origins specified in `CORS_ORIGINS`
- Same method/header restrictions
- Credentials enabled

---

## Testing Security Features

### Test Rate Limiting

```bash
# Bash script to test rate limiting
for i in {1..100}; do
  curl -w "%{http_code}\n" http://localhost:8000/health
  sleep 0.1
done
```

Expected: HTTP 429 after hitting the limit

### Test Security Headers

```bash
curl -I http://localhost:8000/health
```

Expected headers:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'; ...
```

### Test Credential Encryption

```python
from app.utils.encryption import get_credential_encryption

encryptor = get_credential_encryption()
encrypted = encryptor.encrypt("my_password")
decrypted = encryptor.decrypt(encrypted)
assert decrypted == "my_password"
print("Encryption test passed!")
```

### Test XML Sanitization

```python
from app.utils.sanitization import sanitize_xml_content

result = sanitize_xml_content("<script>alert('xss')</script>")
assert "<script>" not in result
print("XML sanitization test passed!")
```

### Test SFTP Host Validation

```python
from app.utils.sanitization import validate_sftp_host

assert validate_sftp_host("localhost") == False
assert validate_sftp_host("192.168.1.1") == False
assert validate_sftp_host("sftp.example.com") == True
print("SFTP validation test passed!")
```

---

## Troubleshooting

### Issue: "ENCRYPTION_KEY not set" Warning

**Solution**: Generate and set encryption key in `.env`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to .env as ENCRYPTION_KEY=...
```

### Issue: "Failed to decrypt password" Error

**Cause**: Trying to decrypt old base64-encoded passwords

**Solution**: Automatic migration is enabled. If it fails:
1. Delete old credentials file: `/tmp/snapmap_sftp/credentials.json`
2. Re-add credentials through API

### Issue: Rate Limit Errors in Development

**Solution**: Increase rate limits in `app/middleware/rate_limiter.py`:
```python
self.general_limiter = RateLimiter(
    requests_per_minute=1000,  # Increase for dev
    requests_per_hour=10000
)
```

### Issue: CORS Errors in Production

**Solution**: Check `CORS_ORIGINS` includes your frontend domain:
```env
CORS_ORIGINS=https://app.yourdomain.com
```

---

## Monitoring and Logging

### Recommended Logging Configuration

Install structured logging:
```bash
pip install python-json-logger
```

Configure in application:
```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Key Events to Log

- File uploads (with size, user IP)
- Configuration changes
- SFTP credential access
- Rate limit violations
- Failed authentication attempts (when implemented)
- Suspicious activity (SSRF attempts, etc.)

### Metrics to Monitor

- Request rate per endpoint
- Error rate
- File upload sizes
- Rate limit violations
- Response times
- Active connections

---

## Next Steps (Not Yet Implemented)

The following features are recommended but not yet implemented:

1. **Authentication System**:
   - JWT-based authentication
   - API key authentication
   - User management

2. **Authorization (RBAC)**:
   - Role-based access control
   - Permission system

3. **Audit Logging**:
   - Comprehensive security event logging
   - Tamper-proof audit trail

4. **Secrets Management**:
   - Integration with AWS Secrets Manager
   - Or Azure Key Vault
   - Automatic credential rotation

5. **Monitoring & Alerting**:
   - Prometheus metrics
   - Grafana dashboards
   - Alert rules for suspicious activity

6. **Vulnerability Scanning**:
   - Automated dependency scanning
   - Regular security audits
   - Penetration testing

---

## Support and Additional Resources

### Documentation

- [SECURITY_AUDIT.md](./SECURITY_AUDIT.md) - Detailed security audit report
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Cryptography Library](https://cryptography.io/)

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Rotate encryption keys** periodically (every 90 days)
3. **Keep dependencies updated** regularly
4. **Monitor logs** for suspicious activity
5. **Use HTTPS** always in production
6. **Implement authentication** before going to production
7. **Regular security audits** (quarterly recommended)

### Running Security Scans

```bash
# Install security tools
pip install bandit safety

# Run Bandit (code security scan)
bandit -r app/

# Run Safety (dependency vulnerability scan)
safety check --json

# Run both
python -m bandit -r app/ && python -m safety check
```

---

## Contact

For security issues or questions:
- Create an issue in the repository (for non-sensitive issues)
- Email: security@yourdomain.com (for sensitive disclosures)
- Follow responsible disclosure practices

**Last Updated**: 2025-11-07
**Version**: 1.0.0
