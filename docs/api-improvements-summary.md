# API Improvements Summary

This document outlines the improvements made to the SnapMap API to enhance usability and provide better error messages based on QA findings.

## Overview

The improvements focus on:
1. Enhanced response data with auto-detection
2. Simplified API calls (reduced required parameters)
3. Specific, actionable error messages
4. Better validation feedback with row-level details

---

## 1. Upload Endpoint Enhancement

**Endpoint:** `POST /api/upload`

**Improvements:**
- Auto-detects CSV delimiter (`,`, `;`, `|`, `\t`)
- Auto-detects character encoding (UTF-8, Latin-1, Windows-1252)
- Extracts source fields automatically
- Returns preview of first 5 rows

**Enhanced Response:**
```json
{
  "file_id": "abc123...",
  "filename": "candidates.csv",
  "row_count": 1213,
  "column_count": 22,
  "columns": ["PersonID", "FirstName", "LastName", ...],

  // NEW FIELDS:
  "detected_delimiter": "|",
  "detected_encoding": "utf-8",
  "source_fields": ["PersonID", "FirstName", "LastName", ...],
  "preview": [
    {"PersonID": "001", "FirstName": "John", ...},
    {...}
  ],

  "sample_data": [...],
  "data_types": {"PersonID": "string", "Email": "email", ...},
  "file_size": 524288
}
```

**Improved Error Messages:**

| Old Error | New Error |
|-----------|-----------|
| "Error parsing file" | "Could not parse file with comma delimiter. Detected pipe (\|) delimiter. File has 22 fields. Please specify delimiter or use auto-detection." |
| "Validation error" | "Character encoding issue detected at byte position 145. File contains characters incompatible with utf-8 encoding. Supported encodings: UTF-8, Latin-1 (ISO-8859-1), Windows-1252. Please convert the file to UTF-8 encoding." |

---

## 2. Auto-Map Endpoint Simplification

**Endpoint:** `POST /api/auto-map`

**Before:**
```json
{
  "source_fields": ["PersonID", "FirstName", "LastName", ...],  // Required
  "target_schema": "candidate",
  "min_confidence": 0.70
}
```

**After (Simplified):**
```json
{
  "file_id": "abc123",  // Just file_id - source_fields auto-extracted!
  "target_schema": "candidate",
  "min_confidence": 0.70
}
```

**How it works:**
- If `file_id` is provided, source fields are automatically extracted from the uploaded file
- `source_fields` is now optional - only needed if not using a previously uploaded file
- Reduces API calls and simplifies workflow

**Improved Error Messages:**

| Old Error | New Error |
|-----------|-----------|
| "HTTP 422 Unprocessable Entity" | "Data mapping failed. Only 3 of 22 fields mapped (13.6%). Required fields missing: CANDIDATE_ID, EMAIL, PHONE. Suggestion: Check field names or adjust mapping manually." |
| "Schema not found" | "Target schema 'employe' not found. Available schemas: employee, candidate. Check the schema name spelling." |

**Example Low Mapping Error:**
```json
{
  "error": {
    "code": "LOW_MAPPING_CONFIDENCE",
    "message": "Data mapping failed. Only 3 of 22 fields mapped (13.6%).",
    "details": {
      "mapped_count": 3,
      "total_source": 22,
      "mapping_percentage": 13.64,
      "required_fields_missing": ["CANDIDATE_ID", "EMAIL", "PHONE"],
      "unmapped_source_fields": ["PersonID", "Mail", "Tel", ...]
    },
    "suggestion": "Required fields missing: CANDIDATE_ID, EMAIL, PHONE. Check field names or adjust mapping manually."
  },
  "status": 422
}
```

---

## 3. New File Format Detection Endpoint

**Endpoint:** `POST /api/detect-file-format`

**Purpose:** Analyze file format without full parsing - useful for large files or pre-validation.

**Request:**
```
POST /api/detect-file-format
Content-Type: multipart/form-data

file: [uploaded file]
```

**Response:**
```json
{
  "delimiter": "|",
  "encoding": "utf-8",
  "has_header": true,
  "row_count": 1213,
  "field_count": 22,
  "preview_fields": ["PersonID", "FirstName", "LastName", ...],
  "special_characters_detected": ["ü", "ö", "ñ", "á"],
  "multi_value_fields": ["WorkEmails", "WorkPhones"],
  "suggested_entity": "candidate"
}
```

**Use Cases:**
- Pre-validate file format before upload
- Check encoding for files with special characters
- Identify multi-value fields (Siemens format with `||`)
- Get AI-based entity type suggestion

---

## 4. Enhanced Validation Error Messages

**Endpoint:** `POST /api/validate`

**Before:**
```json
{
  "error": "Validation error"
}
```

**After:**
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Validation failed for 5 record(s)",
    "details": {
      "total_errors": 5,
      "sample_errors": [
        "Row 3: Invalid email format: 'invalid.email'",
        "Row 7: Required field 'FIRST_NAME' is empty",
        "Row 12: Value '+invalid' doesn't match required pattern",
        "Row 15: Value exceeds maximum length of 100 characters (actual: 256)",
        "Row 22: Invalid date format: '32/13/2024'"
      ],
      "full_validation_result": { ... }
    },
    "suggestion": "Review the errors and fix the data. Download error report for complete details."
  },
  "status": 422
}
```

**Enhanced Validation Messages:**

All validation messages now include:
- Specific row numbers
- Actual invalid values (truncated if long)
- Clear suggestions for fixing
- Field display names (not just technical names)

**Examples:**

| Error Type | Message | Suggestion |
|------------|---------|------------|
| Empty required field | "Row 7: Required field 'First Name' is empty" | "Provide a value for First Name" |
| Invalid email | "Row 3: Invalid email format: 'john.doe'" | "Ensure email is in format: name@domain.com" |
| Invalid pattern | "Row 12: Value '+invalid' doesn't match required pattern" | "Value must match pattern: ^\+?[0-9]{10,15}$" |
| Too long | "Row 8: Value exceeds maximum length of 100 characters (actual: 256)" | "Truncate or shorten the value to 100 characters" |
| Invalid date | "Row 22: Invalid date format: '32/13/2024'" | "Date should be in format: YYYY-MM-DD" |

---

## 5. Common Error Code Reference

All API endpoints now return structured error responses with:
- `code`: Machine-readable error code
- `message`: Human-readable description
- `details`: Additional context (when applicable)
- `suggestion`: Actionable advice for fixing the issue
- `status`: HTTP status code

### Error Codes

| Code | Status | Endpoint | Description |
|------|--------|----------|-------------|
| `FILE_TOO_LARGE` | 413 | /upload | File exceeds 100 MB limit |
| `FILE_READ_ERROR` | 500 | /upload, /detect-file-format | Cannot read uploaded file |
| `INVALID_FILE_FORMAT` | 400 | /upload, /detect-file-format | Unsupported file format or corrupt file |
| `PARSE_ERROR` | 500 | /upload | Error parsing file content |
| `FORMAT_DETECTION_ERROR` | 500 | /detect-file-format | Cannot detect file format |
| `FILE_NOT_FOUND` | 404 | /auto-map | Uploaded file expired or invalid file_id |
| `INVALID_REQUEST` | 400 | /auto-map | Missing required parameters |
| `LOW_MAPPING_CONFIDENCE` | 422 | /auto-map | Too few fields mapped successfully |
| `SCHEMA_NOT_FOUND` | 404 | /auto-map, /validate | Invalid schema name |
| `AUTO_MAP_ERROR` | 500 | /auto-map | Error during field mapping |
| `VALIDATION_FAILED` | 422 | /validate | Data validation errors found |
| `VALIDATION_ERROR` | 500 | /validate | Error during validation process |

---

## 6. Workflow Improvements

### Before (4 API calls):
1. Upload file → get file_id
2. Parse response to extract columns
3. Call auto-map with columns → get mappings
4. Validate data

### After (2-3 API calls):
1. Upload file → get file_id + source_fields + preview (all in one!)
2. Call auto-map with just file_id → get mappings (simplified!)
3. Validate data

**API Call Reduction:** 33% fewer calls, simplified data flow

---

## 7. Technical Implementation Details

### File Parser Enhancements

**Location:** `c:\Code\SnapMap\backend\app\services\file_parser.py`

**New Methods:**
- `detect_file_format()`: Analyzes file without full parsing
- `parse_file()`: Now returns tuple (DataFrame, metadata)

**Detection Logic:**
- Tests multiple delimiters and selects one with most columns
- Uses `chardet` library for encoding detection
- Identifies multi-value fields by scanning for `||` separator
- Suggests entity type based on field name patterns

### Validation Enhancements

**Location:** `c:\Code\SnapMap\backend\app\services\validator.py`

**New Validations:**
- Required field emptiness check
- Email format validation (with actual value shown)
- Date format validation (with actual value shown)
- Max length validation (shows actual vs. expected length)
- Pattern matching validation (with regex pattern shown)

**Performance:**
- Limits error reports to first 100 per field to avoid overwhelming responses
- Truncates long values to 50 characters in error messages

---

## 8. Migration Guide

### For Frontend Developers

**No breaking changes!** All existing API calls will continue to work.

**Optional Enhancements:**
1. Use new response fields: `detected_delimiter`, `detected_encoding`, `source_fields`, `preview`
2. Simplify auto-map calls by using `file_id` instead of manually passing `source_fields`
3. Use `/detect-file-format` for large file pre-validation
4. Display enhanced error messages with row numbers and suggestions

**Example Migration:**

```javascript
// OLD WAY (still works):
const uploadRes = await fetch('/api/upload', ...);
const data = await uploadRes.json();
const sourceFields = data.columns;  // Extract manually

await fetch('/api/auto-map', {
  body: JSON.stringify({
    source_fields: sourceFields,  // Manual extraction
    target_schema: 'candidate'
  })
});

// NEW WAY (simplified):
const uploadRes = await fetch('/api/upload', ...);
const data = await uploadRes.json();
// data.source_fields already available!
// data.detected_delimiter tells you the format
// data.preview gives you a sample

await fetch('/api/auto-map', {
  body: JSON.stringify({
    file_id: data.file_id,  // Just use file_id!
    target_schema: 'candidate'
  })
});
```

---

## 9. Testing Recommendations

1. **Test delimiter detection:**
   - Upload CSV with comma delimiter
   - Upload CSV with pipe delimiter
   - Upload CSV with tab delimiter
   - Upload CSV with semicolon delimiter

2. **Test encoding detection:**
   - Upload file with UTF-8 encoding
   - Upload file with special characters (ü, ö, ñ, á)
   - Upload file with Latin-1 encoding
   - Upload file with Windows-1252 encoding

3. **Test error messages:**
   - Upload invalid file format (.txt)
   - Upload corrupt CSV file
   - Call auto-map with expired file_id
   - Validate data with missing required fields
   - Validate data with invalid email formats

4. **Test auto-extraction:**
   - Upload file and call auto-map with only file_id
   - Verify source_fields are correctly extracted
   - Test with different schemas (employee, candidate)

---

## Success Criteria - All Met!

- [x] Reduced API calls (auto-extract source_fields from file_id)
- [x] Error messages show specific row numbers
- [x] Suggest fixes in error responses
- [x] Add file format detection endpoint
- [x] Improved delimiter and encoding detection
- [x] Enhanced validation with detailed feedback
- [x] Backward compatible (no breaking changes)

---

## Files Modified

1. `c:\Code\SnapMap\backend\app\services\file_parser.py` - Enhanced parsing and detection
2. `c:\Code\SnapMap\backend\app\models\upload.py` - Added new response fields
3. `c:\Code\SnapMap\backend\app\api\endpoints\upload.py` - Enhanced upload and added detect-file-format
4. `c:\Code\SnapMap\backend\app\models\mapping.py` - Made source_fields optional
5. `c:\Code\SnapMap\backend\app\api\endpoints\automapping.py` - Auto-extract from file_id
6. `c:\Code\SnapMap\backend\app\api\endpoints\validate.py` - Better error messages
7. `c:\Code\SnapMap\backend\app\services\validator.py` - Row-level validation details

---

## Next Steps

1. Update frontend to use new response fields
2. Add error message display with row numbers
3. Implement "Download error report" feature
4. Add file format pre-check before upload for large files
5. Consider adding batch validation API for large datasets
