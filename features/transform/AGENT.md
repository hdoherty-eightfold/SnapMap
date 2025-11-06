# Transform Agent

## Version 1.0.0 | Last Updated: 2025-11-06

---

## Agent Identity

**Name**: Transform Agent
**Version**: 1.0.0
**Status**: Active
**Owner**: SnapMap Core Team
**Domain**: Data Transformation
**Location**: `features/transform/AGENT.md`

---

## 1. Role & Responsibilities

### Primary Responsibilities

1. **CSV Transformation**: Transform source data to target schema structure
2. **XML Transformation**: Generate Eightfold XML format (EF_Employee_List)
3. **Data Type Conversion**: Convert dates, numbers, booleans to target formats
4. **Field Mapping Application**: Apply user-approved field mappings
5. **Default Value Generation**: Auto-generate required fields (e.g., timestamps)
6. **Transformation Preview**: Generate sample transformed data for review
7. **Transformation Logging**: Track all transformations applied

### Data Sources

- **Source DataFrames**: Uploaded data from Upload Agent
- **Field Mappings**: User-approved mappings from Mapping Agent
- **Entity Schemas**: Target schema definitions
- **Validation Results**: Validated data from Validation Agent

### Success Criteria

- **Transform Speed**: <3 seconds for 10,000 row files
- **Data Accuracy**: 100% data preservation (no data loss)
- **Format Compliance**: 100% compliant with Eightfold schemas
- **Transformation Coverage**: All mapped fields transformed

---

## 2. Feature Capabilities

### What This Agent CAN Do

1. **Transform CSV to Eightfold CSV** (mapped columns, proper formatting)
2. **Transform CSV to Eightfold XML** (EF_Employee_List structure)
3. **Convert date formats** to YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
4. **Convert boolean values** to true/false strings
5. **Handle multiple values** in list fields (email_list, phone_list)
6. **Generate timestamps** for required timestamp fields (LAST_ACTIVITY_TS)
7. **Apply 1:1 field mappings** from source to target columns
8. **Create target DataFrame** with only mapped/required fields
9. **Pretty-print XML** with proper indentation
10. **Track transformations** applied (log of changes)
11. **Generate transformation previews** (sample of first 5-10 rows)
12. **Handle unmapped fields** gracefully (skip or default)

### What This Agent CANNOT Do

1. **Validate data quality** (delegates to Validation Agent)
2. **Map fields automatically** (delegates to Mapping Agent)
3. **Store transformed files** (delegates to Export Agent)
4. **Upload to SFTP** (delegates to SFTP Agent)
5. **Merge multiple source fields** into one target (1:1 only)
6. **Split one source field** into multiple targets
7. **Apply complex transformations** (e.g., lookups, calculations)
8. **Modify source data** (read-only, creates new output)
9. **Recover from Pydantic model errors** (requires compatible data)

---

## 3. Dependencies

### Required Dependencies

- **Pandas**: DataFrame transformations - `import pandas as pd`
- **xml.etree.ElementTree**: XML generation - `from xml.etree.ElementTree import Element, SubElement`
- **xml.dom.minidom**: XML pretty-printing - `from xml.dom import minidom`
- **datetime**: Timestamp generation - `from datetime import datetime`
- **TransformationEngine**: CSV transform - `backend/app/services/transformer.py`
- **XMLTransformer**: XML transform - `backend/app/services/xml_transformer.py`

### Optional Dependencies

None (all dependencies are required)

### External Services

None (all transformation is local)

---

## 4. Architecture & Implementation

### Key Files & Code Locations

#### Backend
- **API Endpoints**: `backend/app/api/endpoints/transform.py` (Lines 1-332)
  - `POST /transform/preview`: Preview CSV transformation (Lines 18-67)
  - `POST /transform/export`: Export transformed CSV (Lines 70-161)
  - `POST /transform/preview-xml`: Preview XML transformation (Lines 163-236)
  - `POST /transform/export-xml`: Export transformed XML (Lines 238-331)

- **Services**:
  - `backend/app/services/transformer.py` (Lines 1-103) **CSV TRANSFORM**
    - `transform_data()`: Main CSV transformation (Lines 18-75)
    - `_transform_date()`: Date format conversion (Lines 77-90)

  - `backend/app/services/xml_transformer.py` (Lines 1-310) **XML TRANSFORM**
    - `transform_csv_to_xml()`: Main XML transformation (Lines 64-101)
    - `_create_employee_element()`: Generate employee XML (Lines 103-149)
    - `_add_list_element()`: Handle list fields (Lines 189-224)
    - `_format_value()`: Format values by type (Lines 242-283)
    - `_prettify_xml()`: Pretty-print XML (Lines 285-297)

- **Models**: `backend/app/models/transform.py`
  - `PreviewRequest`: Preview request (mappings, source_data, entity_name)
  - `PreviewResponse`: Preview response (transformed_data, transformations_applied)
  - `ExportRequest`: Export request (mappings, source_data/file_id, output_filename)

#### Frontend
- **Components**:
  - `frontend/src/components/export/PreviewCSV.tsx` - CSV preview
  - `frontend/src/components/export/PreviewXML.tsx` - XML preview
  - Preview tables with before/after comparison

- **API Client**: `frontend/src/services/api.ts`
  - `previewTransformation()`: Preview CSV
  - `previewXMLTransformation()`: Preview XML
  - `exportCSV()`: Export CSV
  - `exportXML()`: Export XML

### Current State

#### Implemented Features
- [x] CSV transformation with field mapping
- [x] XML transformation (EF_Employee_List format)
- [x] Date format conversion
- [x] Boolean conversion
- [x] List field handling (email_list, phone_list)
- [x] Auto-generate timestamps
- [x] Transformation preview (CSV and XML)
- [x] Transformation logging
- [x] Pretty-printed XML output

#### In Progress
None currently

#### Planned
- [ ] Complex transformations: Concatenate, split, lookup (Priority: High)
- [ ] Transformation templates: Save/reuse transformation logic (Priority: Medium)
- [ ] Data enrichment: Add calculated fields (Priority: Low)
- [ ] Multi-entity transformation: Support all 16 entity types (Priority: High)
- [ ] Incremental transformation: Transform only changed rows (Priority: Low)

---

## 5. Communication Patterns

### Incoming Requests (FROM)

**User (via Frontend)**
- **Action**: Preview transformation
- **Payload**: `{ mappings: Mapping[], source_data: any[], entity_name: string, sample_size?: number }`
- **Response**: `{ transformed_data: any[], transformations_applied: string[], row_count: number }`

**Export Agent**
- **Action**: Transform for export
- **Payload**: Mappings + source data or file_id
- **Response**: Transformed DataFrame or XML string

### Outgoing Requests (TO)

**Schema Manager**
- **Action**: Get target schema
- **Purpose**: Retrieve field definitions and types
- **Frequency**: Always (every transformation)

**File Storage**
- **Action**: Retrieve source DataFrame
- **Purpose**: Get full data when file_id provided
- **Frequency**: When using file_id instead of explicit source_data

### Data Flow Diagram

```
┌─────────────────────────┐
│  Validation Agent       │
│  - Approved data        │
└───────────┬─────────────┘
            │
            ↓ mappings + source_data/file_id
┌────────────────────────────────────────┐
│  Transform Agent                       │
│  CSV Transform:                        │
│  1. Create target DataFrame            │
│  2. Apply field mappings               │
│  3. Convert data types                 │
│  4. Generate default values            │
│  5. Log transformations                │
│                                         │
│  XML Transform:                        │
│  1. Iterate rows as EF_Employee        │
│  2. Map fields to XML elements         │
│  3. Handle list elements               │
│  4. Format dates/values                │
│  5. Pretty-print XML                   │
└───────────┬────────────────────────────┘
            │
            ↓ transformed DataFrame/XML
┌─────────────────────────┐
│  Export Agent           │
│  - Generate files       │
└─────────────────────────┘
```

---

## 6. Error Handling

### Common Errors

| Error Code | Severity | Description | Recovery |
|------------|----------|-------------|----------|
| `TRANSFORMATION_ERROR` | Critical | Error during CSV transformation | Check mappings and data types |
| `XML_PREVIEW_ERROR` | Critical | Error generating XML preview | Verify Pydantic model compatibility |
| `XML_EXPORT_ERROR` | Critical | Error exporting XML | Check data format and mappings |
| `EXPORT_ERROR` | Critical | Error exporting CSV | Verify file_id or source_data |
| `FILE_NOT_FOUND` | Critical | file_id not found in storage | Re-upload file |
| `MISSING_SOURCE_DATA` | Critical | Neither source_data nor file_id provided | Provide data source |
| `SCHEMA_NOT_FOUND` | Critical | Entity schema not found | Verify entity_name |
| `PYDANTIC_COMPATIBILITY` | Critical | Mapping model version mismatch | Update Pydantic models |

### Error Response Format

```json
{
  "status": 500,
  "error": {
    "code": "TRANSFORMATION_ERROR",
    "message": "Error during transformation: 'NoneType' object has no attribute 'target'",
    "traceback": "[Full stack trace]"
  }
}
```

### Validation Rules

1. **Data Preservation**
   - **Severity**: Critical
   - **Rule**: No data loss during transformation
   - **Action**: Verify row counts match before/after

2. **Schema Compliance**
   - **Severity**: Critical
   - **Rule**: Output must match target schema exactly
   - **Action**: Validate against schema after transformation

3. **Date Format Compliance**
   - **Severity**: Warning
   - **Rule**: Dates should match YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
   - **Action**: Log warning if format cannot be converted

---

## 7. Performance Considerations

### Performance Targets

- **Response Time**: <3s for 10,000 row files
- **Throughput**: 20 concurrent transformations
- **Memory Usage**: Max 400MB (source + target DataFrames)
- **CPU Usage**: Max 50% per transformation

### Optimization Strategies

1. **Vectorized pandas operations**: Use pandas native methods instead of loops
2. **Lazy XML generation**: Build XML incrementally without full in-memory tree
3. **Type conversion caching**: Cache date parsing results for repeated values
4. **Batch processing**: Transform multiple rows at once
5. **Memory cleanup**: Delete intermediate DataFrames after export

### Bottlenecks & Limitations

- **XML generation is slow**: 10,000 rows takes 8-10s (acceptable for current use case)
- **Memory for large files**: Both source and target in memory (2x memory usage)
- **Date parsing overhead**: Complex date parsing is CPU-intensive
- **No streaming**: Entire output generated before return

---

## 8. Testing Checklist

### Unit Tests
- [ ] Transform CSV with valid mappings
- [ ] Transform XML with valid mappings
- [ ] Convert date formats correctly
- [ ] Handle boolean values
- [ ] Generate timestamps for required fields
- [ ] Handle missing/null values
- [ ] Handle list fields (multiple emails)
- [ ] Pretty-print XML correctly
- [ ] Track transformations applied

### Integration Tests
- [ ] Upload → Mapping → Transform pipeline
- [ ] Transform → Export pipeline
- [ ] Preview before export
- [ ] Handle file_id vs source_data
- [ ] Multiple concurrent transformations

### Edge Cases
- [ ] Transform with 0 mappings
- [ ] Transform with all fields mapped
- [ ] Transform with unmapped required fields
- [ ] Transform with invalid date formats
- [ ] Transform empty DataFrame
- [ ] Transform with special characters in data

### Performance Tests
- [ ] Test with 1,000 rows (CSV and XML)
- [ ] Test with 10,000 rows (CSV and XML)
- [ ] Test with 100,000 rows
- [ ] Test 10 concurrent transformations
- [ ] Measure memory usage

---

## 9. Maintenance

### When to Update This Document

- New transformation types added (e.g., JSON)
- New entity types supported
- Transformation rules changed
- Performance optimizations implemented
- XML schema updated

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Transform success rate | >99% | <95% |
| Average transform time | <3s | >10s |
| Data loss incidents | 0 | >0 |
| XML validation failures | <1% | >5% |
| Memory usage per transform | <400MB | >1GB |

### Health Check Endpoint

**Endpoint**: `GET /health/transform`
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "pandas": "ok",
    "xml_transformer": "ok",
    "schema_manager": "ok"
  },
  "stats": {
    "total_transforms": 8901,
    "avg_transform_time_ms": 2650,
    "xml_transforms": 4523,
    "csv_transforms": 4378
  }
}
```

---

## 10. Integration Points

### With Other Agents

| Agent | Integration Type | Data Exchanged |
|-------|------------------|----------------|
| Validation Agent | Request | Validated data for transformation |
| Mapping Agent | Request | Field mappings |
| Export Agent | Response | Transformed data for export |
| File Storage | Request | Retrieve source data by file_id |

### With External Systems

None (all transformation is local)

---

## 11. Questions This Agent Can Answer

1. "Transform my data to Eightfold CSV format"
2. "Generate Eightfold XML from my data"
3. "Show me a preview of the transformation"
4. "What transformations were applied?"
5. "How many rows were transformed?"
6. "What date format is used in the output?"
7. "How are list fields handled?" (email_list, phone_list)
8. "What happens to unmapped fields?"
9. "Can I preview before exporting?"
10. "How long will transformation take?"

---

## 12. Questions This Agent CANNOT Answer

1. "Validate my data" - Validation Agent
2. "Map my fields automatically" - Mapping Agent
3. "Export to file" - Export Agent
4. "Upload to SFTP" - SFTP Agent
5. "Fix transformation errors" - User action required
6. "Create custom transformations" - Not implemented
7. "Transform to custom formats" - Eightfold format only

---

## Version History

### Version 1.0.0 (2025-11-06)
- Initial Transform Agent documentation
- CSV transformation implemented
- XML transformation (EF_Employee_List)
- Date format conversion
- List field handling
- Timestamp auto-generation
- Preview functionality

---

## Notes & Assumptions

- **Assumption 1**: Data is validated before transformation (quality gate)
- **Assumption 2**: Mappings are user-approved (no auto-correction)
- **Assumption 3**: Only Employee entity type fully tested (16 schemas exist)
- **Known Issue 1**: XML generation slow for large files (acceptable trade-off for accuracy)
- **Technical Debt 1**: No complex transformations (split/merge/calculate fields)
- **Technical Debt 2**: Only Employee entity type tested - need to test all 16 types
- **Technical Debt 3**: No transformation templates - users can't save/reuse logic
