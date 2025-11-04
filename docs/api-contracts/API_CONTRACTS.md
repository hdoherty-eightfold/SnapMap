# API Contracts Documentation

**Project**: ETL UI - HR Data Transformation Tool
**Version**: 1.0
**Last Updated**: November 2, 2025

## Overview

This document defines all API contracts between Frontend and Backend modules. All developers MUST follow these specifications exactly to ensure seamless integration.

## Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: TBD

## Common Headers

### Request Headers
```
Content-Type: application/json
Accept: application/json
```

### Response Headers
```
Content-Type: application/json
Access-Control-Allow-Origin: *
```

## Error Response Format

All endpoints follow this error format:

```typescript
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
  };
  status: number;
}
```

**Example**:
```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "File must be CSV or Excel format",
    "details": {
      "supported_formats": [".csv", ".xlsx", ".xls"]
    }
  },
  "status": 400
}
```

---

## API Endpoints

### 1. File Upload

**Endpoint**: `POST /api/upload`
**Owner**: Module 3 (Backend - Transformation)
**Consumer**: Module 1 (Frontend - Core UI)

**Purpose**: Upload and parse CSV/Excel file, return preview data

**Request**:
```typescript
// Content-Type: multipart/form-data
interface UploadRequest {
  file: File;  // CSV or Excel file
}
```

**Response**:
```typescript
interface UploadResponse {
  filename: string;
  row_count: number;
  column_count: number;
  columns: string[];
  sample_data: Record<string, any>[];  // First 10 rows
  data_types: Record<string, string>;   // Column name → data type
  file_size: number;                    // Size in bytes
}
```

**Example Response**:
```json
{
  "filename": "workday_export.csv",
  "row_count": 150,
  "column_count": 12,
  "columns": [
    "EmpID", "FirstName", "LastName", "Email",
    "HireDate", "JobTitle", "Department", "Phone",
    "Location", "Manager", "Skill1", "Skill2"
  ],
  "sample_data": [
    {
      "EmpID": "E001",
      "FirstName": "John",
      "LastName": "Doe",
      "Email": "john@company.com",
      "HireDate": "10/30/2020",
      "JobTitle": "Software Engineer",
      "Department": "Engineering",
      "Phone": "+1-555-0100",
      "Location": "San Francisco",
      "Manager": "Jane Smith",
      "Skill1": "Python",
      "Skill2": "JavaScript"
    }
  ],
  "data_types": {
    "EmpID": "string",
    "FirstName": "string",
    "LastName": "string",
    "Email": "email",
    "HireDate": "date",
    "JobTitle": "string",
    "Department": "string",
    "Phone": "string",
    "Location": "string",
    "Manager": "string",
    "Skill1": "string",
    "Skill2": "string"
  },
  "file_size": 52428
}
```

**Error Codes**:
- `400` - Invalid file format
- `413` - File too large (> 100 MB)
- `500` - Error parsing file

---

### 2. Get Schema

**Endpoint**: `GET /api/schema/{entity_name}`
**Owner**: Module 4 (Backend - Schema & Auto-Map)
**Consumer**: Module 1, Module 2 (Frontend)

**Purpose**: Get entity schema definition

**Parameters**:
- `entity_name`: "employee" (for MVP)

**Response**:
```typescript
interface SchemaResponse {
  entity_name: string;
  display_name: string;
  description: string;
  fields: FieldDefinition[];
}

interface FieldDefinition {
  name: string;                    // UPPERCASE field name
  display_name: string;            // Human-readable name
  type: string;                    // "string" | "number" | "date" | "email" | "datetime"
  required: boolean;
  max_length?: number;
  min_length?: number;
  pattern?: string;                // Regex pattern
  format?: string;                 // For date/datetime
  example: string;
  description: string;
  default_value?: any;
}
```

**Example Response**:
```json
{
  "entity_name": "employee",
  "display_name": "Employee",
  "description": "Employee master data",
  "fields": [
    {
      "name": "EMPLOYEE_ID",
      "display_name": "Employee ID",
      "type": "string",
      "required": true,
      "max_length": 50,
      "example": "E001",
      "description": "Unique employee identifier"
    },
    {
      "name": "FIRST_NAME",
      "display_name": "First Name",
      "type": "string",
      "required": true,
      "max_length": 100,
      "example": "John",
      "description": "Employee's first name"
    },
    {
      "name": "EMAIL",
      "display_name": "Email Address",
      "type": "email",
      "required": true,
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
      "example": "john@company.com",
      "description": "Employee's work email"
    },
    {
      "name": "HIRING_DATE",
      "display_name": "Hiring Date",
      "type": "date",
      "required": false,
      "format": "YYYY-MM-DD",
      "example": "2020-10-30",
      "description": "Date employee was hired"
    }
  ]
}
```

**Error Codes**:
- `404` - Entity not found
- `500` - Error loading schema

---

### 3. Auto-Map Fields

**Endpoint**: `POST /api/auto-map`
**Owner**: Module 4 (Backend - Schema & Auto-Map)
**Consumer**: Module 2 (Frontend - Mapping Engine)

**Purpose**: Automatically map source fields to target fields using fuzzy matching

**Request**:
```typescript
interface AutoMapRequest {
  source_fields: string[];          // Customer's field names
  target_schema?: string;           // Default: "employee"
  min_confidence?: number;          // Default: 0.70 (70%)
}
```

**Response**:
```typescript
interface AutoMapResponse {
  mappings: Mapping[];
  total_mapped: number;
  total_source: number;
  total_target: number;
  mapping_percentage: number;       // 0-100
  unmapped_source: string[];
  unmapped_target: string[];
}

interface Mapping {
  source: string;
  target: string;
  confidence: number;               // 0.0 to 1.0
  method: "exact" | "alias" | "fuzzy";
  alternatives?: Alternative[];     // Top 3 alternatives
}

interface Alternative {
  target: string;
  confidence: number;
}
```

**Example Request**:
```json
{
  "source_fields": [
    "EmpID", "FirstName", "LastName", "Email",
    "HireDate", "JobTitle", "Department", "Phone"
  ],
  "target_schema": "employee",
  "min_confidence": 0.70
}
```

**Example Response**:
```json
{
  "mappings": [
    {
      "source": "EmpID",
      "target": "EMPLOYEE_ID",
      "confidence": 0.98,
      "method": "alias",
      "alternatives": [
        { "target": "EMAIL", "confidence": 0.15 }
      ]
    },
    {
      "source": "FirstName",
      "target": "FIRST_NAME",
      "confidence": 0.95,
      "method": "fuzzy",
      "alternatives": []
    },
    {
      "source": "Email",
      "target": "EMAIL",
      "confidence": 1.0,
      "method": "exact",
      "alternatives": []
    }
  ],
  "total_mapped": 8,
  "total_source": 8,
  "total_target": 10,
  "mapping_percentage": 100,
  "unmapped_source": [],
  "unmapped_target": ["LAST_ACTIVITY_TS", "ROLE"]
}
```

**Error Codes**:
- `400` - Invalid request (empty source_fields)
- `404` - Schema not found
- `500` - Error during auto-mapping

---

### 4. Transform Preview

**Endpoint**: `POST /api/transform/preview`
**Owner**: Module 3 (Backend - Transformation)
**Consumer**: Module 2 (Frontend - Mapping Engine)

**Purpose**: Preview transformation with current mappings

**Request**:
```typescript
interface PreviewRequest {
  mappings: Mapping[];
  source_data: Record<string, any>[];  // Sample rows
  sample_size?: number;                // Default: 5
}
```

**Response**:
```typescript
interface PreviewResponse {
  transformed_data: Record<string, any>[];
  transformations_applied: string[];
  row_count: number;
  warnings: string[];
}
```

**Example Request**:
```json
{
  "mappings": [
    { "source": "EmpID", "target": "EMPLOYEE_ID", "confidence": 0.98 },
    { "source": "FirstName", "target": "FIRST_NAME", "confidence": 0.95 },
    { "source": "HireDate", "target": "HIRING_DATE", "confidence": 0.90 }
  ],
  "source_data": [
    {
      "EmpID": "E001",
      "FirstName": "John",
      "HireDate": "10/30/2020"
    }
  ],
  "sample_size": 5
}
```

**Example Response**:
```json
{
  "transformed_data": [
    {
      "EMPLOYEE_ID": "E001",
      "FIRST_NAME": "John",
      "HIRING_DATE": "2020-10-30",
      "LAST_ACTIVITY_TS": "2025-11-02T14:30:00"
    }
  ],
  "transformations_applied": [
    "HireDate (10/30/2020) → HIRING_DATE (2020-10-30) - Date format changed",
    "LAST_ACTIVITY_TS added with current timestamp"
  ],
  "row_count": 1,
  "warnings": []
}
```

**Error Codes**:
- `400` - Invalid mappings or data
- `500` - Error during transformation

---

### 5. Validate Data

**Endpoint**: `POST /api/validate`
**Owner**: Module 3 (Backend - Transformation)
**Consumer**: Module 2 (Frontend - Mapping Engine)

**Purpose**: Validate mappings and data against schema

**Request**:
```typescript
interface ValidationRequest {
  mappings: Mapping[];
  source_data?: Record<string, any>[];
  schema_name?: string;             // Default: "employee"
}
```

**Response**:
```typescript
interface ValidationResponse {
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
  row_number?: number;
  suggestion?: string;
}

interface ValidationSummary {
  total_errors: number;
  total_warnings: number;
  required_fields_mapped: number;
  required_fields_total: number;
  mapping_completeness: number;     // 0-100
}
```

**Example Response**:
```json
{
  "is_valid": false,
  "errors": [
    {
      "field": "LAST_ACTIVITY_TS",
      "message": "Required field not mapped",
      "severity": "error",
      "suggestion": "Use current timestamp or map from source field"
    }
  ],
  "warnings": [
    {
      "field": "TITLE",
      "message": "Optional field not mapped",
      "severity": "warning"
    }
  ],
  "info": [
    {
      "field": "HIRING_DATE",
      "message": "Date format will be converted from MM/DD/YYYY to YYYY-MM-DD",
      "severity": "info"
    }
  ],
  "summary": {
    "total_errors": 1,
    "total_warnings": 1,
    "required_fields_mapped": 9,
    "required_fields_total": 10,
    "mapping_completeness": 90
  }
}
```

**Error Codes**:
- `400` - Invalid request
- `500` - Error during validation

---

### 6. Export CSV

**Endpoint**: `POST /api/transform/export`
**Owner**: Module 3 (Backend - Transformation)
**Consumer**: Module 1 (Frontend - Core UI)

**Purpose**: Generate and download final transformed CSV

**Request**:
```typescript
interface ExportRequest {
  mappings: Mapping[];
  source_data: Record<string, any>[];
  output_filename?: string;         // Default: "EMPLOYEE-MAIN.csv"
}
```

**Response**:
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="EMPLOYEE-MAIN.csv"

<CSV file content>
```

**Example Request**:
```json
{
  "mappings": [
    { "source": "EmpID", "target": "EMPLOYEE_ID", "confidence": 0.98 },
    { "source": "FirstName", "target": "FIRST_NAME", "confidence": 0.95 }
  ],
  "source_data": [
    { "EmpID": "E001", "FirstName": "John" }
  ],
  "output_filename": "EMPLOYEE-MAIN.csv"
}
```

**Example Response** (CSV content):
```csv
EMPLOYEE_ID,FIRST_NAME,LAST_NAME,EMAIL,HIRING_DATE,LAST_ACTIVITY_TS
E001,John,,,,"2025-11-02T14:30:00"
```

**Error Codes**:
- `400` - Invalid mappings or data
- `500` - Error generating CSV

---

### 7. Get Validation Rules

**Endpoint**: `GET /api/validation-rules/{entity_name}`
**Owner**: Module 4 (Backend - Schema & Auto-Map)
**Consumer**: Module 3 (Backend - Transformation)

**Purpose**: Get validation rules for entity

**Response**:
```typescript
interface ValidationRulesResponse {
  entity_name: string;
  rules: Record<string, FieldRule>;
}

interface FieldRule {
  required: boolean;
  type: string;
  pattern?: string;
  min_length?: number;
  max_length?: number;
  format?: string;
  custom_validators?: string[];
}
```

**Example Response**:
```json
{
  "entity_name": "employee",
  "rules": {
    "EMPLOYEE_ID": {
      "required": true,
      "type": "string",
      "pattern": "^[A-Z0-9]+$",
      "max_length": 50
    },
    "EMAIL": {
      "required": true,
      "type": "email",
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    },
    "HIRING_DATE": {
      "required": false,
      "type": "date",
      "format": "%Y-%m-%d"
    }
  }
}
```

---

## Type Definitions

### TypeScript (Frontend)

```typescript
// types/api.ts

// Common types
export type DataType = "string" | "number" | "date" | "email" | "datetime" | "boolean";
export type MatchMethod = "exact" | "alias" | "fuzzy";
export type Severity = "error" | "warning" | "info";

// Field Definition
export interface FieldDefinition {
  name: string;
  display_name: string;
  type: DataType;
  required: boolean;
  max_length?: number;
  min_length?: number;
  pattern?: string;
  format?: string;
  example: string;
  description: string;
  default_value?: any;
}

// Mapping
export interface Mapping {
  source: string;
  target: string;
  confidence: number;
  method: MatchMethod;
  alternatives?: Alternative[];
}

export interface Alternative {
  target: string;
  confidence: number;
}

// Schema
export interface EntitySchema {
  entity_name: string;
  display_name: string;
  description: string;
  fields: FieldDefinition[];
}

// Validation
export interface ValidationMessage {
  field: string;
  message: string;
  severity: Severity;
  row_number?: number;
  suggestion?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  errors: ValidationMessage[];
  warnings: ValidationMessage[];
  info: ValidationMessage[];
  summary: ValidationSummary;
}

export interface ValidationSummary {
  total_errors: number;
  total_warnings: number;
  required_fields_mapped: number;
  required_fields_total: number;
  mapping_completeness: number;
}

// Upload
export interface UploadResponse {
  filename: string;
  row_count: number;
  column_count: number;
  columns: string[];
  sample_data: Record<string, any>[];
  data_types: Record<string, string>;
  file_size: number;
}

// Auto-map
export interface AutoMapRequest {
  source_fields: string[];
  target_schema?: string;
  min_confidence?: number;
}

export interface AutoMapResponse {
  mappings: Mapping[];
  total_mapped: number;
  total_source: number;
  total_target: number;
  mapping_percentage: number;
  unmapped_source: string[];
  unmapped_target: string[];
}

// Transform
export interface PreviewRequest {
  mappings: Mapping[];
  source_data: Record<string, any>[];
  sample_size?: number;
}

export interface PreviewResponse {
  transformed_data: Record<string, any>[];
  transformations_applied: string[];
  row_count: number;
  warnings: string[];
}

// Export
export interface ExportRequest {
  mappings: Mapping[];
  source_data: Record<string, any>[];
  output_filename?: string;
}
```

### Python (Backend)

```python
# app/models/api.py

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Common types
DataType = Literal["string", "number", "date", "email", "datetime", "boolean"]
MatchMethod = Literal["exact", "alias", "fuzzy"]
Severity = Literal["error", "warning", "info"]

# Field Definition
class FieldDefinition(BaseModel):
    name: str
    display_name: str
    type: DataType
    required: bool
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None
    format: Optional[str] = None
    example: str
    description: str
    default_value: Optional[Any] = None

# Mapping
class Alternative(BaseModel):
    target: str
    confidence: float

class Mapping(BaseModel):
    source: str
    target: str
    confidence: float
    method: MatchMethod
    alternatives: Optional[List[Alternative]] = None

# Schema
class EntitySchema(BaseModel):
    entity_name: str
    display_name: str
    description: str
    fields: List[FieldDefinition]

# Validation
class ValidationMessage(BaseModel):
    field: str
    message: str
    severity: Severity
    row_number: Optional[int] = None
    suggestion: Optional[str] = None

class ValidationSummary(BaseModel):
    total_errors: int
    total_warnings: int
    required_fields_mapped: int
    required_fields_total: int
    mapping_completeness: float

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationMessage]
    warnings: List[ValidationMessage]
    info: List[ValidationMessage]
    summary: ValidationSummary

# Upload
class UploadResponse(BaseModel):
    filename: str
    row_count: int
    column_count: int
    columns: List[str]
    sample_data: List[Dict[str, Any]]
    data_types: Dict[str, str]
    file_size: int

# Auto-map
class AutoMapRequest(BaseModel):
    source_fields: List[str]
    target_schema: Optional[str] = "employee"
    min_confidence: Optional[float] = 0.70

class AutoMapResponse(BaseModel):
    mappings: List[Mapping]
    total_mapped: int
    total_source: int
    total_target: int
    mapping_percentage: float
    unmapped_source: List[str]
    unmapped_target: List[str]

# Transform
class PreviewRequest(BaseModel):
    mappings: List[Mapping]
    source_data: List[Dict[str, Any]]
    sample_size: Optional[int] = 5

class PreviewResponse(BaseModel):
    transformed_data: List[Dict[str, Any]]
    transformations_applied: List[str]
    row_count: int
    warnings: List[str]

# Export
class ExportRequest(BaseModel):
    mappings: List[Mapping]
    source_data: List[Dict[str, Any]]
    output_filename: Optional[str] = "EMPLOYEE-MAIN.csv"
```

---

## Testing Checklist

### Integration Testing

Before declaring integration complete, test these scenarios:

#### 1. Upload Flow
- [ ] Upload CSV file successfully
- [ ] Upload Excel file successfully
- [ ] Handle invalid file format (should return 400)
- [ ] Handle file too large (should return 413)
- [ ] Response matches UploadResponse format
- [ ] Sample data contains 10 rows or less

#### 2. Auto-Map Flow
- [ ] Auto-map with common field names (80%+ accuracy)
- [ ] Auto-map with exact matches (100% confidence)
- [ ] Auto-map with aliases (95%+ confidence)
- [ ] Auto-map with fuzzy matches (70-94% confidence)
- [ ] Response includes alternatives
- [ ] No duplicate mappings

#### 3. Validation Flow
- [ ] Detect required fields not mapped
- [ ] Detect optional fields not mapped
- [ ] Validate email format
- [ ] Validate date format
- [ ] Summary counts are correct

#### 4. Transform Flow
- [ ] Preview shows correct transformations
- [ ] Date format conversion works
- [ ] Required fields are populated
- [ ] Transform log is clear

#### 5. Export Flow
- [ ] CSV file downloads successfully
- [ ] Filename is correct
- [ ] CSV format is valid
- [ ] UTF-8 encoding works
- [ ] Column headers are uppercase

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-02 | 1.0 | Initial API contracts | Team |

---

## Questions or Issues?

If you find any issues with these API contracts or need clarification:

1. **Add comment** directly in this document
2. **Raise in daily standup**
3. **Update this document** and notify all team members
4. **Version changes** - increment version number

---

**⚠️ IMPORTANT**: All changes to API contracts MUST be communicated to all team members immediately!
