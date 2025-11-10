# SnapMap Troubleshooting Guide

**Version:** 2.0.0
**Last Updated:** November 7, 2025

---

## Quick Diagnosis

```bash
# Check backend health
curl http://localhost:8000/health

# Check backend logs
tail -f /var/log/snapmap/backend.log

# Check frontend
curl http://localhost:5173

# Check processes
ps aux | grep -E "uvicorn|node"
```

---

## Common Issues

### Upload Errors

#### "File too large (150 MB)"
**Cause**: File exceeds 100MB limit

**Solutions**:
1. Split file into smaller chunks
2. Increase limit in `backend/app/api/endpoints/upload.py`:
   ```python
   MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
   ```
3. Update nginx client_max_body_size

#### "Unsupported file format"
**Cause**: File type not CSV or Excel

**Solutions**:
- Convert to CSV: Open in Excel → Save As → CSV
- Use supported formats: .csv, .xlsx, .xls

#### "Delimiter detection failed"
**Cause**: Single column or no delimiter

**Solutions**:
1. Check file has at least 2 columns
2. Use manual delimiter selection
3. Verify file isn't corrupted: `head -5 file.csv`

#### "Character encoding issue"
**Cause**: Non-UTF-8 encoding not detected

**Solutions**:
1. Convert to UTF-8: `iconv -f WINDOWS-1252 -t UTF-8 input.csv > output.csv`
2. Save in Excel as "CSV UTF-8"
3. Report issue with sample file

---

### Mapping Errors

#### "Low mapping confidence (45%)"
**Cause**: Field names don't match common patterns

**Solutions**:
- Use manual drag-and-drop mapping
- Add aliases to `backend/app/schemas/field_aliases.json`
- Rebuild vector DB: `python build_vector_db.py`

#### "Required field not mapped"
**Cause**: Source file missing required field

**Solutions**:
1. Add missing column to source file
2. Map existing field to required field manually
3. Contact admin if field not applicable

---

### Validation Errors

#### "Data loss detected: 44 rows missing"
**Cause**: Duplicate IDs or null required fields

**Solutions**:
1. Check error details for row numbers
2. Remove duplicates: `df.drop_duplicates(subset=['CANDIDATE_ID'])`
3. Fill null values or enable deduplication
4. Review error report: Download from validation results

#### "Invalid email format in row 105"
**Cause**: Malformed email address

**Solutions**:
1. Go to row 105 in source file
2. Fix email format (user@domain.com)
3. Re-upload file

---

### Export Errors

#### "Export failed: Memory error"
**Cause**: File too large for available memory

**Solutions**:
1. Increase server RAM
2. Use chunked processing
3. Split file into smaller batches

#### "XML validation failed"
**Cause**: Invalid multi-value field format

**Solutions**:
1. Check `||` separator usage
2. Verify all required fields mapped
3. Review XML structure against XSD

---

### SFTP Errors

#### "Connection timeout"
**Cause**: Network/firewall issues

**Solutions**:
1. Check internet connection
2. Verify firewall allows port 22: `telnet sftp.server.com 22`
3. Test from different network
4. Contact SFTP admin

#### "Authentication failed"
**Cause**: Wrong credentials

**Solutions**:
1. Verify username/password with admin
2. Check for password expiration
3. Test credentials with FileZilla/WinSCP

#### "Permission denied"
**Cause**: No write access to remote path

**Solutions**:
1. Verify remote path exists
2. Check user permissions with admin
3. Try different remote path

---

## Backend Issues

### Won't Start

**Check Logs**:
```bash
# Systemd
sudo journalctl -u snapmap-backend -n 50

# Direct run
cd backend && python -m uvicorn main:app --reload
```

**Common Causes**:

1. **Port in use**:
   ```bash
   # Find process
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

2. **Vector DB not built**:
   ```bash
   cd backend && python build_vector_db.py
   ```

3. **Import errors**:
   ```bash
   # Activate venv
   source venv/bin/activate
   # Reinstall
   pip install -r requirements.txt
   ```

4. **Missing .env file**:
   ```bash
   cp .env.example .env
   # Edit with correct values
   ```

### High Memory Usage

**Check**:
```bash
ps aux --sort=-%mem | head -10
```

**Solutions**:
1. Reduce uvicorn workers: `--workers 2`
2. Clear file storage cache (restart server)
3. Add swap space:
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Slow Performance

**Diagnose**:
```bash
# CPU
top

# Disk I/O
iostat -x 1

# Network
iftop
```

**Solutions**:
1. Enable nginx caching
2. Increase worker count
3. Use SSD storage
4. Add more RAM

---

## Frontend Issues

### Won't Start

**Error**: "Port 5173 already in use"

**Solution**:
```bash
# Kill process
lsof -i :5173
kill -9 <PID>

# Or use different port
npm run dev -- --port 5174
```

**Error**: "Module not found"

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Blank Page

**Check Browser Console** (F12):

1. **CORS error**:
   - Verify backend running
   - Check CORS origins in `backend/main.py`

2. **API connection error**:
   - Verify backend URL in `frontend/.env`
   - Check backend health: `curl http://localhost:8000/health`

3. **Build error**:
   ```bash
   npm run build
   # Check for errors
   ```

---

## Database Issues

### Vector DB Missing

**Error**: "ChromaDB not found"

**Solution**:
```bash
cd backend
python build_vector_db.py
```

### Vector DB Corrupted

**Error**: "ChromaDB persistence error"

**Solution**:
```bash
# Backup
mv chroma_db chroma_db.bak

# Rebuild
python build_vector_db.py
```

---

## Performance Issues

### File Upload Slow

**Causes**:
- Large file size
- Slow network
- Server overloaded

**Solutions**:
1. Check file size: `ls -lh file.csv`
2. Test network speed
3. Check server load: `top`

### Mapping Slow

**Causes**:
- Vector DB not loaded
- Too many fields

**Solutions**:
1. Verify vector DB exists: `ls -la backend/chroma_db/`
2. Reduce source fields
3. Increase server resources

---

## Getting Help

### Self-Service

1. **Check Logs**: `/var/log/snapmap/backend.log`
2. **Search Documentation**: Use Ctrl+F in docs
3. **Review API Docs**: http://localhost:8000/api/docs
4. **Check GitHub Issues**: Known issues and solutions

### Contact Support

**Email**: support@yourcompany.com

**Include**:
- Error message (screenshot or text)
- Steps to reproduce
- Environment (OS, Python version, etc.)
- Log excerpt (last 50 lines)
- Sample file (if possible, sanitized)

**Response Time**: Within 24 hours

---

*Last Updated: November 7, 2025*
