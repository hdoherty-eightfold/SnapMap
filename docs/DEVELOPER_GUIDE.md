# SnapMap Developer Guide

**Version:** 2.0.0
**Last Updated:** November 7, 2025

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Key Components](#key-components)
4. [Data Flow](#data-flow)
5. [Core Services](#core-services)
6. [API Endpoints](#api-endpoints)
7. [Database & Storage](#database--storage)
8. [Extension Points](#extension-points)
9. [Development Workflow](#development-workflow)
10. [Code Examples](#code-examples)
11. [Testing](#testing)
12. [Debugging](#debugging)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Upload  │  │ Mapping  │  │Validation│  │  Export/SFTP │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────┴───────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    API Layer                                │ │
│  │  /upload  /auto-map  /validate  /transform  /sftp          │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│  ┌────────────────────────┴───────────────────────────────────┐ │
│  │                 Business Logic Layer                        │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │  File    │  │  Field   │  │Validator │  │Transform │  │ │
│  │  │  Parser  │  │  Mapper  │  │          │  │  Engine  │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│  ┌────────────────────────┴───────────────────────────────────┐ │
│  │                    Data Layer                               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Vector   │  │  File    │  │ Schema   │  │  SFTP    │  │ │
│  │  │   DB     │  │ Storage  │  │ Manager  │  │ Manager  │  │ │
│  │  │(ChromaDB)│  │(In-Mem)  │  │  (JSON)  │  │(Encrypt) │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend
- **FastAPI**: Modern async web framework for building APIs
- **Pydantic**: Data validation using Python type hints
- **Pandas**: Data manipulation and transformation
- **ChromaDB**: Vector database for semantic search
- **Sentence Transformers**: Neural embeddings for text similarity
- **Uvicorn**: ASGI server for production deployment

#### Frontend
- **React 18**: UI framework with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls

#### Storage & Data
- **ChromaDB**: Pre-computed vector embeddings
- **In-Memory**: Temporary file storage (session-based)
- **JSON Files**: Schema definitions and aliases
- **Encrypted Storage**: SFTP credentials (AES-256)

---

## Project Structure

```
SnapMap/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── endpoints/
│   │   │       ├── upload.py          # File upload endpoint
│   │   │       ├── automapping.py     # Auto-mapping endpoint
│   │   │       ├── validate.py        # Validation endpoint
│   │   │       ├── transform.py       # Export endpoints
│   │   │       ├── sftp.py            # SFTP endpoints
│   │   │       ├── schema.py          # Schema endpoints
│   │   │       ├── ai_inference.py    # AI services (future)
│   │   │       ├── config.py          # Configuration
│   │   │       └── review.py          # Review workflows
│   │   ├── services/
│   │   │   ├── file_parser.py         # CSV/Excel parsing
│   │   │   ├── field_mapper.py        # Semantic field mapping
│   │   │   ├── semantic_matcher.py    # Vector similarity matching
│   │   │   ├── data_validator.py      # Data quality validation
│   │   │   ├── transformer.py         # Data transformation
│   │   │   ├── xml_transformer.py     # XML generation
│   │   │   ├── sftp_manager.py        # SFTP operations
│   │   │   ├── vector_db.py           # ChromaDB wrapper
│   │   │   ├── schema_manager.py      # Schema loading
│   │   │   └── file_storage.py        # In-memory file cache
│   │   ├── models/
│   │   │   ├── upload.py              # Upload request/response
│   │   │   ├── mapping.py             # Mapping request/response
│   │   │   ├── transform.py           # Transform request/response
│   │   │   ├── validation.py          # Validation models
│   │   │   ├── sftp.py                # SFTP models
│   │   │   └── schema.py              # Schema models
│   │   ├── schemas/
│   │   │   ├── employee.json          # Employee entity schema
│   │   │   ├── candidate.json         # Candidate entity schema
│   │   │   ├── user.json              # User entity schema
│   │   │   └── field_aliases.json     # Field name synonyms
│   │   ├── middleware/
│   │   │   ├── security_headers.py    # Security headers
│   │   │   └── rate_limiter.py        # Rate limiting
│   │   ├── utils/
│   │   │   ├── encryption.py          # AES encryption
│   │   │   └── sanitization.py        # Input sanitization
│   │   └── core/
│   │       └── config.py              # App configuration
│   ├── tests/
│   │   ├── test_delimiter_detection.py
│   │   ├── test_character_encoding.py
│   │   ├── test_field_mapping_accuracy.py
│   │   ├── test_multi_value_fields.py
│   │   ├── test_data_loss_validation.py
│   │   └── conftest.py                # Pytest configuration
│   ├── main.py                        # FastAPI app entry point
│   ├── build_vector_db.py             # Vector DB builder
│   ├── requirements.txt               # Python dependencies
│   └── pytest.ini                     # Pytest configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── upload/
│   │   │   │   └── FileUpload.tsx     # File upload component
│   │   │   ├── mapping/
│   │   │   │   ├── FieldMapping.tsx   # Field mapping UI
│   │   │   │   └── ConnectionLines.tsx # Visual connections
│   │   │   ├── validation/
│   │   │   │   └── IssueReview.tsx    # Error display
│   │   │   ├── export/
│   │   │   │   ├── PreviewCSV.tsx     # CSV preview
│   │   │   │   └── PreviewXML.tsx     # XML preview
│   │   │   ├── sftp/
│   │   │   │   ├── SFTPCredentialManager.tsx
│   │   │   │   ├── SFTPUploadPage.tsx
│   │   │   │   └── SFTPExplorer.tsx
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       ├── Card.tsx
│   │   │       └── LoadingSpinner.tsx
│   │   ├── services/
│   │   │   └── api.ts                 # API client
│   │   ├── contexts/
│   │   │   ├── AppContext.tsx         # Global state
│   │   │   ├── ThemeContext.tsx       # Theme provider
│   │   │   └── ToastContext.tsx       # Notifications
│   │   ├── App.tsx                    # Main app component
│   │   └── main.tsx                   # Entry point
│   ├── package.json                   # Node dependencies
│   ├── vite.config.ts                 # Vite configuration
│   └── tsconfig.json                  # TypeScript config
└── docs/
    ├── IMPLEMENTATION_COMPLETE.md
    ├── USER_GUIDE.md
    ├── DEVELOPER_GUIDE.md (this file)
    ├── API_REFERENCE.md
    ├── DEPLOYMENT_GUIDE.md
    └── ...
```

---

## Key Components

### 1. File Parser (`file_parser.py`)

**Purpose**: Parse CSV, TSV, pipe-delimited, and Excel files with automatic delimiter and encoding detection.

**Key Features**:
- Delimiter auto-detection (`,`, `|`, `\t`, `;`)
- Character encoding detection (UTF-8, Latin-1, Windows-1252)
- Multi-value field detection (`||` separator)
- Excel file support (`.xlsx`, `.xls`)

**Core Method**:
```python
def parse_file(self, file_content: bytes, filename: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Parse file and return DataFrame + metadata

    Returns:
        (DataFrame, {
            "detected_delimiter": "|",
            "detected_encoding": "utf-8",
            "multi_value_fields": ["WORK EMAILS", "WORK PHONES"]
        })
    """
```

**Algorithm**:
1. Detect file type by extension (`.csv`, `.xlsx`, `.xls`)
2. For CSV:
   - Try UTF-8 decoding, fallback to chardet
   - Use `csv.Sniffer` to detect delimiter
   - Replace `||` with placeholder to avoid false detection
   - Parse with pandas
   - Restore `||` in data
3. For Excel:
   - Use `pd.read_excel()` directly
4. Detect multi-value fields by scanning for `||`

**Edge Cases Handled**:
- Single column files (no delimiter)
- Empty files
- Quoted strings with embedded delimiters
- Mixed encodings (rare but handled)
- Malformed CSV (graceful degradation)

---

### 2. Field Mapper (`field_mapper.py`)

**Purpose**: Automatically map source fields to target schema fields using semantic similarity.

**Key Features**:
- Multi-stage matching (alias → semantic → fuzzy)
- Confidence scoring (0-100%)
- Alternative suggestions
- Case-insensitive matching

**Core Method**:
```python
def auto_map(
    self,
    source_fields: List[str],
    target_schema: EntitySchema,
    min_confidence: float = 0.70
) -> List[Mapping]:
    """
    Auto-map source fields to target schema

    Returns:
        [
            Mapping(source="PERSON ID", target="CANDIDATE_ID", confidence=0.92),
            Mapping(source="WORK EMAILS", target="EMAIL", confidence=0.88),
            ...
        ]
    """
```

**Matching Algorithm**:

**Stage 1: Alias/Exact Matching (85-100% confidence)**
```python
# Check alias dictionary
aliases = {
    "CANDIDATE_ID": ["PERSON_ID", "EMP_ID", "EMPLOYEE_ID", "WORKER_ID"],
    "EMAIL": ["WORK_EMAIL", "EMAIL_ADDRESS", "WORK_EMAILS"],
    ...
}
if source_field.upper() in aliases[target_field]:
    confidence = 0.95  # High confidence
```

**Stage 2: Semantic Matching (70-85% confidence)**
```python
# Use vector embeddings for semantic similarity
embedding_source = model.encode(source_field)
embedding_target = model.encode(target_field)
similarity = cosine_similarity(embedding_source, embedding_target)
confidence = similarity  # 0.0 to 1.0
```

**Stage 3: Fuzzy Matching (70-84% confidence)**
```python
# String similarity as fallback
from difflib import SequenceMatcher
ratio = SequenceMatcher(None, source_field.lower(), target_field.lower()).ratio()
confidence = ratio  # 0.0 to 1.0
```

**Why Multi-Stage?**
- **Alias matching**: Fastest, most accurate for known patterns
- **Semantic matching**: Handles synonyms and variations (e.g., "employee" ≈ "worker")
- **Fuzzy matching**: Catches typos and abbreviations

---

### 3. Semantic Matcher (`semantic_matcher.py`)

**Purpose**: Vector-based semantic similarity using pre-computed embeddings.

**Key Features**:
- Uses sentence-transformers model (`all-MiniLM-L6-v2`)
- ChromaDB for efficient similarity search
- Pre-computed embeddings for instant matching

**Core Method**:
```python
def find_best_matches(
    self,
    source_field: str,
    target_fields: List[str],
    top_k: int = 3
) -> List[Tuple[str, float]]:
    """
    Find best matching target fields using semantic similarity

    Returns:
        [("CANDIDATE_ID", 0.92), ("EMPLOYEE_ID", 0.87), ("USER_ID", 0.65)]
    """
```

**How It Works**:
1. **Build Phase** (one-time, via `build_vector_db.py`):
   ```python
   # Generate embeddings for all schema fields
   field_names = ["CANDIDATE_ID", "FIRST_NAME", "EMAIL", ...]
   embeddings = model.encode(field_names)

   # Store in ChromaDB
   collection.add(
       documents=field_names,
       embeddings=embeddings,
       ids=[f"field_{i}" for i in range(len(field_names))]
   )
   ```

2. **Query Phase** (real-time):
   ```python
   # Generate embedding for source field
   query_embedding = model.encode(["PERSON ID"])

   # Query ChromaDB for nearest neighbors
   results = collection.query(
       query_embeddings=query_embedding,
       n_results=3
   )
   # Returns: [("CANDIDATE_ID", 0.92), ...]
   ```

**Performance**:
- **Build time**: ~30 seconds (one-time)
- **Query time**: <1ms per field (instant)
- **Memory**: ~50MB (vector database)

---

### 4. Data Validator (`data_validator.py`)

**Purpose**: Validate data quality and prevent data loss.

**Key Features**:
- Row count validation (no data loss)
- Required field validation
- Format validation (email, date, phone)
- Multi-value field validation
- Duplicate detection

**Core Methods**:
```python
def validate_row_count(
    self,
    input_df: pd.DataFrame,
    output_df: pd.DataFrame,
    allow_deduplication: bool = False
) -> None:
    """
    Validate no rows were lost during transformation

    Raises:
        DataLossError: If rows were lost
    """
    input_count = len(input_df)
    output_count = len(output_df)

    if output_count < input_count and not allow_deduplication:
        lost_rows = input_count - output_count
        raise DataLossError(
            message=f"Data loss detected: {lost_rows} rows missing",
            lost_rows=lost_rows,
            total_rows=input_count,
            details={
                "missing_rows": list(set(input_df.index) - set(output_df.index))
            }
        )

def validate_field_completeness(
    self,
    df: pd.DataFrame,
    required_fields: List[str]
) -> Dict:
    """
    Check percentage of populated fields

    Returns:
        {
            "completeness_percentage": 87.5,
            "null_counts": {"FIRST_NAME": 0, "EMAIL": 42},
            "missing_required": ["EMAIL"]
        }
    """
```

**Validation Rules**:
- **Row Count**: Input rows == Output rows (strict)
- **Required Fields**: No null values in required fields
- **Email Format**: Regex `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Date Format**: ISO 8601 or common formats (YYYY-MM-DD, MM/DD/YYYY)
- **Phone Format**: Flexible (international formats supported)

---

### 5. XML Transformer (`xml_transformer.py`)

**Purpose**: Transform CSV data to Eightfold XML format.

**Key Features**:
- EF_Employee_List structure
- Nested elements for multi-value fields
- Date formatting
- Pretty-printed output

**Core Method**:
```python
def transform_csv_to_xml(
    self,
    df: pd.DataFrame,
    mappings: List[Dict],
    entity_name: str = "employee"
) -> str:
    """
    Transform DataFrame to XML

    Returns:
        Pretty-printed XML string
    """
```

**XML Structure**:
```xml
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
    <phone_list>
      <phone>+1-555-0100</phone>
    </phone_list>
  </employee>
</EF_Employee_List>
```

**Multi-Value Handling**:
```python
# Input: "john@co.com||jane@co.com"
# Split by ||
emails = value.split("||")

# Create nested elements
email_list = SubElement(employee, "email_list")
for email in emails:
    email_elem = SubElement(email_list, "email")
    email_elem.text = email.strip()
```

---

### 6. SFTP Manager (`sftp_manager.py`)

**Purpose**: Manage SFTP credentials and file uploads.

**Key Features**:
- Encrypted credential storage
- Connection testing
- File upload with progress
- Error handling

**Core Methods**:
```python
def add_credential(
    self,
    name: str,
    host: str,
    port: int,
    username: str,
    password: str,
    remote_path: str = "/"
) -> SFTPCredential:
    """
    Add encrypted SFTP credential
    """

def upload_file(
    self,
    credential_id: str,
    local_path: str,
    remote_filename: str = None
) -> UploadResult:
    """
    Upload file to SFTP server
    """
```

**Security**:
- Passwords encrypted with AES-256 (Fernet)
- Encryption key from environment variable
- Credentials stored in JSON with encrypted password field

---

## Data Flow

### Complete Workflow

```
┌────────────┐
│  1. UPLOAD │
└─────┬──────┘
      │ POST /api/upload (file: multipart/form-data)
      ↓
┌─────────────────────────────────────────────┐
│ FileParser.parse_file()                     │
│  - Detect delimiter (|, comma, tab, etc.)   │
│  - Detect encoding (UTF-8, Latin-1, CP1252) │
│  - Parse with pandas                        │
│  - Detect multi-value fields (||)           │
└─────┬───────────────────────────────────────┘
      │ Returns: DataFrame + metadata
      ↓
┌─────────────────────────────────────────────┐
│ FileStorage.store_dataframe()               │
│  - Generate file_id                         │
│  - Store in memory (session cache)          │
└─────┬───────────────────────────────────────┘
      │ Returns: file_id
      ↓
┌────────────┐
│  2. MAPPING│
└─────┬──────┘
      │ POST /api/auto-map (file_id, target_schema)
      ↓
┌─────────────────────────────────────────────┐
│ FieldMapper.auto_map()                      │
│  - Stage 1: Alias matching                  │
│  - Stage 2: Semantic matching (ChromaDB)    │
│  - Stage 3: Fuzzy matching (difflib)        │
└─────┬───────────────────────────────────────┘
      │ Returns: List[Mapping]
      ↓
┌─────────────────────────────────────────────┐
│ Frontend: User reviews/adjusts mappings     │
│  - Drag-and-drop to override               │
│  - View confidence scores                   │
└─────┬───────────────────────────────────────┘
      │
      ↓
┌────────────┐
│ 3. VALIDATE│
└─────┬──────┘
      │ POST /api/validate (file_id, mappings)
      ↓
┌─────────────────────────────────────────────┐
│ DataValidator.validate_row_count()          │
│ DataValidator.validate_field_completeness() │
│ DataValidator.validate_multi_value_fields() │
└─────┬───────────────────────────────────────┘
      │ Returns: Validation report or errors
      ↓
┌────────────┐
│ 4. EXPORT  │
└─────┬──────┘
      │ POST /api/transform/export (CSV)
      │ POST /api/transform/export-xml (XML)
      ↓
┌─────────────────────────────────────────────┐
│ Transformer.transform_data() (CSV)          │
│   OR                                        │
│ XMLTransformer.transform_csv_to_xml() (XML) │
└─────┬───────────────────────────────────────┘
      │ Returns: File download
      ↓
┌────────────┐
│ 5. SFTP    │
└─────┬──────┘
      │ POST /api/sftp/upload/{credential_id}
      ↓
┌─────────────────────────────────────────────┐
│ SFTPManager.upload_file()                   │
│  - Decrypt credentials                      │
│  - Connect to SFTP server                   │
│  - Upload file                              │
└─────┬───────────────────────────────────────┘
      │ Returns: Upload confirmation
      ↓
    [DONE]
```

---

## Core Services

### File Parser Service

**Location**: `backend/app/services/file_parser.py`

**Responsibilities**:
- Parse CSV, TSV, pipe-delimited, Excel files
- Auto-detect delimiter and encoding
- Handle special characters (Turkish, Spanish, German, French)
- Detect multi-value fields (`||` separator)

**Key Methods**:

```python
class FileParser:
    def parse_file(self, file_content: bytes, filename: str) -> Tuple[pd.DataFrame, Dict]:
        """Main parsing method"""

    def detect_file_format(self, file_content: bytes, filename: str) -> Dict:
        """Detect format without full parsing"""

    def detect_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer data types for each column"""
```

**Usage Example**:
```python
from app.services.file_parser import get_file_parser

parser = get_file_parser()
df, metadata = parser.parse_file(file_bytes, "employees.csv")

print(metadata)
# {
#     "detected_delimiter": "|",
#     "detected_encoding": "utf-8",
#     "multi_value_fields": ["WORK EMAILS"]
# }
```

---

### Field Mapper Service

**Location**: `backend/app/services/field_mapper.py`

**Responsibilities**:
- Auto-map source fields to target schema
- Calculate confidence scores
- Provide alternative matches
- Handle edge cases (abbreviations, typos, synonyms)

**Key Methods**:

```python
class FieldMapper:
    def auto_map(
        self,
        source_fields: List[str],
        target_schema: EntitySchema,
        min_confidence: float = 0.70
    ) -> List[Mapping]:
        """Auto-map with confidence threshold"""

    def get_best_match(
        self,
        source_field: str,
        target_fields: List[FieldDefinition],
        used_targets: Set[str]
    ) -> Optional[Mapping]:
        """Get best match for single field"""
```

**Usage Example**:
```python
from app.services.field_mapper import get_field_mapper
from app.services.schema_manager import get_schema_manager

mapper = get_field_mapper()
schema_manager = get_schema_manager()

schema = schema_manager.get_schema("employee")
source_fields = ["PERSON ID", "WORK EMAILS", "FULL NAME"]

mappings = mapper.auto_map(source_fields, schema, min_confidence=0.70)

for m in mappings:
    print(f"{m.source} → {m.target} ({m.confidence:.0%})")
# PERSON ID → CANDIDATE_ID (92%)
# WORK EMAILS → EMAIL (88%)
# FULL NAME → DISPLAY_NAME (85%)
```

---

### Data Validator Service

**Location**: `backend/app/services/data_validator.py`

**Responsibilities**:
- Validate row counts (prevent data loss)
- Check required fields
- Validate formats (email, date, phone)
- Detect duplicates

**Key Methods**:

```python
class DataValidator:
    def validate_row_count(
        self,
        input_df: pd.DataFrame,
        output_df: pd.DataFrame,
        allow_deduplication: bool = False
    ) -> None:
        """Raise DataLossError if rows lost"""

    def validate_field_completeness(
        self,
        df: pd.DataFrame,
        required_fields: List[str]
    ) -> Dict:
        """Check field population percentages"""

    def validate_multi_value_fields(
        self,
        df: pd.DataFrame,
        multi_value_fields: List[str],
        separator: str = "||"
    ) -> Dict:
        """Detect and validate multi-value fields"""
```

**Usage Example**:
```python
from app.services.data_validator import get_data_validator, DataLossError

validator = get_data_validator()

try:
    validator.validate_row_count(input_df, output_df)
    print("✓ No data loss")
except DataLossError as e:
    print(f"✗ Data loss: {e.lost_rows} rows missing")
    print(f"  Details: {e.details}")
```

---

## API Endpoints

See `API_REFERENCE.md` for complete API documentation. Here's a summary:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Upload and parse file |
| POST | `/api/detect-file-format` | Detect format without parsing |
| POST | `/api/auto-map` | Auto-map fields |
| POST | `/api/validate` | Validate data |
| POST | `/api/transform/export` | Export as CSV |
| POST | `/api/transform/export-xml` | Export as XML |
| GET | `/api/entities` | List entity types |
| GET | `/api/schema/{entity_name}` | Get entity schema |
| POST | `/api/sftp/credentials` | Create SFTP credential |
| GET | `/api/sftp/credentials` | List SFTP credentials |
| POST | `/api/sftp/upload/{credential_id}` | Upload file via SFTP |

---

## Database & Storage

### Vector Database (ChromaDB)

**Purpose**: Store pre-computed embeddings for semantic field matching.

**Location**: `backend/chroma_db/` (created by `build_vector_db.py`)

**Schema**:
```python
collection = chromadb.Collection("field_embeddings")
# Documents: Field names (e.g., "CANDIDATE_ID", "FIRST_NAME")
# Embeddings: 384-dim vectors from sentence-transformers
# Metadata: {"entity": "employee", "field_type": "string"}
```

**Build Command**:
```bash
cd backend
python build_vector_db.py
```

**Build Process**:
1. Load all schema definitions (`app/schemas/*.json`)
2. Extract all field names
3. Generate embeddings using `all-MiniLM-L6-v2` model
4. Store in ChromaDB collection
5. Verify with test queries

**Performance**:
- Build time: ~30 seconds
- Query time: <1ms per field
- Storage: ~50MB

---

### In-Memory File Storage

**Purpose**: Temporary storage of uploaded DataFrames.

**Location**: `backend/app/services/file_storage.py`

**Implementation**:
```python
class FileStorage:
    def __init__(self):
        self._storage: Dict[str, Tuple[pd.DataFrame, str, datetime]] = {}

    def store_dataframe(self, df: pd.DataFrame, filename: str) -> str:
        """Store DataFrame and return file_id"""
        file_id = self._generate_file_id()
        self._storage[file_id] = (df, filename, datetime.now())
        return file_id

    def retrieve_dataframe(self, file_id: str) -> Optional[pd.DataFrame]:
        """Retrieve DataFrame by file_id"""
```

**Expiration**: Files are cleared after 1 hour of inactivity or on server restart.

---

### Schema Storage

**Purpose**: Define target entity schemas (Employee, Candidate, User).

**Location**: `backend/app/schemas/*.json`

**Schema Format**:
```json
{
  "entity_name": "employee",
  "version": "1.0",
  "fields": [
    {
      "name": "CANDIDATE_ID",
      "type": "string",
      "required": true,
      "description": "Unique employee identifier"
    },
    {
      "name": "FIRST_NAME",
      "type": "string",
      "required": true,
      "description": "Employee first name"
    },
    ...
  ]
}
```

**Field Types**:
- `string`: Text data
- `email`: Email address (validated)
- `date`: Date in ISO 8601 format
- `integer`: Numeric (whole numbers)
- `float`: Numeric (decimals)
- `boolean`: True/False

---

## Extension Points

### Adding a New Entity Type

**Example**: Add "Contractor" entity

**Step 1: Create Schema**

Create `backend/app/schemas/contractor.json`:
```json
{
  "entity_name": "contractor",
  "version": "1.0",
  "fields": [
    {
      "name": "CONTRACTOR_ID",
      "type": "string",
      "required": true,
      "description": "Unique contractor identifier"
    },
    {
      "name": "COMPANY_NAME",
      "type": "string",
      "required": true,
      "description": "Contracting company"
    },
    ...
  ]
}
```

**Step 2: Rebuild Vector Database**
```bash
cd backend
python build_vector_db.py
```

**Step 3: Update Frontend**

Add "Contractor" to entity dropdown in `frontend/src/components/mapping/EntitySelector.tsx`.

**Done!** The new entity is automatically available in the API.

---

### Adding Custom Field Aliases

**Example**: Add aliases for "BADGE_NUMBER" field

Edit `backend/app/schemas/field_aliases.json`:
```json
{
  "EMPLOYEE_ID": ["EMP_ID", "PERSON_ID", "WORKER_ID", "BADGE_NUMBER"],
  ...
}
```

**Rebuild Vector Database**:
```bash
cd backend
python build_vector_db.py
```

Now "BADGE_NUMBER" will automatically map to "EMPLOYEE_ID" with high confidence.

---

### Adding Custom Validation Rules

**Example**: Validate that employee ID is numeric

Edit `backend/app/services/data_validator.py`:

```python
def validate_employee_id_format(self, df: pd.DataFrame) -> List[Dict]:
    """Validate EMPLOYEE_ID is numeric"""
    errors = []

    if "EMPLOYEE_ID" in df.columns:
        non_numeric = df[~df["EMPLOYEE_ID"].astype(str).str.isnumeric()]

        for idx, row in non_numeric.iterrows():
            errors.append({
                "row": idx + 2,  # +2 for header + 0-index
                "field": "EMPLOYEE_ID",
                "value": row["EMPLOYEE_ID"],
                "error": "EMPLOYEE_ID must be numeric"
            })

    return errors
```

Call this method in the validation endpoint.

---

## Development Workflow

### Local Development Setup

**1. Clone Repository**
```bash
git clone https://github.com/your-org/snapmap.git
cd snapmap
```

**2. Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build vector database (REQUIRED!)
python build_vector_db.py

# Run server
python -m uvicorn main:app --reload --port 8000
```

**3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

**4. Access Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

### Making Code Changes

**Backend Changes**:
1. Edit code in `backend/app/`
2. Server auto-reloads (if using `--reload`)
3. Test endpoint in Swagger UI (http://localhost:8000/api/docs)
4. Write unit test in `backend/tests/`
5. Run tests: `pytest tests/`

**Frontend Changes**:
1. Edit code in `frontend/src/`
2. Vite auto-reloads browser
3. Test in browser
4. Check console for errors (F12)

**Schema Changes**:
1. Edit schema in `backend/app/schemas/*.json`
2. Rebuild vector DB: `python build_vector_db.py`
3. Restart backend server

---

### Running Tests

**Backend Tests**:
```bash
cd backend

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_delimiter_detection.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

**Frontend Tests** (if configured):
```bash
cd frontend
npm run test
```

---

### Debugging

**Backend Debugging**:

**Method 1: Print Statements**
```python
print(f"DEBUG: df shape = {df.shape}")
print(f"DEBUG: columns = {df.columns.tolist()}")
```

**Method 2: Logging**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing file: {filename}")
logger.info(f"Detected delimiter: {delimiter}")
logger.warning(f"Low confidence mapping: {source} → {target}")
logger.error(f"Failed to parse file: {error}")
```

**Method 3: VS Code Debugger**

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

Set breakpoints and press F5 to start debugging.

**Frontend Debugging**:

**Method 1: Browser Console**
```typescript
console.log('DEBUG: file uploaded', file);
console.error('ERROR: API call failed', error);
```

**Method 2: React DevTools**
- Install React DevTools extension
- Inspect component state and props
- View component tree

**Method 3: Network Tab**
- Open DevTools (F12)
- Go to "Network" tab
- Filter by "Fetch/XHR"
- Inspect API requests/responses

---

## Code Examples

### Example 1: Upload and Parse File

**Backend** (`upload.py`):
```python
@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    # Read file
    content = await file.read()

    # Parse file
    parser = get_file_parser()
    df, metadata = parser.parse_file(content, file.filename)

    # Store in memory
    storage = get_file_storage()
    file_id = storage.store_dataframe(df, file.filename)

    return UploadResponse(
        file_id=file_id,
        row_count=len(df),
        columns=df.columns.tolist(),
        detected_delimiter=metadata["detected_delimiter"],
        detected_encoding=metadata["detected_encoding"]
    )
```

**Frontend** (`FileUpload.tsx`):
```typescript
const handleFileUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post('/api/upload', formData);
    setFileId(response.data.file_id);
    setColumns(response.data.columns);
    console.log(`Uploaded: ${file.name} (${response.data.row_count} rows)`);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

---

### Example 2: Auto-Map Fields

**Backend** (`automapping.py`):
```python
@router.post("/auto-map", response_model=AutoMapResponse)
async def auto_map_fields(request: AutoMapRequest):
    # Get schema
    schema_manager = get_schema_manager()
    schema = schema_manager.get_schema(request.target_schema)

    # Perform auto-mapping
    mapper = get_field_mapper()
    mappings = mapper.auto_map(
        request.source_fields,
        schema,
        request.min_confidence
    )

    return AutoMapResponse(
        mappings=mappings,
        mapped_count=len(mappings),
        mapping_percentage=(len(mappings) / len(request.source_fields)) * 100
    )
```

**Frontend** (`FieldMapping.tsx`):
```typescript
const handleAutoMap = async () => {
  try {
    const response = await axios.post('/api/auto-map', {
      file_id: fileId,
      target_schema: 'employee',
      min_confidence: 0.70
    });

    setMappings(response.data.mappings);
    console.log(`Auto-mapped ${response.data.mapped_count} fields`);
  } catch (error) {
    console.error('Auto-mapping failed:', error);
  }
};
```

---

### Example 3: Export as XML

**Backend** (`transform.py`):
```python
@router.post("/transform/export-xml")
async def export_xml(request: ExportRequest):
    # Retrieve DataFrame
    storage = get_file_storage()
    df = storage.retrieve_dataframe(request.file_id)

    # Transform to XML
    xml_transformer = get_xml_transformer()
    xml_str = xml_transformer.transform_csv_to_xml(
        df,
        request.mappings,
        request.entity_name
    )

    # Return as download
    return Response(
        content=xml_str,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={request.entity_name}.xml"
        }
    )
```

**Frontend** (`PreviewXML.tsx`):
```typescript
const handleExportXML = async () => {
  try {
    const response = await axios.post('/api/transform/export-xml', {
      file_id: fileId,
      mappings: mappings,
      entity_name: 'employee'
    }, {
      responseType: 'blob'
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'employee.xml');
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Export failed:', error);
  }
};
```

---

## Testing

See `TESTING_GUIDE.md` for comprehensive testing documentation.

**Quick Reference**:

```bash
# Run all tests
pytest tests/

# Run specific module
pytest tests/test_delimiter_detection.py

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_delimiter_detection.py::TestDelimiterDetection::test_pipe_delimiter
```

---

## Debugging

### Common Issues

**1. "Module not found" errors**
- **Cause**: Not in correct directory or virtual environment not activated
- **Fix**: `cd backend && source venv/bin/activate`

**2. "Vector DB not found" errors**
- **Cause**: Forgot to build vector database
- **Fix**: `python build_vector_db.py`

**3. CORS errors in frontend**
- **Cause**: Backend not running or CORS not configured
- **Fix**: Check backend is running on port 8000, verify CORS origins in `main.py`

**4. "File not found" errors in API**
- **Cause**: file_id expired or wrong file_id
- **Fix**: Re-upload file to get new file_id

---

## Best Practices

### Code Style

**Python**:
- Follow PEP 8 style guide
- Use type hints for all function parameters and return types
- Write docstrings for all public methods
- Use `black` for auto-formatting: `black app/`

**TypeScript**:
- Use functional components with hooks
- Define interfaces for all data structures
- Use meaningful variable names
- Follow React best practices

### Performance

**1. Use batch operations**
```python
# Good: Vectorized operation
df['EMAIL_CLEAN'] = df['EMAIL'].str.lower().str.strip()

# Bad: Row-by-row operation
for idx, row in df.iterrows():
    df.loc[idx, 'EMAIL_CLEAN'] = row['EMAIL'].lower().strip()
```

**2. Avoid unnecessary copies**
```python
# Good: Modify in place
df.drop_duplicates(inplace=True)

# Bad: Create copy
df = df.drop_duplicates()
```

**3. Stream large files**
```python
# Good: Stream response
def stream_csv():
    for chunk in df_chunks:
        yield chunk.to_csv()

return StreamingResponse(stream_csv(), media_type="text/csv")

# Bad: Load entire file in memory
csv_str = df.to_csv()
return Response(csv_str, media_type="text/csv")
```

### Security

**1. Validate all inputs**
```python
from pydantic import BaseModel, validator

class UploadRequest(BaseModel):
    filename: str

    @validator('filename')
    def validate_filename(cls, v):
        if not v.endswith(('.csv', '.xlsx', '.xls')):
            raise ValueError("Invalid file type")
        return v
```

**2. Sanitize user data**
```python
from app.utils.sanitization import sanitize_string

user_input = sanitize_string(user_input)
```

**3. Use environment variables for secrets**
```python
import os
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
```

---

## Contributing

### Contribution Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and write tests
4. Run tests: `pytest tests/`
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Security considerations addressed

---

## Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pandas**: https://pandas.pydata.org/docs/
- **ChromaDB**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/
- **React**: https://react.dev/

### Internal Docs
- `USER_GUIDE.md`: End-user documentation
- `API_REFERENCE.md`: Complete API specifications
- `DEPLOYMENT_GUIDE.md`: Production deployment
- `TROUBLESHOOTING_GUIDE.md`: Common issues and solutions

---

*Developer Guide Version: 2.0.0*
*Last Updated: November 7, 2025*
*Author: SnapMap Development Team*
