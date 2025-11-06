# Upload Agent

## Version 1.0.0 | Last Updated: 2025-11-06

---

## Agent Identity

**Name**: Upload Agent
**Version**: 1.0.0
**Status**: Active
**Owner**: SnapMap Core Team
**Domain**: File Upload & Parsing
**Location**: `features/upload/AGENT.md`

---

## 1. Role & Responsibilities

### Primary Responsibilities

1. **File Upload**: Accept CSV and Excel files via HTTP multipart upload
2. **File Parsing**: Parse uploaded files into structured DataFrames
3. **Data Type Detection**: Automatically detect column data types (string, number, date, email)
4. **File Storage**: Store parsed DataFrames in memory for downstream processing
5. **Validation**: Validate file size, format, and basic structure
6. **Sample Generation**: Provide preview of first 10 rows for UI display

### Data Sources

- **User Uploads**: CSV files (.csv), Excel files (.xlsx, .xls) up to 100MB
- **File System**: Temporary in-memory storage for file content
- **Pandas Parser**: DataFrame parsing engine

### Success Criteria

- **Upload Speed**: <2 seconds for files up to 100MB
- **Parse Success Rate**: >99% for valid CSV/Excel files
- **Type Detection Accuracy**: >95% for common data types
- **Memory Efficiency**: <2x file size in memory

---

## 2. Feature Capabilities

### What This Agent CAN Do

1. **Parse CSV files** with various encodings (UTF-8, Latin-1, CP1252)
2. **Parse Excel files** (.xlsx, .xls) including multi-sheet workbooks (uses first sheet)
3. **Detect column data types** automatically (string, integer, float, date, email, boolean)
4. **Store full DataFrames** in memory with unique file_id for retrieval
5. **Generate file metadata** (row count, column count, column names, sample data)
6. **Validate file size** (max 100MB limit)
7. **Validate file format** (reject unsupported formats with clear error messages)
8. **Handle various CSV delimiters** (comma, semicolon, tab)
9. **Extract sample data** (first 10 rows) for preview
10. **Generate unique file IDs** for tracking uploaded files
11. **Return structured responses** with UploadResponse model
12. **Handle parsing errors** gracefully with detailed error messages

### What This Agent CANNOT Do

1. **Detect entity types** (delegates to Mapping Agent via semantic matching)
2. **Validate data quality** (delegates to Validation Agent)
3. **Transform data** (delegates to Transform Agent)
4. **Store files permanently** (in-memory storage only, no disk persistence)
5. **Parse other file formats** (JSON, XML, PDF, etc.)
6. **Handle password-protected files**
7. **Process files larger than 100MB**
8. **Parse files with macros or complex Excel features**
9. **Recover corrupted files**
10. **Stream large files** (loads entire file into memory)

---

## 3. Dependencies

### Required Dependencies

- **FastAPI**: HTTP framework - `from fastapi import APIRouter, UploadFile, File`
- **Pandas**: DataFrame parsing - `import pandas as pd`
- **file_parser service**: Parse logic - `backend/app/services/file_parser.py`
- **file_storage service**: Storage management - `backend/app/services/file_storage.py`
- **UploadResponse model**: Response schema - `backend/app/models/upload.py`

### Optional Dependencies

- **openpyxl**: Excel 2007+ parsing (.xlsx) - Fallback to xlrd if missing
- **xlrd**: Legacy Excel parsing (.xls) - Required for .xls files

### External Services

None (all processing is local)

---

## 4. Architecture & Implementation

### Key Files & Code Locations

#### Backend
- **API Endpoints**: `backend/app/api/endpoints/upload.py` (Lines 1-117)
  - `POST /upload`: Main upload endpoint (Lines 14-116)
  - File size validation (Lines 30-48)
  - File parsing (Lines 62-90)
  - Error handling (Lines 92-116)

- **Services**:
  - `backend/app/services/file_parser.py`
    - `parse_file()`: Parse CSV/Excel content (core function)
    - `detect_column_types()`: Detect data types per column
  - `backend/app/services/file_storage.py`
    - `store_dataframe()`: Store DataFrame with unique ID
    - `retrieve_dataframe()`: Retrieve DataFrame by ID

- **Models**: `backend/app/models/upload.py`
  - `UploadResponse`: Response schema with file metadata
    - `filename`, `file_id`, `row_count`, `column_count`
    - `columns`, `sample_data`, `data_types`, `file_size`

#### Frontend
- **Components**: `frontend/src/components/upload/FileUpload.tsx`
  - File upload UI with drag-and-drop (Lines 1-250)
  - File validation (size, format)
  - Upload progress indication
  - Sample data preview table

- **API Client**: `frontend/src/services/api.ts`
  - `uploadFile()`: Upload file to backend (Lines 10-30)

### Current State

#### Implemented Features
- [x] CSV file parsing (UTF-8, Latin-1, CP1252 encodings)
- [x] Excel file parsing (.xlsx, .xls)
- [x] Automatic data type detection
- [x] File size validation (100MB limit)
- [x] In-memory file storage with unique IDs
- [x] Sample data generation (first 10 rows)
- [x] File metadata extraction
- [x] Drag-and-drop upload UI
- [x] Upload progress indication
- [x] Error handling with detailed messages

#### In Progress
None currently

#### Planned
- [ ] Multi-sheet Excel support: Allow user to select sheet (Priority: Medium)
- [ ] Streaming upload: Support files >100MB via streaming (Priority: Low)
- [ ] File compression: Accept .zip files with multiple CSVs (Priority: Low)
- [ ] Custom delimiter detection: Auto-detect CSV delimiter (Priority: Medium)
- [ ] Encoding detection: Auto-detect file encoding (Priority: Medium)

---

## 5. Communication Patterns

### Incoming Requests (FROM)

**User (via Frontend)**
- **Action**: Upload file
- **Payload**: `FormData { file: File }`
- **Response**: `UploadResponse { filename, file_id, row_count, column_count, columns, sample_data, data_types, file_size }`

**Main Orchestrator**
- **Action**: Request file upload
- **Payload**: File binary data
- **Response**: Upload metadata

### Outgoing Requests (TO)

**File Storage Service**
- **Action**: Store parsed DataFrame
- **Purpose**: Persist DataFrame for downstream agents
- **Frequency**: Always (every successful upload)

**No direct agent-to-agent communication** (follows protocol: all routing via Main Orchestrator)

### Data Flow Diagram

```
┌──────────────────────┐
│  User (Frontend)     │
│  - Selects file      │
│  - Drag/drop upload  │
└──────────┬───────────┘
           │
           ↓ FormData { file }
┌──────────────────────────────┐
│  Upload Agent                │
│  1. Validate size/format     │
│  2. Read file content        │
│  3. Parse to DataFrame       │
│  4. Detect column types      │
│  5. Generate sample (10 rows)│
│  6. Store in memory          │
│  7. Generate file_id         │
└──────────┬───────────────────┘
           │
           ↓ UploadResponse
┌──────────────────────┐
│  Frontend UI         │
│  - Display metadata  │
│  - Show sample table │
│  - Enable next steps │
└──────────────────────┘
```

---

## 6. Error Handling

### Common Errors

| Error Code | Severity | Description | Recovery |
|------------|----------|-------------|----------|
| `FILE_TOO_LARGE` | Critical | File size exceeds 100MB limit | Split file or compress data |
| `INVALID_FILE_FORMAT` | Critical | File is not CSV or Excel | Convert file to CSV/Excel |
| `FILE_READ_ERROR` | Critical | Cannot read file content | Check file permissions, retry upload |
| `PARSE_ERROR` | Critical | Error parsing file structure | Validate CSV structure, check for corrupted data |
| `EMPTY_FILE` | Critical | File has no data rows | Add data to file |
| `UNSUPPORTED_ENCODING` | Warning | File encoding not recognized | Convert to UTF-8 encoding |

### Error Response Format

```json
{
  "status": 413,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size (150.5 MB) exceeds 100 MB limit",
    "details": {
      "file_size": 157810688,
      "max_size": 104857600,
      "suggested_formats": [".csv", ".xlsx", ".xls"]
    }
  }
}
```

### Validation Rules

1. **File Size Validation**
   - **Severity**: Critical
   - **Rule**: File size <= 100MB (104,857,600 bytes)
   - **Action**: Reject upload with HTTP 413

2. **File Format Validation**
   - **Severity**: Critical
   - **Rule**: Extension must be .csv, .xlsx, or .xls
   - **Action**: Reject upload with HTTP 400

3. **File Structure Validation**
   - **Severity**: Critical
   - **Rule**: File must have at least 1 data row
   - **Action**: Reject with "Empty file" error

---

## 7. Performance Considerations

### Performance Targets

- **Response Time**: <2s for files up to 100MB
- **Throughput**: 10 concurrent uploads
- **Memory Usage**: Max 200MB per upload (2x file size)
- **CPU Usage**: Max 50% of single core per upload

### Optimization Strategies

1. **Pandas chunked reading**: For large CSV files, use chunking to reduce memory
2. **Type inference optimization**: Limit sample size for type detection to first 1000 rows
3. **Streaming upload**: Frontend streams file to backend (reduces memory on client)
4. **Async processing**: FastAPI async endpoint prevents blocking
5. **Memory cleanup**: Delete DataFrames after export or timeout (1 hour TTL)

### Bottlenecks & Limitations

- **Memory bottleneck**: Entire file loaded into memory (limits to 100MB)
- **Pandas parsing speed**: Large files (50MB+) take 5-10s to parse
- **No parallel parsing**: Each file parsed sequentially
- **Encoding detection**: Limited to common encodings (UTF-8, Latin-1, CP1252)

---

## 8. Testing Checklist

### Unit Tests
- [ ] Upload valid CSV file (UTF-8)
- [ ] Upload valid Excel file (.xlsx)
- [ ] Upload file with non-UTF-8 encoding
- [ ] Reject file >100MB
- [ ] Reject invalid file format (.txt, .json)
- [ ] Detect column types correctly (string, int, float, date)
- [ ] Handle empty CSV file
- [ ] Handle CSV with duplicate column names

### Integration Tests
- [ ] Upload → Mapping Agent handoff
- [ ] File storage → retrieval by file_id
- [ ] Upload → Validation Agent (full pipeline)
- [ ] Concurrent uploads (10 users)

### Edge Cases
- [ ] CSV with 1,000+ columns
- [ ] CSV with 100,000+ rows
- [ ] Excel with multiple sheets (verify first sheet used)
- [ ] CSV with special characters in headers
- [ ] CSV with mixed encodings
- [ ] File with trailing commas

### Performance Tests
- [ ] Test with 10MB file
- [ ] Test with 50MB file
- [ ] Test with 100MB file (max)
- [ ] Test 10 concurrent uploads
- [ ] Measure memory usage during upload

---

## 9. Maintenance

### When to Update This Document

- New file formats supported (e.g., JSON, XML)
- File size limit changed
- New data types detected
- Storage mechanism changed (e.g., Redis, S3)
- API contract changed (new fields in UploadResponse)

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Upload success rate | >99% | <95% |
| Average upload time | <2s | >5s |
| Parse error rate | <1% | >5% |
| Memory usage per upload | <200MB | >500MB |
| File storage TTL expirations | Normal | >10% premature |

### Health Check Endpoint

**Endpoint**: `GET /health/upload`
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "pandas": "ok",
    "file_storage": "ok"
  },
  "stats": {
    "total_uploads": 1234,
    "active_files": 15,
    "avg_upload_time_ms": 1850
  }
}
```

---

## 10. Integration Points

### With Other Agents

| Agent | Integration Type | Data Exchanged |
|-------|------------------|----------------|
| Main Orchestrator | Request/Response | Upload metadata, file_id |
| Mapping Agent | Indirect (via file_id) | Column names, sample data |
| Validation Agent | Indirect (via file_id) | Full DataFrame for validation |
| Transform Agent | Indirect (via file_id) | Full DataFrame for transformation |

### With External Systems

- **File System**: Temporary in-memory storage (no disk I/O)
- **Browser**: Multipart form upload via HTTP

---

## 11. Questions This Agent Can Answer

1. "Upload my employee CSV file"
2. "What columns does my file have?"
3. "How many rows are in my file?"
4. "Show me a preview of my data"
5. "What data types were detected in each column?"
6. "Is my file format supported?"
7. "What's the file size limit?"
8. "Why did my upload fail?"
9. "Can I upload Excel files?"
10. "How do I upload a file?"

---

## 12. Questions This Agent CANNOT Answer

1. "What entity type is this file?" - Mapping Agent (via semantic matching)
2. "Is my data valid?" - Validation Agent
3. "Transform my data to Eightfold format" - Transform Agent
4. "Export my data as XML" - Export Agent
5. "Map fields automatically" - Mapping Agent
6. "Fix validation errors" - User action required
7. "Store files permanently" - Out of scope (in-memory only)

---

## Version History

### Version 1.0.0 (2025-11-06)
- Initial Upload Agent documentation
- CSV and Excel parsing implemented
- Automatic type detection
- File size validation (100MB limit)
- In-memory storage with file_id tracking
- Sample data generation

---

## Notes & Assumptions

- **Assumption 1**: Files are uploaded one at a time (no batch upload UI)
- **Assumption 2**: First sheet of Excel files is always the target sheet
- **Assumption 3**: File storage is ephemeral (1 hour TTL, no persistence)
- **Known Issue 1**: Files >50MB may take 5-10s to parse (acceptable for current use case)
- **Technical Debt 1**: No permanent storage - consider adding Redis/S3 for production scale
- **Technical Debt 2**: Type detection limited to basic types - enhance for domain-specific types (SSN, phone, etc.)
