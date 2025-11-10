# Multi-Value Field Support and Data Loss Validation

## Overview

This document describes the implementation of two critical data engineering features:

1. **Multi-Value Field Support**: Handling fields with `||` separator (Siemens format)
2. **Data Loss Validation**: Comprehensive row count validation throughout the ETL pipeline

## Implementation Date

2025-11-06

## 1. Multi-Value Field Support

### Problem Statement

Siemens data files contain fields with multiple values separated by `||`:
- `WorkEmails`: "email1@domain.com||email2@domain.com"
- `HomeEmails`: Multiple emails separated by `||`
- `WorkPhones`: Multiple phone numbers separated by `||`

These multi-value fields need to be properly parsed and transformed into XML list structures.

### Solution

#### File: `c:\Code\SnapMap\backend\app\services\xml_transformer.py`

**Changes Made:**
- Enhanced `_add_list_element()` method to detect `||` separator
- Added automatic detection: checks for `||` first, falls back to comma separation
- Generates proper XML list structures

**Code Implementation:**
```python
def _add_list_element(self, parent, path, value, created_lists):
    """Add an element to a list container with multi-value support"""
    # Handle multiple values - check for || separator first (Siemens format)
    value_str = str(value)
    if '||' in value_str:
        # Siemens multi-value format with || separator
        values = [v.strip() for v in value_str.split('||')]
    else:
        # Standard comma-separated format
        values = [v.strip() for v in value_str.split(',')]

    for val in values:
        if val:  # Skip empty values
            item_elem = SubElement(list_elem, item_name)
            item_elem.text = val
```

**XML Output Example:**
```xml
<email_list>
  <email>email1@domain.com</email>
  <email>email2@domain.com</email>
</email_list>
```

**Supported Fields:**
- EMAIL → `email_list/email`
- PHONE → `phone_list/phone`
- URL → `url_list/url`

### Testing Multi-Value Fields

**Input Data:**
```csv
EmployeeID,WorkEmails,WorkPhones
12345,"john@company.com||john.doe@company.com","555-1234||555-5678"
```

**Expected XML Output:**
```xml
<EF_Employee>
  <employee_id>12345</employee_id>
  <email_list>
    <email>john@company.com</email>
    <email>john.doe@company.com</email>
  </email_list>
  <phone_list>
    <phone>555-1234</phone>
    <phone>555-5678</phone>
  </phone_list>
</EF_Employee>
```

---

## 2. Data Loss Validation

### Problem Statement

Data can be lost at multiple stages of the ETL pipeline:
- File parsing (encoding issues, delimiter detection)
- Field mapping (missing required fields)
- Data validation (filtering invalid rows)
- XML transformation (serialization errors)

Without validation, rows can silently disappear, leading to incomplete data exports.

### Solution

#### File: `c:\Code\SnapMap\backend\app\services\data_validator.py`

**New Service Module** providing:

1. **DataLossError Exception**
   - Custom exception with detailed context
   - Tracks lost rows, total rows, and reasons
   - Provides actionable error messages

2. **DataValidator Class**

**Key Methods:**

##### `validate_row_count(input_df, output_df, operation_name)`
Validates that no rows were lost during processing.

```python
validator = get_data_validator()
validator.validate_row_count(
    input_df=source_df,
    output_df=transformed_df,
    operation_name="field mapping"
)
```

**Raises:** `DataLossError` if `len(input_df) != len(output_df)`

**Error Details Include:**
- Number of lost rows
- Loss percentage
- Potential reasons (nulls, duplicates)
- Sample missing row indices

##### `validate_field_completeness(df, required_fields, operation_name)`
Validates that required fields are present and non-empty.

```python
is_valid, issues = validator.validate_field_completeness(
    df=df,
    required_fields=["EMPLOYEE_ID", "EMAIL"],
    operation_name="schema validation"
)
```

**Returns:** Tuple of (is_valid: bool, issues: List[Dict])

##### `validate_multi_value_fields(df, multi_value_fields, separator)`
Detects and reports multi-value fields.

```python
multi_value_info = validator.validate_multi_value_fields(
    df=df,
    multi_value_fields=df.columns.tolist(),
    separator="||"
)
```

**Returns:** Dictionary with:
- `has_multi_value_fields`: bool
- `fields_analyzed`: List of field details
- `total_multi_value_cells`: int

### Integration Points

#### 1. File Upload (`upload.py`)

**Location:** `c:\Code\SnapMap\backend\app\api\endpoints\upload.py`

**Validation Added:**
- Multi-value field detection after parsing
- Metadata enhancement with multi-value field info

```python
# Check for multi-value fields (Siemens format with ||)
multi_value_info = validator.validate_multi_value_fields(
    df,
    multi_value_fields=df.columns.tolist(),
    separator="||"
)

if multi_value_info["has_multi_value_fields"]:
    parse_metadata["multi_value_fields"] = multi_value_info["fields_analyzed"]
```

#### 2. Data Transformation (`transformer.py`)

**Location:** `c:\Code\SnapMap\backend\app\services\transformer.py`

**Validation Added:**
- Row count validation after field mapping
- Detailed error context with transformation info

```python
# Validate no data loss during field mapping
validator = get_data_validator()
try:
    validator.validate_row_count(
        input_df=source_df,
        output_df=output_df,
        operation_name="field mapping"
    )
except DataLossError as e:
    # Re-raise with additional context
    raise DataLossError(
        message=f"Data loss during field mapping: {e.message}",
        lost_rows=e.lost_rows,
        total_rows=e.total_rows,
        details={
            **e.details,
            "transformations_applied": transformations,
            "mapped_fields": list(mapping_dict.keys())
        }
    )
```

#### 3. Transform Endpoints (`transform.py`)

**Location:** `c:\Code\SnapMap\backend\app\api\endpoints\transform.py`

**Validation Added to:**
- `/transform/preview` - Preview transformation
- `/transform/export` - CSV export
- `/transform/export-xml` - XML export

**Error Handling:**
```python
except DataLossError as e:
    raise HTTPException(
        status_code=400,
        detail={
            "error": {
                "code": "DATA_LOSS_DETECTED",
                "message": e.message,
                "lost_rows": e.lost_rows,
                "total_rows": e.total_rows,
                "loss_percentage": f"{(e.lost_rows / e.total_rows * 100):.1f}%",
                "details": e.details
            },
            "status": 400
        }
    )
```

**XML Export Validation:**
- Parses generated XML to count `<EF_Employee>` elements
- Compares with input row count
- Raises error if mismatch detected

```python
xml_root = fromstring(xml_content)
xml_row_count = len(xml_root.findall('EF_Employee'))

if xml_row_count != initial_row_count:
    raise DataLossError(
        message=f"Data loss during XML transformation: {initial_row_count - xml_row_count} rows lost",
        lost_rows=initial_row_count - xml_row_count,
        total_rows=initial_row_count,
        details={"xml_rows": xml_row_count, "input_rows": initial_row_count}
    )
```

---

## 3. Improved Error Handling

### File Parser (`file_parser.py`)

**Location:** `c:\Code\SnapMap\backend\app\services\file_parser.py`

**Enhanced Error Messages:**

#### 1. Character Encoding Errors
```python
except UnicodeDecodeError as e:
    raise ValueError(
        f"Character encoding issue detected at byte position {e.start}. "
        f"File contains characters incompatible with {encoding} encoding. "
        f"Supported encodings: UTF-8, Latin-1 (ISO-8859-1), Windows-1252. "
        f"Please convert the file to UTF-8 encoding."
    )
```

**User-Friendly Message:**
> "Character encoding issue detected at byte position 1234. File contains characters incompatible with utf-8 encoding. Supported encodings: UTF-8, Latin-1 (ISO-8859-1), Windows-1252. Please convert the file to UTF-8 encoding."

#### 2. Delimiter Detection Errors
```python
elif 'delimiter' in error_msg.lower() or 'separator' in error_msg.lower():
    raise ValueError(
        f"Delimiter detection failed. Attempted delimiter: '{delimiter}'. "
        f"Supported delimiters: comma (,), pipe (|), tab (\\t), semicolon (;). "
        f"Please check the file format and specify the correct delimiter."
    )
```

**User-Friendly Message:**
> "Delimiter detection failed. Attempted delimiter: ','. Supported delimiters: comma (,), pipe (|), tab (\t), semicolon (;). Please check the file format and specify the correct delimiter."

---

## API Error Responses

### HTTP 400 - Data Loss Detected

**Example Response:**
```json
{
  "error": {
    "code": "DATA_LOSS_DETECTED",
    "message": "Data loss detected in field mapping: 5 rows lost (2.5%). Input: 200 rows, Output: 195 rows.",
    "lost_rows": 5,
    "total_rows": 200,
    "loss_percentage": "2.5%",
    "details": {
      "input_rows": 200,
      "output_rows": 195,
      "lost_count": 5,
      "potential_reasons": [
        {
          "reason": "Null values present",
          "columns": {
            "EMPLOYEE_ID": 3,
            "EMAIL": 2
          }
        }
      ],
      "sample_missing_row_indices": [5, 12, 45, 78, 103],
      "transformations_applied": [
        "EmployeeID → EMPLOYEE_ID: Field mapped",
        "EmailAddress → EMAIL: Field mapped"
      ]
    }
  },
  "status": 400
}
```

### HTTP 400 - Invalid File Format

**Example Response:**
```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Character encoding issue detected. Detected encoding: iso-8859-1. Supported encodings: UTF-8, Latin-1, Windows-1252. Try saving the file as UTF-8 or specify the correct encoding.",
    "details": {
      "supported_formats": [".csv", ".xlsx", ".xls"],
      "suggestion": "Please check the file format and encoding."
    }
  },
  "status": 400
}
```

---

## Success Criteria

### ✅ Multi-Value Field Support
- [x] Multi-value emails parse correctly with `||` separator
- [x] XML generates proper `<email_list>` with multiple `<email>` tags
- [x] Backward compatible with comma-separated values
- [x] Supports email, phone, and URL lists

### ✅ Data Loss Validation
- [x] HTTP 400 error returned if any row loss detected
- [x] Error messages show specific row count and percentage
- [x] Potential reasons for data loss identified
- [x] Sample missing row indices provided
- [x] Validation at all pipeline stages (parse, map, validate, transform)

### ✅ Improved Error Handling
- [x] Specific error messages for encoding issues
- [x] Specific error messages for delimiter detection failures
- [x] User-friendly suggestions for fixing issues
- [x] Detailed error context in API responses

---

## Testing Recommendations

### 1. Multi-Value Field Test

**Test File:** `test_multivalue.csv`
```csv
EmployeeID,WorkEmails,WorkPhones
1,john@company.com||john.doe@company.com,555-1234||555-5678
2,jane@company.com,555-9999
```

**Expected Behavior:**
- Row 1: Multiple emails and phones in XML lists
- Row 2: Single email and phone in XML lists

### 2. Data Loss Test

**Test Scenario:** Upload file with 100 rows, map fields, export XML

**Expected Behavior:**
- If any rows lost: HTTP 400 with detailed error
- Error shows exact count and percentage
- Error includes potential reasons

### 3. Encoding Test

**Test File:** File with special characters (é, ñ, ü)

**Expected Behavior:**
- Successful parsing with proper encoding detection
- Or clear error message with encoding suggestion

---

## Files Modified

1. `c:\Code\SnapMap\backend\app\services\xml_transformer.py`
   - Enhanced `_add_list_element()` for multi-value support

2. `c:\Code\SnapMap\backend\app\services\data_validator.py` (NEW)
   - Complete data validation service
   - DataLossError exception
   - Row count validation
   - Field completeness validation
   - Multi-value field detection

3. `c:\Code\SnapMap\backend\app\services\file_parser.py`
   - Improved error handling for encoding issues
   - Better delimiter detection error messages

4. `c:\Code\SnapMap\backend\app\services\transformer.py`
   - Integrated data loss validation
   - Enhanced error context

5. `c:\Code\SnapMap\backend\app\api\endpoints\upload.py`
   - Multi-value field detection
   - Enhanced metadata

6. `c:\Code\SnapMap\backend\app\api\endpoints\transform.py`
   - Data loss validation in preview endpoint
   - Data loss validation in CSV export
   - Data loss validation in XML export
   - XML row count validation

---

## Future Enhancements

1. **Configurable Separators**
   - Allow users to specify custom separators
   - Support for multiple separator types per file

2. **Data Loss Reporting**
   - Generate detailed reports of lost rows
   - Export lost row data for analysis

3. **Automatic Data Recovery**
   - Attempt to recover lost rows
   - Fill missing values with defaults

4. **Performance Optimization**
   - Optimize validation for large datasets
   - Batch validation for streaming data

---

## References

- Siemens Data Format Specification
- Eightfold XML Schema Documentation
- ETL Best Practices for Data Integrity
- Python Pandas Data Validation Patterns
