# SFTP Feature Specification

## Overview
Secure SFTP integration for uploading transformed files directly to customer servers with credential management and progress tracking.

## Components
- `frontend/src/components/sftp/SFTPUploadPage.tsx`
- `frontend/src/components/sftp/SFTPCredentialManager.tsx`
- `frontend/src/components/sftp/SFTPExplorer.tsx`
- `backend/app/api/endpoints/sftp.py`

## Key Functionality
1. **Credential Management**: Secure storage and management of SFTP credentials
2. **Server Exploration**: Browse remote SFTP directories
3. **File Upload**: Upload transformed files with progress tracking
4. **Connection Testing**: Test SFTP connections before upload
5. **Multiple Profiles**: Support for multiple SFTP server profiles
6. **Upload History**: Track upload history and status

## Security Features
- Encrypted credential storage
- SSH key authentication support
- Connection timeout handling
- Secure file transmission
- Credential validation

## API Endpoints
- `POST /sftp/credentials` - Save SFTP credentials
- `GET /sftp/credentials` - List saved credentials
- `POST /sftp/test-connection` - Test SFTP connection
- `POST /sftp/upload` - Upload file to SFTP server
- `GET /sftp/browse/{path}` - Browse remote directory
- `GET /sftp/upload-status/{upload_id}` - Check upload progress

## Dependencies
- Paramiko for SFTP connectivity
- Cryptography for credential encryption
- Background task processing
- WebSocket for real-time progress updates

## Testing
**Location:** `backend/tests/features/sftp/`

**Test Files:**
- `test_sftp_persistence.py` - Tests SFTP credential storage and upload persistence

**Test Coverage:**
- SFTP connection establishment
- Credential encryption/decryption
- File upload with progress tracking
- Connection timeout handling
- Authentication methods (password, SSH key)
- Upload retry logic
- Directory browsing functionality

**Security Tests:**
- Credential storage encryption validation
- SSH key authentication testing
- Connection security verification
- Timeout and retry mechanisms
- Error handling for authentication failures

**Integration Tests:**
- Mock SFTP server connectivity
- Real-world server compatibility testing
- Large file upload validation (>100MB)
- Concurrent upload handling
- Upload interruption and recovery

**Performance Benchmarks:**
- Connection establishment: <3 seconds
- File upload speed: Limited by network bandwidth
- Memory usage: <100MB for 1GB file uploads
- Concurrent uploads: Up to 5 simultaneous connections

## Configuration
- SFTP timeout settings
- Max concurrent uploads
- Retry logic configuration
- Supported authentication methods

## Error Handling
- Connection failures
- Authentication errors
- Network timeouts
- File permission issues
- Remote server errors
- Upload interruption recovery