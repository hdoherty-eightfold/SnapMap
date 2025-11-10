# SnapMap API Reference

**Version:** 2.0.0
**Base URL:** `http://localhost:8000`
**Last Updated:** November 7, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Endpoints](#endpoints)
   - [Upload](#upload-endpoints)
   - [Auto-Mapping](#auto-mapping-endpoints)
   - [Validation](#validation-endpoints)
   - [Transformation](#transformation-endpoints)
   - [SFTP](#sftp-endpoints)
   - [Schema](#schema-endpoints)
   - [Configuration](#configuration-endpoints)
6. [Data Models](#data-models)
7. [Code Examples](#code-examples)

---

## Overview

The SnapMap API is a RESTful API built with FastAPI. It provides endpoints for:
- File upload and parsing
- Automatic field mapping
- Data validation
- Data transformation (CSV and XML export)
- SFTP file transfer

### API Documentation

- **Interactive Docs (Swagger)**: http://localhost:8000/api/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/api/redoc

### Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com
```

### Content Types

- **Request**: `application/json` or `multipart/form-data` (for file uploads)
- **Response**: `application/json` (default), `text/csv`, or `application/xml` (exports)

---

## Authentication

**Current Version**: No authentication required (local deployment)

**Future Versions**: Will support:
- API key authentication
- OAuth 2.0
- JWT tokens

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "context",
      "fields": ["field1", "field2"]
    },
    "suggestion": "Actionable guidance for fixing the error"
  },
  "status": 400
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File exceeds size limit |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_FILE_FORMAT` | Unsupported file type |
| `FILE_TOO_LARGE` | File exceeds 100MB limit |
| `PARSE_ERROR` | Unable to parse file |
| `DATA_LOSS_DETECTED` | Rows lost during transformation |
| `VALIDATION_FAILED` | Data validation errors |
| `SCHEMA_NOT_FOUND` | Invalid entity schema |
| `FILE_NOT_FOUND` | file_id not found or expired |
| `SFTP_CONNECTION_ERROR` | SFTP connection failed |
| `SFTP_UPLOAD_ERROR` | File upload to SFTP failed |

---

## Rate Limiting

**Limit**: 100 requests per minute per IP address

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1699999999
```

**When Exceeded**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Maximum 100 requests per minute.",
    "retry_after": 42
  },
  "status": 429
}
```

---

## Endpoints

### Upload Endpoints

#### POST /api/upload

Upload and parse a CSV or Excel file.

**Request**:
```http
POST /api/upload
Content-Type: multipart/form-data

file: <file binary>
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@employees.csv"
```

**Response** (200 OK):
```json
{
  "filename": "employees.csv",
  "file_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "row_count": 1213,
  "column_count": 45,
  "columns": [
    "PERSON ID",
    "WORK EMAILS",
    "WORK PHONES",
    "FULL NAME",
    ...
  ],
  "sample_data": [
    {
      "PERSON ID": "12345",
      "WORK EMAILS": "john@company.com||j.doe@company.com",
      "FULL NAME": "John Doe"
    },
    ...
  ],
  "data_types": {
    "PERSON ID": "string",
    "WORK EMAILS": "string",
    "FULL NAME": "string"
  },
  "file_size": 2457600,
  "detected_delimiter": "|",
  "detected_encoding": "utf-8",
  "source_fields": ["PERSON ID", "WORK EMAILS", ...],
  "preview": [...]
}
```

**Error Responses**:

**400 - Invalid File Format**:
```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Unsupported file format: .txt",
    "details": {
      "supported_formats": [".csv", ".xlsx", ".xls"],
      "suggestion": "Please check the file format and encoding."
    }
  },
  "status": 400
}
```

**413 - File Too Large**:
```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size (152.3 MB) exceeds 100 MB limit"
  },
  "status": 413
}
```

**500 - Parse Error**:
```json
{
  "error": {
    "code": "PARSE_ERROR",
    "message": "Unable to parse file 'employees.csv'. Encoding detection failed.",
    "suggestion": "Verify the file is not corrupted and matches one of the supported formats."
  },
  "status": 500
}
```

---

#### POST /api/detect-file-format

Detect file format details without full parsing (lightweight operation).

**Request**:
```http
POST /api/detect-file-format
Content-Type: multipart/form-data

file: <file binary>
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/detect-file-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@employees.csv"
```

**Response** (200 OK):
```json
{
  "delimiter": "|",
  "encoding": "utf-8",
  "has_header": true,
  "row_count": 1213,
  "field_count": 45,
  "preview_fields": [
    "PERSON ID",
    "WORK EMAILS",
    "WORK PHONES",
    ...
  ],
  "special_characters_detected": ["ş", "ğ", "ı", "ö", "ü", "ç"],
  "multi_value_fields": ["WORK EMAILS", "WORK PHONES"],
  "suggested_entity": "employee"
}
```

**Use Case**: Pre-flight check before full upload to verify file format.

---

### Auto-Mapping Endpoints

#### POST /api/auto-map

Automatically map source fields to target schema fields using semantic matching.

**Request**:
```http
POST /api/auto-map
Content-Type: application/json

{
  "file_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "target_schema": "employee",
  "min_confidence": 0.70
}
```

**Alternative Request** (without file_id):
```json
{
  "source_fields": ["PERSON ID", "WORK EMAILS", "FULL NAME"],
  "target_schema": "employee",
  "min_confidence": 0.70
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/auto-map" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "target_schema": "employee",
    "min_confidence": 0.70
  }'
```

**Response** (200 OK):
```json
{
  "mappings": [
    {
      "source": "PERSON ID",
      "target": "CANDIDATE_ID",
      "confidence": 0.92,
      "mapping_type": "semantic",
      "alternatives": [
        {"target": "EMPLOYEE_ID", "confidence": 0.87},
        {"target": "USER_ID", "confidence": 0.65}
      ]
    },
    {
      "source": "WORK EMAILS",
      "target": "EMAIL",
      "confidence": 0.88,
      "mapping_type": "alias",
      "alternatives": []
    },
    {
      "source": "FULL NAME",
      "target": "DISPLAY_NAME",
      "confidence": 0.85,
      "mapping_type": "semantic",
      "alternatives": [
        {"target": "FULL_NAME", "confidence": 0.82}
      ]
    }
  ],
  "mapped_count": 42,
  "total_source": 45,
  "total_target": 67,
  "unmapped_source": ["BADGE_NUM", "DEPT_CODE", "COST_CENTER"],
  "unmapped_target": ["MIDDLE_NAME", "SUFFIX", ...],
  "required_unmapped": ["LAST_NAME"],
  "mapping_percentage": 93.3,
  "confidence_distribution": {
    "high": 28,
    "medium": 12,
    "low": 2
  }
}
```

**Mapping Types**:
- `alias`: Exact match from alias dictionary (highest confidence)
- `semantic`: Vector similarity match (medium-high confidence)
- `fuzzy`: String similarity match (fallback)

**Error Responses**:

**400 - Invalid Request**:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Either 'file_id' or 'source_fields' must be provided",
    "suggestion": "Upload a file first and use the file_id, or manually provide source_fields"
  },
  "status": 400
}
```

**404 - File Not Found**:
```json
{
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "File with ID 'a1b2c3d4...' not found or expired",
    "suggestion": "Please upload the file again to get a new file_id"
  },
  "status": 404
}
```

---

### Validation Endpoints

#### POST /api/validate

Validate mappings and data against target schema.

**Request**:
```http
POST /api/validate
Content-Type: application/json

{
  "schema_name": "employee",
  "mappings": [
    {
      "source": "PERSON ID",
      "target": "CANDIDATE_ID"
    },
    {
      "source": "WORK EMAILS",
      "target": "EMAIL"
    }
  ],
  "source_data": [
    {
      "PERSON ID": "12345",
      "WORK EMAILS": "john@company.com"
    },
    {
      "PERSON ID": "",
      "WORK EMAILS": "invalid-email"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "schema_name": "employee",
    "mappings": [
      {"source": "PERSON ID", "target": "CANDIDATE_ID"}
    ],
    "source_data": [
      {"PERSON ID": "12345"}
    ]
  }'
```

**Response** (200 OK):
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [
    {
      "field": "EMAIL",
      "message": "Optional field not mapped",
      "severity": "warning",
      "row_number": null
    }
  ],
  "info": [],
  "summary": {
    "total_errors": 0,
    "total_warnings": 1,
    "total_info": 0,
    "required_fields_mapped": 3,
    "required_fields_total": 3,
    "optional_fields_mapped": 12,
    "optional_fields_total": 42
  }
}
```

**Error Response (422 - Validation Failed)**:
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Validation failed for 2 record(s)",
    "details": {
      "total_errors": 2,
      "sample_errors": [
        "Row 2: CANDIDATE_ID is required but empty",
        "Row 3: EMAIL has invalid format: 'invalid-email'"
      ],
      "full_validation_result": {
        "is_valid": false,
        "errors": [
          {
            "field": "CANDIDATE_ID",
            "message": "CANDIDATE_ID is required but empty",
            "severity": "error",
            "row_number": 2,
            "value": ""
          },
          {
            "field": "EMAIL",
            "message": "Invalid email format",
            "severity": "error",
            "row_number": 3,
            "value": "invalid-email"
          }
        ],
        "warnings": [],
        "info": []
      }
    },
    "suggestion": "Review the errors and fix the data. Download error report for complete details."
  },
  "status": 422
}
```

---

### Transformation Endpoints

#### POST /api/transform/export

Export transformed data as CSV.

**Request**:
```http
POST /api/transform/export
Content-Type: application/json

{
  "file_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "entity_name": "employee",
  "mappings": [
    {
      "source": "PERSON ID",
      "target": "CANDIDATE_ID"
    },
    {
      "source": "WORK EMAILS",
      "target": "EMAIL"
    }
  ],
  "allow_deduplication": false
}
```

**Alternative Request** (with source_data):
```json
{
  "entity_name": "employee",
  "mappings": [...],
  "source_data": [
    {"PERSON ID": "12345", "WORK EMAILS": "john@company.com"},
    ...
  ]
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/transform/export" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "a1b2c3d4...",
    "entity_name": "employee",
    "mappings": [...]
  }' \
  --output transformed.csv
```

**Response** (200 OK):
```
Content-Type: text/csv
Content-Disposition: attachment; filename="employee_transformed.csv"

CANDIDATE_ID,FIRST_NAME,LAST_NAME,EMAIL
12345,John,Doe,john@company.com
67890,Jane,Smith,jane@company.com
...
```

**Error Response (400 - Data Loss)**:
```json
{
  "error": {
    "code": "DATA_LOSS_DETECTED",
    "message": "Data loss detected: 44 rows missing (3.6% loss)",
    "lost_rows": 44,
    "total_rows": 1213,
    "loss_percentage": "3.6%",
    "details": {
      "missing_rows": [15, 28, 42, ...],
      "possible_causes": [
        "Duplicate CANDIDATE_ID values (enable deduplication if intentional)",
        "Null values in required fields (fix source data)"
      ]
    }
  },
  "status": 400
}
```

---

#### POST /api/transform/export-xml

Export transformed data as XML (Eightfold format).

**Request**:
```http
POST /api/transform/export-xml
Content-Type: application/json

{
  "file_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "entity_name": "employee",
  "mappings": [
    {
      "source": "PERSON ID",
      "target": "CANDIDATE_ID"
    },
    {
      "source": "WORK EMAILS",
      "target": "EMAIL"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/transform/export-xml" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "a1b2c3d4...",
    "entity_name": "employee",
    "mappings": [...]
  }' \
  --output transformed.xml
```

**Response** (200 OK):
```xml
Content-Type: application/xml
Content-Disposition: attachment; filename="employee_transformed.xml"

<?xml version="1.0" encoding="UTF-8"?>
<EF_Employee_List>
  <employee>
    <candidate_id>12345</candidate_id>
    <first_name>John</first_name>
    <last_name>Doe</last_name>
    <email_list>
      <email>john@company.com</email>
      <email>j.doe@company.com</email>
    </email_list>
  </employee>
  <employee>
    <candidate_id>67890</candidate_id>
    <first_name>Jane</first_name>
    <last_name>Smith</last_name>
    <email_list>
      <email>jane@company.com</email>
    </email_list>
  </employee>
</EF_Employee_List>
```

**Multi-Value Fields**: Automatically converted to nested elements:
- `EMAIL` → `<email_list><email>...</email></email_list>`
- `PHONE` → `<phone_list><phone>...</phone></phone_list>`
- `URL` → `<url_list><url>...</url></url_list>`

---

### SFTP Endpoints

#### GET /api/sftp/credentials

List all SFTP credentials.

**Request**:
```http
GET /api/sftp/credentials
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/sftp/credentials"
```

**Response** (200 OK):
```json
{
  "credentials": [
    {
      "id": "cred_001",
      "name": "Eightfold Production",
      "host": "sftp.eightfold.ai",
      "port": 22,
      "username": "user@company.com",
      "remote_path": "/incoming/employees",
      "created_at": "2025-11-01T10:30:00Z",
      "last_used": "2025-11-07T14:22:00Z"
    },
    {
      "id": "cred_002",
      "name": "Test Server",
      "host": "test-sftp.company.com",
      "port": 22,
      "username": "testuser",
      "remote_path": "/uploads",
      "created_at": "2025-11-05T09:15:00Z",
      "last_used": null
    }
  ],
  "count": 2
}
```

---

#### POST /api/sftp/credentials

Create new SFTP credential.

**Request**:
```http
POST /api/sftp/credentials
Content-Type: application/json

{
  "name": "Eightfold Production",
  "host": "sftp.eightfold.ai",
  "port": 22,
  "username": "user@company.com",
  "password": "secure_password_123",
  "remote_path": "/incoming/employees"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/sftp/credentials" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eightfold Production",
    "host": "sftp.eightfold.ai",
    "port": 22,
    "username": "user@company.com",
    "password": "secure_password_123",
    "remote_path": "/incoming/employees"
  }'
```

**Response** (200 OK):
```json
{
  "id": "cred_003",
  "name": "Eightfold Production",
  "host": "sftp.eightfold.ai",
  "port": 22,
  "username": "user@company.com",
  "remote_path": "/incoming/employees",
  "created_at": "2025-11-07T15:30:00Z",
  "last_used": null
}
```

**Note**: Password is encrypted with AES-256 and never returned in responses.

---

#### POST /api/sftp/test-connection/{credential_id}

Test SFTP connection before uploading.

**Request**:
```http
POST /api/sftp/test-connection/cred_001
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/sftp/test-connection/cred_001"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Connection successful",
  "details": {
    "host": "sftp.eightfold.ai",
    "port": 22,
    "remote_path": "/incoming/employees",
    "writable": true,
    "connection_time_ms": 423
  }
}
```

**Error Response (500 - Connection Failed)**:
```json
{
  "error": {
    "code": "SFTP_CONNECTION_ERROR",
    "message": "Connection to sftp.eightfold.ai:22 failed: Connection timed out",
    "suggestion": "Check network connectivity and firewall rules. Verify host and port are correct."
  },
  "status": 500
}
```

---

#### POST /api/sftp/upload/{credential_id}

Upload file to SFTP server.

**Request**:
```http
POST /api/sftp/upload/cred_001
Content-Type: multipart/form-data

file: <file binary>
remote_filename: "employees_2025-11-07.xml" (optional)
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/sftp/upload/cred_001" \
  -F "file=@transformed.xml" \
  -F "remote_filename=employees_2025-11-07.xml"
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file_size": 2457600,
  "remote_path": "/incoming/employees/employees_2025-11-07.xml",
  "upload_time_ms": 3214,
  "uploaded_at": "2025-11-07T15:45:00Z"
}
```

**Error Response (500 - Upload Failed)**:
```json
{
  "error": {
    "code": "SFTP_UPLOAD_ERROR",
    "message": "Upload failed: Permission denied",
    "suggestion": "Check user permissions on remote server. Verify remote_path is writable."
  },
  "status": 500
}
```

---

### Schema Endpoints

#### GET /api/entities

List available entity types.

**Request**:
```http
GET /api/entities
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/entities"
```

**Response** (200 OK):
```json
{
  "entities": [
    {
      "name": "employee",
      "display_name": "Employee",
      "description": "Current workforce data",
      "version": "1.0",
      "field_count": 67
    },
    {
      "name": "candidate",
      "display_name": "Candidate",
      "description": "Job applicant data",
      "version": "1.0",
      "field_count": 52
    },
    {
      "name": "user",
      "display_name": "User",
      "description": "System user data",
      "version": "1.0",
      "field_count": 34
    }
  ],
  "count": 3
}
```

---

#### GET /api/schema/{entity_name}

Get schema definition for an entity.

**Request**:
```http
GET /api/schema/employee
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8000/api/schema/employee"
```

**Response** (200 OK):
```json
{
  "entity_name": "employee",
  "version": "1.0",
  "description": "Employee data for Eightfold integration",
  "fields": [
    {
      "name": "CANDIDATE_ID",
      "type": "string",
      "required": true,
      "description": "Unique employee identifier",
      "max_length": 50,
      "pattern": null,
      "example": "12345"
    },
    {
      "name": "FIRST_NAME",
      "type": "string",
      "required": true,
      "description": "Employee first name",
      "max_length": 100,
      "pattern": null,
      "example": "John"
    },
    {
      "name": "EMAIL",
      "type": "email",
      "required": false,
      "description": "Primary email address",
      "max_length": 255,
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
      "example": "john.doe@company.com"
    },
    ...
  ],
  "required_fields": ["CANDIDATE_ID", "FIRST_NAME", "LAST_NAME"],
  "optional_fields": ["EMAIL", "PHONE_NUMBER", ...],
  "total_fields": 67
}
```

**Error Response (404 - Not Found)**:
```json
{
  "error": {
    "code": "SCHEMA_NOT_FOUND",
    "message": "Schema 'contractor' not found",
    "suggestion": "Available schemas: employee, candidate, user. Check the entity name."
  },
  "status": 404
}
```

---

### Configuration Endpoints

#### GET /api/config

Get application configuration.

**Request**:
```http
GET /api/config
```

**Response** (200 OK):
```json
{
  "version": "2.0.0",
  "environment": "development",
  "features": {
    "semantic_mapping": true,
    "xml_export": true,
    "sftp_upload": true,
    "multi_value_fields": true,
    "data_validation": true
  },
  "limits": {
    "max_file_size_mb": 100,
    "max_row_count": 100000,
    "rate_limit_per_minute": 100,
    "session_timeout_minutes": 60
  },
  "supported_formats": [".csv", ".xlsx", ".xls"],
  "supported_delimiters": [",", "|", "\t", ";"],
  "supported_encodings": ["utf-8", "utf-8-sig", "latin-1", "windows-1252"]
}
```

---

## Data Models

### UploadResponse

```typescript
interface UploadResponse {
  filename: string;
  file_id: string;
  row_count: number;
  column_count: number;
  columns: string[];
  sample_data: Record<string, any>[];
  data_types: Record<string, string>;
  file_size: number;
  detected_delimiter: string;
  detected_encoding: string;
  source_fields: string[];
  preview: Record<string, any>[];
}
```

### Mapping

```typescript
interface Mapping {
  source: string;
  target: string;
  confidence: number;
  mapping_type: "alias" | "semantic" | "fuzzy";
  alternatives: Alternative[];
}

interface Alternative {
  target: string;
  confidence: number;
}
```

### ValidationResult

```typescript
interface ValidationResult {
  is_valid: boolean;
  errors: ValidationMessage[];
  warnings: ValidationMessage[];
  info: ValidationMessage[];
  summary: ValidationSummary;
}

interface ValidationMessage {
  field: string;
  message: string;
  severity: "error" | "warning" | "info";
  row_number: number | null;
  value: any;
}

interface ValidationSummary {
  total_errors: number;
  total_warnings: number;
  total_info: number;
  required_fields_mapped: number;
  required_fields_total: number;
  optional_fields_mapped: number;
  optional_fields_total: number;
}
```

---

## Code Examples

### Python (requests)

```python
import requests

# Upload file
with open('employees.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': f}
    )
    upload_result = response.json()
    file_id = upload_result['file_id']

# Auto-map fields
response = requests.post(
    'http://localhost:8000/api/auto-map',
    json={
        'file_id': file_id,
        'target_schema': 'employee',
        'min_confidence': 0.70
    }
)
mappings = response.json()['mappings']

# Export as XML
response = requests.post(
    'http://localhost:8000/api/transform/export-xml',
    json={
        'file_id': file_id,
        'entity_name': 'employee',
        'mappings': mappings
    }
)

# Save XML
with open('output.xml', 'wb') as f:
    f.write(response.content)
```

### JavaScript (axios)

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Upload file
const formData = new FormData();
formData.append('file', fs.createReadStream('employees.csv'));

const uploadResponse = await axios.post(
  'http://localhost:8000/api/upload',
  formData,
  { headers: formData.getHeaders() }
);

const fileId = uploadResponse.data.file_id;

// Auto-map fields
const mapResponse = await axios.post(
  'http://localhost:8000/api/auto-map',
  {
    file_id: fileId,
    target_schema: 'employee',
    min_confidence: 0.70
  }
);

const mappings = mapResponse.data.mappings;

// Export as CSV
const exportResponse = await axios.post(
  'http://localhost:8000/api/transform/export',
  {
    file_id: fileId,
    entity_name: 'employee',
    mappings: mappings
  },
  { responseType: 'blob' }
);

// Save CSV
fs.writeFileSync('output.csv', exportResponse.data);
```

### cURL (Complete Workflow)

```bash
# 1. Upload file
FILE_ID=$(curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@employees.csv" \
  | jq -r '.file_id')

echo "File ID: $FILE_ID"

# 2. Auto-map fields
curl -X POST "http://localhost:8000/api/auto-map" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FILE_ID\",
    \"target_schema\": \"employee\",
    \"min_confidence\": 0.70
  }" \
  -o mappings.json

# 3. Export as XML
curl -X POST "http://localhost:8000/api/transform/export-xml" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FILE_ID\",
    \"entity_name\": \"employee\",
    \"mappings\": $(cat mappings.json | jq '.mappings')
  }" \
  --output output.xml

echo "Export complete: output.xml"
```

---

## Postman Collection

A Postman collection with all endpoints is available:

**Download**: `/docs/postman/SnapMap_API.postman_collection.json`

**Import Steps**:
1. Open Postman
2. Click "Import"
3. Select the JSON file
4. Collection appears in sidebar

**Pre-configured**:
- All endpoints with examples
- Environment variables (BASE_URL)
- Test scripts for validation
- Example request bodies

---

## Changelog

See `CHANGELOG.md` for version history and breaking changes.

---

## Support

**Issues**: GitHub Issues
**Email**: support@yourcompany.com
**Documentation**: `/docs/`

---

*API Reference Version: 2.0.0*
*Last Updated: November 7, 2025*
*Author: SnapMap API Team*
