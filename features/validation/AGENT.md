# Validation Agent

## Version 1.0.0 | Last Updated: 2025-11-06

---

## Agent Identity

**Name**: Validation Agent
**Version**: 1.0.0
**Status**: Active
**Owner**: SnapMap Core Team
**Domain**: Data Quality Validation
**Location**: `features/validation/AGENT.md`

---

## 1. Role & Responsibilities

### Primary Responsibilities

1. **Schema Validation**: Validate CSV structure against Eightfold entity schemas
2. **Header Validation**: Match headers to schema fields with typo detection
3. **Required Field Validation**: Ensure all required fields are present and populated
4. **Data Type Validation**: Validate email, date, numeric formats
5. **Data Quality Checks**: Detect invalid characters, encoding issues, max length violations
6. **Issue Reporting**: Generate detailed validation reports with severity levels
7. **Recovery Suggestions**: Provide actionable suggestions for fixing errors

### Data Sources

- **Uploaded DataFrames**: Source data from Upload Agent
- **Entity Schemas**: Target schema definitions (16 entity types)
- **Field Mappings**: Mapping configuration from Mapping Agent
- **Validation Rules**: Schema-defined validation rules per field

### Success Criteria

- **Validation Speed**: <10 seconds for 10,000+ row files
- **Accuracy**: >99% accuracy detecting critical errors
- **Coverage**: Validate 100% of required fields and data types
- **Actionability**: >95% of errors have recovery suggestions

---

## 2. Feature Capabilities

### What This Agent CAN Do

1. **Validate CSV structure** (empty files, duplicate columns, unnamed columns)
2. **Match headers to schema fields** with fuzzy matching for typo detection
3. **Check required fields** for presence and data completeness
4. **Validate email addresses** using regex patterns
5. **Validate date fields** with multiple format parsing
6. **Validate numeric fields** (integer, float)
7. **Detect invalid characters** (null bytes, control characters)
8. **Check max length constraints** per field
9. **Generate severity-based issues** (critical, warning, info)
10. **Provide row-level error counts** (how many rows affected)
11. **Suggest corrections** for misspelled headers
12. **Return structured ValidationIssue objects** with details and suggestions
13. **Support fuzzy header matching** (80%+ similarity = likely typo)

### What This Agent CANNOT Do

1. **Auto-fix validation errors** (provides suggestions only)
2. **Transform data** (delegates to Transform Agent)
3. **Map fields** (delegates to Mapping Agent)
4. **Modify source data** (read-only validation)
5. **Validate business logic** (e.g., "hire date must be before termination date")
6. **Validate cross-field relationships** (only single-field validation)
7. **Learn from user corrections** (static validation rules)
8. **Validate nested structures** (flat field validation only)
9. **Make autonomous data corrections** (user approval required)

---

## 3. Dependencies

### Required Dependencies

- **Pandas**: DataFrame operations - `import pandas as pd`
- **re**: Regex patterns - `import re`
- **schema_manager**: Entity schema access - `backend/app/services/schema_manager.py`
- **ValidationIssue model**: Response schema - Defined in `csv_validator.py`

### Optional Dependencies

- **Levenshtein**: Fuzzy string matching - Falls back to SequenceMatcher if missing
- **dateutil**: Advanced date parsing - Falls back to pandas if missing

### External Services

None (all validation is local)

---

## 4. Architecture & Implementation

### Key Files & Code Locations

#### Backend
- **API Endpoints**: `backend/app/api/endpoints/validate.py`
  - `POST /validate`: Main validation endpoint
  - Accepts file_id + entity_name + mappings
  - Returns validation report with issues

- **Services**: `backend/app/services/csv_validator.py` (Lines 1-551) **PRIMARY**
  - `validate_file()`: Main validation entry point (Lines 69-122)
  - `_validate_csv_structure()`: Check CSV structure (Lines 124-172)
  - `_validate_headers()`: Header matching with fuzzy logic (Lines 174-257)
  - `_check_required_fields()`: Required field validation (Lines 259-297)
  - `_validate_data_quality()`: Type and quality checks (Lines 299-342)
  - `_validate_email_field()`: Email validation (Lines 344-370)
  - `_validate_date_field()`: Date validation (Lines 372-405)
  - `_validate_numeric_field()`: Numeric validation (Lines 407-435)
  - `_check_invalid_characters()`: Character validation (Lines 437-470)
  - `_check_max_length()`: Length validation (Lines 472-498)
  - `_find_best_match()`: Fuzzy header matching (Lines 500-538)

- **Models**: `ValidationIssue` class (Lines 23-51)
  - `severity`, `issue_type`, `field`, `description`
  - `affected_rows`, `suggestion`
  - `to_dict()`: Convert to API response format

#### Frontend
- **Components**: `frontend/src/components/review/IssueReview.tsx`
  - Validation results display (Lines 1-350)
  - Issue filtering by severity
  - Field-level error details
  - Suggested fixes display
  - Error count badges

- **API Client**: `frontend/src/services/api.ts`
  - `validateData()`: Call validation endpoint

### Current State

#### Implemented Features
- [x] CSV structure validation
- [x] Header validation with fuzzy matching
- [x] Required field checks
- [x] Email format validation
- [x] Date format validation
- [x] Numeric type validation
- [x] Invalid character detection
- [x] Max length validation
- [x] Severity-based issue classification
- [x] Row-level error counting
- [x] Recovery suggestions
- [x] Typo detection and correction

#### In Progress
None currently

#### Planned
- [ ] Business logic validation: Cross-field rules (Priority: High)
- [ ] Custom validation rules: User-defined validators (Priority: Medium)
- [ ] Data profiling: Statistical data quality metrics (Priority: Low)
- [ ] Auto-fix suggestions: Automated correction proposals (Priority: High)
- [ ] Validation templates: Reusable rule sets (Priority: Medium)

---

## 5. Communication Patterns

### Incoming Requests (FROM)

**User (via Frontend)**
- **Action**: Validate data
- **Payload**: `{ file_id: string, entity_name: string, mappings?: Mapping[] }`
- **Response**: `{ is_valid: boolean, issues: ValidationIssue[], stats: {...} }`

**Main Orchestrator**
- **Action**: Validate before transformation
- **Payload**: DataFrame + entity schema + mappings
- **Response**: Validation report

### Outgoing Requests (TO)

**Schema Manager**
- **Action**: Get target schema
- **Purpose**: Retrieve validation rules and field definitions
- **Frequency**: Always (every validation request)

**File Storage**
- **Action**: Retrieve DataFrame
- **Purpose**: Get full data for validation
- **Frequency**: When file_id provided

### Data Flow Diagram

```
┌─────────────────────────┐
│  Upload Agent           │
│  - file_id              │
│  - DataFrame            │
└───────────┬─────────────┘
            │
            ↓
┌─────────────────────────┐
│  Mapping Agent          │
│  - field mappings       │
└───────────┬─────────────┘
            │
            ↓ file_id + entity_name + mappings
┌────────────────────────────────────────┐
│  Validation Agent                      │
│  1. Validate CSV structure             │
│  2. Validate headers (fuzzy match)     │
│  3. Check required fields              │
│  4. Validate data types (email/date)   │
│  5. Check data quality (chars/length)  │
│  6. Classify issues by severity        │
│  7. Generate recovery suggestions      │
│  8. Return validation report           │
└───────────┬────────────────────────────┘
            │
            ↓ ValidationReport
┌─────────────────────────┐
│  Frontend UI            │
│  - Display issues       │
│  - Filter by severity   │
│  - Show suggestions     │
│  - Block if critical    │
└─────────────────────────┘
```

---

## 6. Error Handling

### Common Errors

| Error Code | Severity | Description | Recovery |
|------------|----------|-------------|----------|
| `SCHEMA_ERROR` | Critical | Cannot load entity schema | Verify entity name is valid |
| `EMPTY_FILE` | Critical | CSV file has no data rows | Add data to file |
| `DUPLICATE_COLUMNS` | Critical | Duplicate column names found | Rename duplicate columns |
| `MISSING_REQUIRED_FIELD` | Critical | Required field not in file | Add column to CSV |
| `MISSING_REQUIRED_DATA` | Critical | Required field has empty values | Fill in missing values |
| `INVALID_EMAIL` | Warning | Email format incorrect | Fix email format (user@domain.com) |
| `INVALID_DATE` | Warning | Date cannot be parsed | Use YYYY-MM-DD format |
| `INVALID_NUMBER` | Warning | Non-numeric value in number field | Remove non-numeric characters |
| `MISSPELLED_HEADER` | Warning | Header appears to be typo | Rename to suggested field name |
| `UNKNOWN_HEADER` | Info | Header not in schema | Remove column or verify name |
| `EMPTY_COLUMNS` | Info | Column has no data | Remove column or add data |
| `NULL_BYTES` | Warning | Null bytes in data | Clean data encoding |
| `EXCEEDS_MAX_LENGTH` | Warning | Value exceeds max length | Truncate or shorten value |

### Error Response Format

```json
{
  "is_valid": false,
  "issues": [
    {
      "severity": "critical",
      "type": "missing_required_field",
      "field": "EMAIL",
      "description": "Required field 'EMAIL' is missing from the file",
      "affected_rows": "all",
      "suggestion": "Add EMAIL column to source file"
    },
    {
      "severity": "warning",
      "type": "invalid_email",
      "field": "email_address",
      "description": "Field 'email_address' has 15 invalid email addresses",
      "affected_rows": 15,
      "suggestion": "Fix email format to match user@domain.com"
    }
  ],
  "stats": {
    "total_issues": 2,
    "critical": 1,
    "warnings": 1,
    "info": 0
  }
}
```

### Validation Rules

1. **Critical Issues Block Pipeline**
   - **Severity**: Critical
   - **Rule**: Any critical issue prevents transformation
   - **Action**: User must fix before proceeding

2. **Warnings Allow Continuation**
   - **Severity**: Warning
   - **Rule**: Warnings are logged but don't block
   - **Action**: User can proceed with caution

3. **Info Issues Are Informational**
   - **Severity**: Info
   - **Rule**: Informational only
   - **Action**: No action required

---

## 7. Performance Considerations

### Performance Targets

- **Response Time**: <10s for 10,000 row files
- **Throughput**: 15 concurrent validation requests
- **Memory Usage**: Max 300MB (2x file size + validation overhead)
- **CPU Usage**: Max 60% per validation

### Optimization Strategies

1. **Vectorized operations**: Use pandas vectorized methods instead of loops
2. **Early termination**: Stop validation if critical errors found (optional)
3. **Lazy evaluation**: Only validate fields that are mapped
4. **Sampling for type detection**: Validate first 1000 rows for type checks
5. **Parallel validation**: Run independent checks concurrently

### Bottlenecks & Limitations

- **Large file validation**: 100,000+ row files take 30+ seconds
- **Complex regex**: Email/date validation is CPU-intensive
- **Memory for large DataFrames**: Entire DataFrame loaded in memory
- **No incremental validation**: Re-validates entire file on each request

---

## 8. Testing Checklist

### Unit Tests
- [ ] Detect empty CSV file
- [ ] Detect duplicate column names
- [ ] Detect missing required fields
- [ ] Validate email format (valid/invalid)
- [ ] Validate date format (multiple formats)
- [ ] Validate numeric fields
- [ ] Detect invalid characters
- [ ] Check max length violations
- [ ] Fuzzy match misspelled headers
- [ ] Generate recovery suggestions

### Integration Tests
- [ ] Upload → Mapping → Validation pipeline
- [ ] Validation blocks transformation if critical errors
- [ ] Validation allows transformation if warnings only
- [ ] Multiple concurrent validations

### Edge Cases
- [ ] File with all empty columns
- [ ] File with 100% invalid emails
- [ ] File with mixed date formats
- [ ] File with null bytes in all rows
- [ ] File with all columns unnamed
- [ ] File with 1000+ columns

### Performance Tests
- [ ] Test with 1,000 rows
- [ ] Test with 10,000 rows
- [ ] Test with 100,000 rows
- [ ] Test 10 concurrent validations
- [ ] Measure validation time per row

---

## 9. Maintenance

### When to Update This Document

- New validation rules added
- Severity thresholds changed
- New data types supported
- Error recovery suggestions improved
- Performance optimizations implemented

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Validation success rate | >95% | <90% (too many critical errors) |
| Average validation time | <5s | >15s |
| Critical error rate | <10% | >25% |
| False positive rate | <2% | >10% |
| Recovery suggestion accuracy | >90% | <75% |

### Health Check Endpoint

**Endpoint**: `GET /health/validation`
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "pandas": "ok",
    "schema_manager": "ok"
  },
  "stats": {
    "total_validations": 5678,
    "avg_validation_time_ms": 4250,
    "critical_error_rate": 0.08
  }
}
```

---

## 10. Integration Points

### With Other Agents

| Agent | Integration Type | Data Exchanged |
|-------|------------------|----------------|
| Upload Agent | Request | file_id, DataFrame |
| Mapping Agent | Request | Field mappings |
| Transform Agent | Response | Validation approval/rejection |
| Main Orchestrator | Request/Response | Validation reports |

### With External Systems

None (all validation is local)

---

## 11. Questions This Agent Can Answer

1. "Is my data valid against the Employee schema?"
2. "What validation errors were found?"
3. "Which fields have invalid data?"
4. "How many rows are affected by this error?"
5. "What's the suggested fix for this error?"
6. "Are there any critical errors?"
7. "Can I proceed to transformation?"
8. "Why is this header flagged as misspelled?"
9. "What email format is required?"
10. "Which required fields are missing?"

---

## 12. Questions This Agent CANNOT Answer

1. "Fix validation errors automatically" - User action required
2. "Transform my data" - Transform Agent
3. "Map fields to schema" - Mapping Agent
4. "Why did my upload fail?" - Upload Agent
5. "Create custom validation rules" - Not implemented (future)
6. "Validate business logic" - Not implemented (future)
7. "Learn from my corrections" - Static rules only

---

## Version History

### Version 1.0.0 (2025-11-06)
- Initial Validation Agent documentation
- CSV structure validation
- Header validation with fuzzy matching
- Required field checks
- Data type validation (email, date, numeric)
- Data quality checks (characters, length)
- Severity-based issue classification
- Recovery suggestions

---

## Notes & Assumptions

- **Assumption 1**: Validation is performed before transformation (quality gate)
- **Assumption 2**: Critical errors block pipeline, warnings allow continuation
- **Assumption 3**: Validation rules are static (no user customization yet)
- **Known Issue 1**: Large files (100K+ rows) slow to validate (acceptable for current use case)
- **Technical Debt 1**: No business logic validation (e.g., date range checks)
- **Technical Debt 2**: No custom validation rules - users can't define their own validators
- **Technical Debt 3**: No incremental validation - re-validates entire file on each request
