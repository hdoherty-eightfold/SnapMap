# Export Agent

## Version 1.0.0 | Last Updated: 2025-11-06

---

## Agent Identity

**Name**: Export Agent
**Version**: 1.0.0
**Status**: Active
**Owner**: SnapMap Core Team
**Domain**: File Export & Download
**Location**: `features/export/AGENT.md`

---

## 1. Role & Responsibilities

### Primary Responsibilities

1. **CSV Export**: Generate downloadable CSV files from transformed data
2. **XML Export**: Generate downloadable XML files (Eightfold format)
3. **File Streaming**: Stream file content to browser for download
4. **Filename Management**: Generate appropriate filenames with extensions
5. **Content-Type Headers**: Set correct MIME types for downloads
6. **Encoding Management**: Ensure UTF-8 encoding for all exports

### Data Sources

- **Transformed DataFrames**: From Transform Agent
- **XML Strings**: From XML Transformer
- **File Storage**: Retrieve source data by file_id

### Success Criteria

- **Export Speed**: <5 seconds for 10,000 row files
- **File Integrity**: 100% data preservation in export
- **Format Compliance**: 100% valid CSV/XML format
- **Download Success Rate**: >99% successful downloads

---

## 2. Feature Capabilities

### What This Agent CAN Do

1. **Export CSV files** with UTF-8 encoding
2. **Export XML files** (Eightfold EF_Employee_List format)
3. **Stream file downloads** to browser
4. **Generate filenames** automatically or use user-provided names
5. **Set Content-Disposition headers** for proper browser download
6. **Handle large files** (up to 100MB)
7. **Support file_id or explicit data** as input
8. **Return StreamingResponse** for efficient download
9. **Preserve data integrity** (no data loss in export)
10. **Handle CSV special characters** (quotes, commas, newlines)
11. **Pretty-print XML** with proper indentation
12. **Generate proper MIME types** (text/csv, application/xml)

### What This Agent CANNOT Do

1. **Transform data** (delegates to Transform Agent)
2. **Validate data** (delegates to Validation Agent)
3. **Upload to SFTP** (delegates to SFTP Agent)
4. **Store files permanently** (generates on-demand, no persistence)
5. **Export to other formats** (JSON, Excel, PDF not supported)
6. **Compress files** (no .zip or .gz generation)
7. **Split large files** (single file export only)
8. **Email files** (download only)
9. **Schedule exports** (on-demand only)

---

## 3. Dependencies

### Required Dependencies

- **FastAPI**: StreamingResponse - `from fastapi.responses import StreamingResponse`
- **io.StringIO**: In-memory file buffer - `from io import StringIO`
- **Pandas**: CSV generation - `df.to_csv()`
- **Transform Agent**: Data transformation
- **XML Transformer**: XML generation

### Optional Dependencies

None (all dependencies are required)

### External Services

None (all export is local)

---

## 4. Architecture & Implementation

### Key Files & Code Locations

#### Backend
- **API Endpoints**: `backend/app/api/endpoints/transform.py`
  - `POST /transform/export`: Export CSV (Lines 70-161)
    - Accept source_data or file_id
    - Transform data
    - Generate CSV
    - Return StreamingResponse
  - `POST /transform/export-xml`: Export XML (Lines 238-331)
    - Accept source_data or file_id
    - Transform to XML
    - Return StreamingResponse

- **Services**:
  - Transform Agent: Transforms data before export
  - XML Transformer: Generates XML structure
  - File Storage: Retrieves data by file_id

#### Frontend
- **Components**:
  - `frontend/src/components/export/PreviewCSV.tsx` - CSV preview with export button
  - `frontend/src/components/export/PreviewXML.tsx` - XML preview with export button
  - Export buttons trigger download

- **API Client**: `frontend/src/services/api.ts`
  - `exportCSV()`: Trigger CSV download
  - `exportXML()`: Trigger XML download

### Current State

#### Implemented Features
- [x] CSV export with UTF-8 encoding
- [x] XML export (EF_Employee_List format)
- [x] StreamingResponse for downloads
- [x] Automatic filename generation
- [x] Content-Disposition headers
- [x] Support for file_id and source_data
- [x] Pretty-printed XML output
- [x] Error handling with detailed messages

#### In Progress
None currently

#### Planned
- [ ] Excel export: Generate .xlsx files (Priority: Medium)
- [ ] JSON export: Generate JSON format (Priority: Low)
- [ ] File compression: .zip for large files (Priority: Low)
- [ ] Batch export: Multiple files at once (Priority: Medium)
- [ ] Email export: Send files via email (Priority: Low)

---

## 5. Communication Patterns

### Incoming Requests (FROM)

**User (via Frontend)**
- **Action**: Export CSV
- **Payload**: `{ mappings: Mapping[], source_data?: any[], file_id?: string, entity_name: string, output_filename: string }`
- **Response**: StreamingResponse (file download)

**User (via Frontend)**
- **Action**: Export XML
- **Payload**: Same as CSV
- **Response**: StreamingResponse (XML file download)

### Outgoing Requests (TO)

**Transform Agent**
- **Action**: Transform data
- **Purpose**: Get transformed DataFrame or XML
- **Frequency**: Always (before export)

**File Storage**
- **Action**: Retrieve DataFrame
- **Purpose**: Get source data when file_id provided
- **Frequency**: When file_id used instead of source_data

### Data Flow Diagram

```
┌─────────────────────────┐
│  Transform Agent        │
│  - Transformed data     │
└───────────┬─────────────┘
            │
            ↓ transformed DataFrame or XML
┌────────────────────────────────────┐
│  Export Agent                      │
│  CSV Export:                       │
│  1. Convert DataFrame to CSV       │
│  2. Create StringIO buffer         │
│  3. Write CSV content              │
│  4. Set MIME type (text/csv)       │
│  5. Set filename header            │
│  6. Return StreamingResponse       │
│                                     │
│  XML Export:                       │
│  1. Get XML string from Transform  │
│  2. Encode to UTF-8 bytes          │
│  3. Set MIME type (application/xml)│
│  4. Set filename header            │
│  5. Return StreamingResponse       │
└───────────┬────────────────────────┘
            │
            ↓ File download
┌─────────────────────────┐
│  Browser                │
│  - Download file        │
│  - Save to disk         │
└─────────────────────────┘
```

---

## 6. Error Handling

### Common Errors

| Error Code | Severity | Description | Recovery |
|------------|----------|-------------|----------|
| `EXPORT_ERROR` | Critical | Error exporting CSV | Check data format and mappings |
| `XML_EXPORT_ERROR` | Critical | Error exporting XML | Verify data and XML structure |
| `FILE_NOT_FOUND` | Critical | file_id not found | Re-upload file or provide source_data |
| `MISSING_SOURCE_DATA` | Critical | Neither source_data nor file_id provided | Provide data source |
| `TRANSFORMATION_ERROR` | Critical | Error during transformation | Check Transform Agent |
| `ENCODING_ERROR` | Warning | Character encoding issue | Verify UTF-8 compatibility |

### Error Response Format

```json
{
  "status": 500,
  "error": {
    "code": "EXPORT_ERROR",
    "message": "Error exporting CSV: 'list' object has no attribute 'to_csv'",
    "details": {
      "file_id": "abc123",
      "entity_name": "employee"
    }
  }
}
```

### Validation Rules

1. **Data Source Validation**
   - **Severity**: Critical
   - **Rule**: Either source_data or file_id must be provided
   - **Action**: Return HTTP 400 if both missing

2. **Filename Extension**
   - **Severity**: Info
   - **Rule**: Add .csv or .xml extension if missing
   - **Action**: Auto-append extension

3. **UTF-8 Encoding**
   - **Severity**: Warning
   - **Rule**: All exports use UTF-8 encoding
   - **Action**: Warn if non-UTF-8 characters detected

---

## 7. Performance Considerations

### Performance Targets

- **Response Time**: <5s for 10,000 row files
- **Throughput**: 25 concurrent exports
- **Memory Usage**: Max 200MB per export
- **CPU Usage**: Max 40% per export

### Optimization Strategies

1. **Streaming response**: Stream file to browser without full buffering
2. **Pandas to_csv optimization**: Use efficient pandas CSV writer
3. **Lazy XML generation**: Build XML incrementally
4. **Memory cleanup**: Delete buffers after streaming
5. **Concurrent exports**: Support parallel export requests

### Bottlenecks & Limitations

- **Large CSV export**: 100,000 rows takes 10-15s
- **XML is slower than CSV**: XML export 2x slower than CSV
- **Memory for large files**: Entire file in memory before streaming
- **No compression**: Large files not compressed (future enhancement)

---

## 8. Testing Checklist

### Unit Tests
- [ ] Export CSV with valid data
- [ ] Export XML with valid data
- [ ] Handle file_id correctly
- [ ] Handle source_data correctly
- [ ] Generate filename with extension
- [ ] Set correct MIME types
- [ ] Handle missing source_data and file_id
- [ ] Preserve UTF-8 encoding

### Integration Tests
- [ ] Transform → Export CSV pipeline
- [ ] Transform → Export XML pipeline
- [ ] Upload → Map → Transform → Export
- [ ] Multiple concurrent exports
- [ ] Large file export (100MB)

### Edge Cases
- [ ] Export with 0 rows
- [ ] Export with special characters in data
- [ ] Export with very long column names
- [ ] Export with null values
- [ ] Export with non-ASCII characters
- [ ] Filename with special characters

### Performance Tests
- [ ] Test with 1,000 rows
- [ ] Test with 10,000 rows
- [ ] Test with 100,000 rows
- [ ] Test 10 concurrent exports
- [ ] Measure download time

---

## 9. Maintenance

### When to Update This Document

- New export formats added (Excel, JSON)
- Export performance optimized
- File compression implemented
- Batch export added
- Error handling improved

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Export success rate | >99% | <95% |
| Average export time | <5s | >15s |
| Download completion rate | >98% | <90% |
| Encoding errors | <0.1% | >1% |
| Memory usage per export | <200MB | >500MB |

### Health Check Endpoint

**Endpoint**: `GET /health/export`
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "pandas": "ok",
    "transform_agent": "ok"
  },
  "stats": {
    "total_exports": 12456,
    "csv_exports": 7823,
    "xml_exports": 4633,
    "avg_export_time_ms": 3850
  }
}
```

---

## 10. Integration Points

### With Other Agents

| Agent | Integration Type | Data Exchanged |
|-------|------------------|----------------|
| Transform Agent | Request | Transformed data for export |
| File Storage | Request | Retrieve data by file_id |
| SFTP Agent | Response | File path for upload |
| Main Orchestrator | Request/Response | Export requests, file downloads |

### With External Systems

- **Browser**: File download via HTTP StreamingResponse

---

## 11. Questions This Agent Can Answer

1. "Export my transformed data as CSV"
2. "Export my data as Eightfold XML"
3. "Download the transformed file"
4. "What filename will be used?"
5. "What encoding is used for export?"
6. "How long will export take?"
7. "Can I export large files?"
8. "What file formats are supported?"
9. "How do I download the file?"
10. "Is the export data the same as transformed?"

---

## 12. Questions This Agent CANNOT Answer

1. "Transform my data" - Transform Agent
2. "Upload to SFTP server" - SFTP Agent
3. "Validate my data" - Validation Agent
4. "Email me the file" - Not implemented
5. "Export to Excel format" - Not implemented
6. "Compress the file" - Not implemented
7. "Schedule exports" - Not implemented

---

## Version History

### Version 1.0.0 (2025-11-06)
- Initial Export Agent documentation
- CSV export with UTF-8 encoding
- XML export (Eightfold format)
- StreamingResponse for downloads
- Filename generation
- Content-Disposition headers

---

## Notes & Assumptions

- **Assumption 1**: Files are exported on-demand (no persistence)
- **Assumption 2**: Downloads are browser-initiated (no server-side storage)
- **Assumption 3**: UTF-8 encoding is universally acceptable
- **Known Issue 1**: Large XML exports (100K+ rows) slow (acceptable for current use case)
- **Technical Debt 1**: No file compression - large files consume bandwidth
- **Technical Debt 2**: No Excel export - some users prefer .xlsx format
- **Technical Debt 3**: No batch export - users can't export multiple entities at once
