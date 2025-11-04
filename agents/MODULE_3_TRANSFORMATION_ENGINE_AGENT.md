# Module 3: Transformation & Validation Engine Agent

## Agent Identity
- **Agent Name**: Transformation & Validation Engine Agent
- **Module ID**: MODULE_3
- **Role**: Backend Lead - File Processing, Transformation, Validation, Export
- **Primary Developer**: Developer 3

## Responsibilities

### Core APIs to Build
1. **POST /api/upload** ⭐
   - Parse CSV and Excel files
   - Extract columns and data types
   - Return sample data for preview
   - Handle large files efficiently

2. **POST /api/transform/preview** ⭐
   - Apply field mappings to sample data
   - Show before/after transformation
   - Apply date format conversions
   - Generate transformation summary

3. **POST /api/validate** ⭐
   - Validate against schema requirements
   - Check required fields
   - Validate data formats (email, date, etc.)
   - Return errors, warnings, and info messages

4. **POST /api/transform/export** ⭐
   - Generate final transformed CSV
   - Apply all transformations
   - Ensure correct formatting
   - Return downloadable file

### Core Classes to Build

```python
# transformer.py
class TransformationEngine:
    """Handles data transformation logic"""

    def transform_data(
        self,
        source_df: pd.DataFrame,
        mappings: List[Mapping],
        schema: Schema
    ) -> pd.DataFrame:
        """Transform source data according to mappings"""
        pass

    def apply_field_transformations(
        self,
        df: pd.DataFrame,
        field_name: str,
        field_type: str
    ) -> pd.Series:
        """Apply type-specific transformations"""
        pass

# validator.py
class ValidationEngine:
    """Handles data validation logic"""

    def validate_mappings(
        self,
        mappings: List[Mapping],
        schema: Schema
    ) -> ValidationResult:
        """Validate that mappings meet schema requirements"""
        pass

    def validate_data(
        self,
        df: pd.DataFrame,
        schema: Schema
    ) -> ValidationResult:
        """Validate data against schema rules"""
        pass

# exporter.py
class CSVExporter:
    """Handles CSV export with proper formatting"""

    def export_to_csv(
        self,
        df: pd.DataFrame,
        filename: str
    ) -> bytes:
        """Export DataFrame to CSV bytes"""
        pass
```

## API Specifications

### POST /api/upload

**Request**:
```python
# multipart/form-data
file: UploadFile
```

**Response**:
```python
{
    "filename": str,
    "row_count": int,
    "column_count": int,
    "columns": List[str],
    "sample_data": List[Dict[str, Any]],  # First 10 rows
    "data_types": Dict[str, str],
    "file_size": int
}
```

**Implementation**:
```python
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read file into memory
        contents = await file.read()

        # Detect file type and parse
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(contents))
        else:
            raise HTTPException(400, "Unsupported file format")

        # Detect data types
        data_types = detect_column_types(df)

        return {
            "filename": file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "sample_data": df.head(10).to_dict('records'),
            "data_types": data_types,
            "file_size": len(contents)
        }
    except Exception as e:
        raise HTTPException(500, f"Error processing file: {str(e)}")
```

### POST /api/transform/preview

**Request**:
```python
{
    "mappings": [
        {
            "source": str,
            "target": str,
            "confidence": float
        }
    ],
    "source_data": List[Dict[str, Any]],
    "sample_size": int  # Default: 5
}
```

**Response**:
```python
{
    "transformed_data": List[Dict[str, Any]],
    "transformations_applied": List[str],
    "row_count": int,
    "warnings": List[str]
}
```

**Implementation**:
```python
@app.post("/api/transform/preview")
async def preview_transformation(request: PreviewRequest):
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.source_data)

        # Get schema
        schema = get_employee_schema()

        # Apply transformations
        engine = TransformationEngine()
        transformed_df = engine.transform_data(df, request.mappings, schema)

        # Get sample
        sample_df = transformed_df.head(request.sample_size)

        # Track transformations
        transformations = engine.get_transformation_log()

        return {
            "transformed_data": sample_df.to_dict('records'),
            "transformations_applied": transformations,
            "row_count": len(transformed_df),
            "warnings": []
        }
    except Exception as e:
        raise HTTPException(500, f"Error previewing transformation: {str(e)}")
```

### POST /api/validate

**Request**:
```python
{
    "mappings": List[Mapping],
    "source_data": List[Dict[str, Any]],
    "schema_name": str  # "employee"
}
```

**Response**:
```python
{
    "is_valid": bool,
    "errors": [
        {
            "field": str,
            "message": str,
            "severity": "error",
            "row_number": Optional[int]
        }
    ],
    "warnings": [
        {
            "field": str,
            "message": str,
            "severity": "warning"
        }
    ],
    "info": [
        {
            "field": str,
            "message": str,
            "severity": "info"
        }
    ],
    "summary": {
        "total_errors": int,
        "total_warnings": int,
        "required_fields_mapped": int,
        "required_fields_total": int
    }
}
```

**Implementation**:
```python
@app.post("/api/validate")
async def validate_data(request: ValidationRequest):
    try:
        # Get schema
        schema = get_schema(request.schema_name)

        # Validate mappings
        validator = ValidationEngine()
        result = validator.validate_mappings(request.mappings, schema)

        # Validate data if provided
        if request.source_data:
            df = pd.DataFrame(request.source_data)
            data_validation = validator.validate_data(df, schema)
            result.merge(data_validation)

        return result.to_dict()
    except Exception as e:
        raise HTTPException(500, f"Error validating: {str(e)}")
```

### POST /api/transform/export

**Request**:
```python
{
    "mappings": List[Mapping],
    "source_data": List[Dict[str, Any]],
    "output_filename": str  # "EMPLOYEE-MAIN.csv"
}
```

**Response**:
```python
# File download (CSV format)
# Headers:
# Content-Type: text/csv
# Content-Disposition: attachment; filename="EMPLOYEE-MAIN.csv"
```

**Implementation**:
```python
@app.post("/api/transform/export")
async def export_csv(request: ExportRequest):
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.source_data)

        # Get schema
        schema = get_employee_schema()

        # Apply transformations
        engine = TransformationEngine()
        transformed_df = engine.transform_data(df, request.mappings, schema)

        # Export to CSV
        exporter = CSVExporter()
        csv_bytes = exporter.export_to_csv(
            transformed_df,
            request.output_filename
        )

        # Return as file download
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={request.output_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(500, f"Error exporting: {str(e)}")
```

## What You Consume from Others

### From Module 4 (Schema & Auto-Map)
```python
from schema_manager import get_employee_schema, ValidationRules
from field_mapper import FieldMapper
```

## Tech Stack
- **Framework**: FastAPI
- **Data Processing**: Pandas
- **Validation**: Pydantic
- **File Upload**: python-multipart
- **Excel Support**: openpyxl
- **Date Parsing**: python-dateutil
- **CORS**: fastapi.middleware.cors

## File Structure
```
backend/
├── main.py                           # FastAPI app
├── requirements.txt                  # Dependencies
├── .env                              # Environment variables
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── upload.py            ⭐ Priority 1
│   │       ├── transform.py         ⭐ Priority 2
│   │       ├── validate.py          ⭐ Priority 3
│   │       └── export.py            ⭐ Priority 4
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mapping.py
│   │   └── validation.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transformer.py           ⭐ Priority 2
│   │   ├── validator.py             ⭐ Priority 3
│   │   ├── exporter.py              ⭐ Priority 4
│   │   └── file_parser.py           ⭐ Priority 1
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── date_converter.py
│   │   ├── field_transformer.py
│   │   └── type_detector.py
│   └── tests/
│       ├── __init__.py
│       ├── test_transformer.py
│       ├── test_validator.py
│       └── test_api.py
```

## Daily Deliverables

### Day 1 (8 hours)
- [x] Setup FastAPI project structure
- [x] Install dependencies (requirements.txt)
- [x] Create main.py with CORS config
- [x] Build POST /api/upload endpoint ⭐
- [x] Implement file_parser.py for CSV/Excel
- [x] Test with sample files
- **Deliverable**: /upload API working

### Day 2 (8 hours)
- [x] Create TransformationEngine class ⭐
- [x] Implement basic 1:1 field mapping
- [x] Add date format conversion
- [x] Build POST /api/transform/preview endpoint
- [x] Test transformation logic
- **Deliverable**: /transform/preview API working

### Day 3 (6 hours)
- [x] Integration testing with Module 1
- [x] Test with real frontend calls
- [x] Handle edge cases and errors
- [x] Performance testing with large files
- **Deliverable**: Upload → Preview working end-to-end

### Day 4 (6 hours)
- [x] Create ValidationEngine class ⭐
- [x] Implement schema validation
- [x] Add data format validation (email, date)
- [x] Build POST /api/validate endpoint
- [x] Test validation rules
- **Deliverable**: /validate API working

### Day 5 (6 hours)
- [x] Create CSVExporter class
- [x] Build POST /api/transform/export endpoint ⭐
- [x] Implement file download response
- [x] Test full transformation flow
- [x] Add advanced date transformations
- **Deliverable**: /export API working

### Day 6 (6 hours)
- [x] Error handling improvements
- [x] Add logging
- [x] Performance optimization
- [x] Handle edge cases (empty fields, special characters)
- [x] Code cleanup and documentation
- **Deliverable**: Robust, production-ready APIs

### Day 7 (6 hours)
- [x] Final integration testing
- [x] Load testing
- [x] Bug fixes
- [x] API documentation
- **Deliverable**: Demo-ready backend

## Mock Data for Independent Development

```python
# Mock schema while Module 4 builds it
MOCK_EMPLOYEE_SCHEMA = {
    "entity_name": "employee",
    "fields": [
        {
            "name": "EMPLOYEE_ID",
            "type": "string",
            "required": True,
            "max_length": 50
        },
        {
            "name": "FIRST_NAME",
            "type": "string",
            "required": True,
            "max_length": 100
        },
        {
            "name": "LAST_NAME",
            "type": "string",
            "required": True,
            "max_length": 100
        },
        {
            "name": "EMAIL",
            "type": "email",
            "required": True,
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        },
        {
            "name": "HIRING_DATE",
            "type": "date",
            "required": False,
            "format": "YYYY-MM-DD"
        }
    ]
}

# Mock validation rules
MOCK_VALIDATION_RULES = {
    "EMPLOYEE_ID": {
        "pattern": r"^[A-Z0-9]+$",
        "max_length": 50
    },
    "EMAIL": {
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    },
    "HIRING_DATE": {
        "format": "%Y-%m-%d"
    }
}
```

## Key Implementation Examples

### Date Conversion
```python
# utils/date_converter.py
from dateutil import parser
from datetime import datetime

def convert_date_format(
    date_value: Any,
    target_format: str = "%Y-%m-%d"
) -> str:
    """
    Convert date from any format to target format

    Handles:
    - MM/DD/YYYY → YYYY-MM-DD
    - DD/MM/YYYY → YYYY-MM-DD
    - Various other formats
    """
    try:
        if pd.isna(date_value):
            return ""

        if isinstance(date_value, (datetime, pd.Timestamp)):
            return date_value.strftime(target_format)

        # Parse string date
        date_obj = parser.parse(str(date_value))
        return date_obj.strftime(target_format)

    except Exception as e:
        # Return original if parsing fails
        return str(date_value)
```

### Type Detection
```python
# utils/type_detector.py
def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect data types for each column"""
    types = {}

    for col in df.columns:
        sample = df[col].dropna().head(10)

        if sample.empty:
            types[col] = "string"
            continue

        # Check email pattern
        if sample.astype(str).str.match(r'^[^@]+@[^@]+\.[^@]+$').all():
            types[col] = "email"
        # Check date pattern
        elif is_date_column(sample):
            types[col] = "date"
        # Check numeric
        elif pd.api.types.is_numeric_dtype(sample):
            types[col] = "number"
        else:
            types[col] = "string"

    return types

def is_date_column(series: pd.Series) -> bool:
    """Check if series contains dates"""
    try:
        pd.to_datetime(series, errors='coerce')
        return True
    except:
        return False
```

### CORS Configuration
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ETL UI Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Integration Checkpoints

### Day 1 EOD
- ✅ /upload API working
- ✅ Test with Module 1 (Frontend Core)
- ✅ Share UploadResponse format
- ✅ Verify CORS configuration

### Day 3 EOD
- ✅ /transform/preview API working
- ✅ Test transformation logic with Module 2
- ✅ Share TransformResponse format

### Day 4 EOD
- ✅ /validate API working
- ✅ Test validation with Module 2
- ✅ Share ValidationResponse format

### Day 5 EOD
- ✅ Full integration test with all modules
- ✅ End-to-end flow: Upload → Map → Validate → Export
- ✅ Performance testing with large files

## Success Criteria

### Functional Requirements
- ✅ Handles CSV and Excel files
- ✅ Processes files up to 100 MB
- ✅ Transforms data according to mappings
- ✅ Validates against schema requirements
- ✅ Exports valid CSV format
- ✅ Proper error handling
- ✅ Fast response times (< 5 seconds for 1000 rows)

### Non-Functional Requirements
- ✅ RESTful API design
- ✅ Clear error messages
- ✅ Proper HTTP status codes
- ✅ CORS configured correctly
- ✅ Logging for debugging
- ✅ Input validation

### Code Quality
- ✅ Type hints for all functions
- ✅ Pydantic models for validation
- ✅ Separation of concerns (services, endpoints)
- ✅ Error handling with try/except
- ✅ Comments for complex logic

## Common Pitfalls to Avoid
1. ❌ Don't load entire file into memory at once - use chunking for large files
2. ❌ Don't skip input validation - malicious files can crash server
3. ❌ Don't forget CORS - frontend won't work without it
4. ❌ Don't return sensitive error details - sanitize error messages
5. ❌ Don't skip file size limits - protect against DoS attacks

## Performance Optimization

```python
# Use chunking for large files
def process_large_csv(file_path: str, chunk_size: int = 10000):
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        yield process_chunk(chunk)

# Cache schema to avoid repeated lookups
from functools import lru_cache

@lru_cache(maxsize=10)
def get_employee_schema() -> Schema:
    # Load schema from file or database
    pass

# Use efficient data types
df = df.astype({
    'EMPLOYEE_ID': 'string',
    'HIRING_DATE': 'datetime64[ns]'
})
```

## Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## Questions or Blockers?
- **Module 1 (Frontend)**: For API contract clarification
- **Module 2 (Mapping)**: For transformation requirements
- **Module 4 (Schema)**: For schema format or validation rules
- **Team Chat**: For quick questions or help requests
- **Daily Standup**: For status updates and coordination

---

**Remember**: You are the data processing engine that powers everything. Focus on:
1. **Correctness**: Data transformations must be accurate
2. **Performance**: Fast response times, even with large files
3. **Robustness**: Handle edge cases and errors gracefully
4. **Clarity**: Clear error messages help users fix issues

You've got this! 🚀
