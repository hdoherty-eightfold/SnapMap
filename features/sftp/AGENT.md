# SFTP Agent

## Version 1.0.0 | Last Updated: 2025-11-06

---

## Agent Identity

**Name**: SFTP Agent
**Version**: 1.0.0
**Status**: Active
**Owner**: SnapMap Core Team
**Domain**: SFTP File Transfer
**Location**: `features/sftp/AGENT.md`

---

## 1. Role & Responsibilities

### Primary Responsibilities

1. **Credential Management**: Store and manage SFTP server credentials securely
2. **Connection Testing**: Verify SFTP connections before file transfer
3. **File Upload**: Upload transformed files to remote SFTP servers
4. **Path Management**: Handle remote directory paths and file naming
5. **Error Recovery**: Provide detailed error messages for connection/upload failures
6. **Credential Persistence**: Save credentials to disk for reuse across sessions

### Data Sources

- **SFTP Credentials**: Host, port, username, password, remote path
- **Exported Files**: CSV or XML files from Export Agent
- **Credential Storage**: JSON file in temp directory (`/tmp/snapmap_sftp/credentials.json`)

### Success Criteria

- **Upload Speed**: <10 seconds for 10MB files
- **Connection Success Rate**: >95% for valid credentials
- **Credential Security**: Basic base64 encoding (production requires encryption)
- **Upload Reliability**: >98% successful uploads

---

## 2. Feature Capabilities

### What This Agent CAN Do

1. **Add SFTP credentials** (host, port, username, password, remote_path)
2. **Update existing credentials** (change any field)
3. **Delete credentials** by ID
4. **List all saved credentials** (without passwords)
5. **Test SFTP connections** before upload
6. **Upload files to SFTP servers** via paramiko
7. **Store credentials persistently** (JSON file with base64 passwords)
8. **Manage multiple credential sets** (different servers/accounts)
9. **Auto-generate credential IDs** (UUID v4)
10. **Track connection status** (last tested, connection success/failure)
11. **Handle connection timeouts** (10 second timeout)
12. **Support custom remote paths** per credential

### What This Agent CANNOT Do

1. **Encrypt passwords** (uses basic base64 encoding - NOT secure for production)
2. **Browse SFTP directories** (SFTP Explorer UI exists but backend APIs not implemented)
3. **Download files from SFTP** (upload only)
4. **Support SSH key authentication** (password-only)
5. **Manage file permissions** on remote server
6. **Delete files on SFTP server**
7. **Synchronize directories** (single file upload only)
8. **Retry failed uploads** automatically
9. **Compress files before upload** (uploads as-is)
10. **Validate remote path existence** before saving credentials

---

## 3. Dependencies

### Required Dependencies

- **paramiko**: SFTP client - `pip install paramiko` (SSH2 protocol)
- **uuid**: Credential ID generation - `import uuid`
- **json**: Credential persistence - `import json`
- **base64**: Password encoding - `import base64`
- **pathlib**: File path handling - `from pathlib import Path`

### Optional Dependencies

None (paramiko is required for SFTP functionality)

### External Services

- **Remote SFTP Servers**: Customer SFTP servers (external, customer-managed)

---

## 4. Architecture & Implementation

### Key Files & Code Locations

#### Backend
- **API Endpoints**: `backend/app/api/endpoints/sftp.py`
  - `GET /sftp/credentials`: List all credentials
  - `POST /sftp/credentials`: Add new credential
  - `PUT /sftp/credentials/{id}`: Update credential
  - `DELETE /sftp/credentials/{id}`: Delete credential
  - `POST /sftp/test`: Test connection
  - `POST /sftp/upload`: Upload file

- **Services**: `backend/app/services/sftp_manager.py` (Lines 1-322) **PRIMARY**
  - `add_credential()`: Add new SFTP credential (Lines 81-110)
  - `get_credential()`: Get credential by ID (Lines 112-117)
  - `get_all_credentials()`: List all (sanitized) (Lines 119-121)
  - `update_credential()`: Update existing (Lines 123-153)
  - `delete_credential()`: Delete by ID (Lines 155-161)
  - `test_connection()`: Test SFTP connection (Lines 163-227)
  - `upload_file()`: Upload to SFTP server (Lines 229-303)
  - `_encode_password()`: Base64 encode (Lines 31-33)
  - `_decode_password()`: Base64 decode (Lines 35-37)
  - `_load_credentials()`: Load from disk (Lines 39-60)
  - `_save_credentials()`: Save to disk (Lines 62-79)
  - `_sanitize_credential()`: Remove password (Lines 305-309)

- **Models**: `backend/app/models/sftp.py`
  - `SFTPCredential`: Credential schema
  - `SFTPTestRequest`: Test connection request
  - `SFTPUploadRequest`: Upload file request

#### Frontend
- **Components**: `frontend/src/components/sftp/`
  - `SFTPCredentialManager.tsx`: Credential CRUD UI (Lines 1-400)
  - `SFTPUploadPage.tsx`: File upload UI (Lines 1-300)
  - `SFTPExplorer.tsx`: Browse SFTP (UI only, backend not implemented)

- **API Client**: `frontend/src/services/sftp-api.ts`
  - `getCredentials()`: List credentials
  - `addCredential()`: Add new
  - `updateCredential()`: Update
  - `deleteCredential()`: Delete
  - `testConnection()`: Test
  - `uploadFile()`: Upload

### Current State

#### Implemented Features
- [x] Credential CRUD (create, read, update, delete)
- [x] Credential persistence (JSON file with base64 passwords)
- [x] Connection testing via paramiko
- [x] File upload via SFTP
- [x] Multiple credential sets
- [x] Connection status tracking
- [x] Frontend credential manager UI
- [x] Frontend upload UI

#### In Progress
None currently

#### Planned
- [ ] SSH key authentication: Support private key auth (Priority: High)
- [ ] Password encryption: Proper encryption (Fernet, KMS) (Priority: Critical)
- [ ] SFTP Explorer backend: Browse directories, download files (Priority: Medium)
- [ ] Retry logic: Auto-retry failed uploads (Priority: Medium)
- [ ] Upload progress: Real-time progress tracking (Priority: Low)
- [ ] Batch upload: Upload multiple files (Priority: Low)

---

## 5. Communication Patterns

### Incoming Requests (FROM)

**User (via Frontend)**
- **Action**: Add SFTP credential
- **Payload**: `{ name: string, host: string, port: number, username: string, password: string, remote_path?: string }`
- **Response**: `{ id: string, name: string, host: string, ... }` (without password)

**User (via Frontend)**
- **Action**: Test SFTP connection
- **Payload**: `{ credential_id: string }`
- **Response**: `{ success: boolean, message?: string, error?: string }`

**User (via Frontend)**
- **Action**: Upload file to SFTP
- **Payload**: `{ credential_id: string, local_path: string, remote_filename?: string }`
- **Response**: `{ success: boolean, path?: string, error?: string }`

### Outgoing Requests (TO)

**Export Agent**
- **Action**: Get file path for upload
- **Purpose**: Retrieve exported file location
- **Frequency**: Before every upload

**Remote SFTP Servers**
- **Action**: SSH connection, file transfer
- **Purpose**: Upload files to customer servers
- **Frequency**: Per upload request

### Data Flow Diagram

```
┌─────────────────────────┐
│  Export Agent           │
│  - Exported file path   │
└───────────┬─────────────┘
            │
            ↓ local_path
┌────────────────────────────────────────┐
│  SFTP Agent                            │
│  1. Load credential by ID              │
│  2. Create SSH client (paramiko)       │
│  3. Connect to SFTP server             │
│     - hostname, port, username, pwd    │
│  4. Open SFTP session                  │
│  5. Determine remote path + filename   │
│  6. Upload file (sftp.put)             │
│  7. Close SFTP + SSH connections       │
│  8. Return success/failure             │
└───────────┬────────────────────────────┘
            │
            ↓ Upload result
┌─────────────────────────┐
│  Remote SFTP Server     │
│  - File uploaded        │
└─────────────────────────┘
```

---

## 6. Error Handling

### Common Errors

| Error Code | Severity | Description | Recovery |
|------------|----------|-------------|----------|
| `CREDENTIAL_NOT_FOUND` | Critical | Credential ID not found | Create credential first |
| `CONNECTION_TIMEOUT` | Critical | SFTP connection timeout (10s) | Verify host, port, network |
| `AUTHENTICATION_FAILED` | Critical | Invalid username/password | Update credentials |
| `PERMISSION_DENIED` | Critical | Cannot write to remote path | Verify remote path permissions |
| `FILE_NOT_FOUND` | Critical | Local file not found | Export file first |
| `PARAMIKO_NOT_INSTALLED` | Critical | paramiko library missing | Install paramiko |
| `REMOTE_PATH_INVALID` | Warning | Remote path doesn't exist | Verify path or create directory |
| `NETWORK_UNREACHABLE` | Critical | Cannot reach SFTP server | Check network, firewall |

### Error Response Format

```json
{
  "success": false,
  "error": "paramiko.ssh_exception.AuthenticationException: Authentication failed"
}
```

**Test Connection Response**:
```json
{
  "success": false,
  "error": "Connection timeout: could not connect to example.com:22"
}
```

**Upload Response**:
```json
{
  "success": true,
  "path": "/uploads/employee_data.csv"
}
```

### Validation Rules

1. **Credential Completeness**
   - **Severity**: Critical
   - **Rule**: Host, port, username, password required
   - **Action**: Reject credential if missing required fields

2. **Connection Timeout**
   - **Severity**: Warning
   - **Rule**: Connection attempt times out after 10 seconds
   - **Action**: Return timeout error

3. **Password Security**
   - **Severity**: Critical (Production)
   - **Rule**: Passwords should be encrypted (currently only base64)
   - **Action**: Implement proper encryption for production

---

## 7. Performance Considerations

### Performance Targets

- **Response Time**: <10s for 10MB file upload
- **Throughput**: 5 concurrent uploads
- **Memory Usage**: Max 100MB per upload
- **CPU Usage**: Max 30% per upload

### Optimization Strategies

1. **Connection pooling**: Reuse SSH connections for multiple uploads (not implemented)
2. **Async uploads**: Non-blocking upload operations
3. **Progress tracking**: Real-time upload progress (not implemented)
4. **Retry logic**: Auto-retry on transient failures (not implemented)
5. **Connection caching**: Cache successful connections for 5 minutes (not implemented)

### Bottlenecks & Limitations

- **Network speed**: Upload speed limited by network bandwidth
- **No connection pooling**: New connection per upload (overhead)
- **No parallel uploads**: Sequential uploads only
- **No compression**: Files uploaded as-is (no gzip)
- **Password security**: Base64 encoding is NOT secure (production risk)

---

## 8. Testing Checklist

### Unit Tests
- [ ] Add SFTP credential
- [ ] Update SFTP credential
- [ ] Delete SFTP credential
- [ ] List all credentials (password sanitized)
- [ ] Test connection (success)
- [ ] Test connection (failure - bad credentials)
- [ ] Upload file (success)
- [ ] Upload file (failure - file not found)
- [ ] Password encoding/decoding
- [ ] Credential persistence (load/save)

### Integration Tests
- [ ] Export → SFTP upload pipeline
- [ ] Test connection before upload
- [ ] Upload to real SFTP server (integration test environment)
- [ ] Multiple concurrent uploads
- [ ] Credential CRUD via API

### Edge Cases
- [ ] Test connection with invalid host
- [ ] Upload with missing local file
- [ ] Upload with invalid remote path
- [ ] Test timeout (>10s connection)
- [ ] Handle special characters in password
- [ ] Handle special characters in filename

### Performance Tests
- [ ] Upload 1MB file
- [ ] Upload 10MB file
- [ ] Upload 100MB file
- [ ] Test 5 concurrent uploads
- [ ] Measure upload time vs file size

---

## 9. Maintenance

### When to Update This Document

- SSH key authentication implemented
- Password encryption implemented
- SFTP Explorer backend implemented
- Retry logic added
- Connection pooling added
- Performance optimizations

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Upload success rate | >98% | <90% |
| Average upload time (10MB) | <10s | >30s |
| Connection test success | >95% | <85% |
| Authentication failures | <5% | >15% |
| Credential storage errors | 0 | >0 |

### Health Check Endpoint

**Endpoint**: `GET /health/sftp`
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "paramiko": "ok",
    "credential_storage": "ok"
  },
  "stats": {
    "total_credentials": 12,
    "total_uploads": 3456,
    "avg_upload_time_ms": 8500,
    "last_upload": "2025-11-06T14:23:15Z"
  }
}
```

---

## 10. Integration Points

### With Other Agents

| Agent | Integration Type | Data Exchanged |
|-------|------------------|----------------|
| Export Agent | Request | Local file path for upload |
| Main Orchestrator | Request/Response | Upload requests, status |

### With External Systems

- **Remote SFTP Servers**: File upload via SSH/SFTP protocol
- **File System**: Credential persistence (JSON file in temp directory)

---

## 11. Questions This Agent Can Answer

1. "Add SFTP credentials for my server"
2. "Test connection to SFTP server"
3. "Upload transformed file to SFTP"
4. "List all saved SFTP credentials"
5. "Update SFTP credentials"
6. "Delete SFTP credentials"
7. "What SFTP servers are configured?"
8. "Why did my connection test fail?"
9. "What port does SFTP use?" (typically 22)
10. "How are passwords stored?" (base64 - NOT secure for production)

---

## 12. Questions This Agent CANNOT Answer

1. "Browse files on SFTP server" - Not implemented (UI exists, backend missing)
2. "Download files from SFTP" - Upload only
3. "Use SSH keys for authentication" - Not implemented
4. "Encrypt passwords securely" - Not implemented (only base64)
5. "Automatically retry failed uploads" - Not implemented
6. "Upload multiple files at once" - Single file only
7. "Synchronize directories" - Not implemented

---

## Version History

### Version 1.0.0 (2025-11-06)
- Initial SFTP Agent documentation
- Credential CRUD operations
- Connection testing via paramiko
- File upload to SFTP servers
- Credential persistence (JSON + base64)
- Frontend credential manager
- Frontend upload UI

---

## Notes & Assumptions

- **Assumption 1**: Users have SFTP server credentials (external servers)
- **Assumption 2**: Passwords stored with base64 encoding (NOT secure for production)
- **Assumption 3**: SFTP servers use standard port 22
- **Known Issue 1**: Password storage is NOT secure (base64 is easily decoded)
- **Known Issue 2**: SFTP Explorer backend not implemented (UI exists but non-functional)
- **Technical Debt 1**: CRITICAL - Implement proper password encryption (Fernet, KMS, Vault)
- **Technical Debt 2**: Implement SSH key authentication (more secure than passwords)
- **Technical Debt 3**: Implement SFTP Explorer backend (browse, download, delete files)
- **Technical Debt 4**: Add retry logic for transient network failures
- **Security Warning**: Current password storage is NOT production-ready - must encrypt before deploying to production
