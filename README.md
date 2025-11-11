# SnapMap - HR Data Transformation Tool

> Transform HR data files into Eightfold-compatible formats with semantic field mapping and schema validation.

## What It Does

Upload CSV/Excel files → Auto-map fields → Validate data → Export as CSV or XML → Upload via SFTP

**Core Technology:**
- Semantic field matching using vector embeddings (ChromaDB + Sentence Transformers)
- Schema validation for data quality
- No AI/LLMs - just fast, local vector similarity matching

## 📁 Project Structure

### Feature-Based Architecture
```
.claude/features/          # Feature specifications and agents
├── MAIN_ORCHESTRATOR.md   # Main coordination agent
├── upload/SPEC.md         # File upload feature
├── review/SPEC.md         # Data quality analysis
├── mapping/SPEC.md        # AI-powered field mapping
├── export/SPEC.md         # Multi-format export
├── sftp/SPEC.md          # Secure file upload
├── settings/SPEC.md       # App configuration
└── layout/SPEC.md         # UI navigation framework
```

### Development Guidelines
- **Each feature has its own SPEC.md** defining functionality, APIs, and dependencies
- **Main Orchestrator** coordinates feature interactions and prevents breaking changes
- **Isolated testing** per feature with integration test coverage
- **Safe updates** following change management protocol

---

## Features

### 1. File Upload
- CSV and Excel (.csv, .xlsx, .xls) support
- Drag-and-drop interface
- Instant preview

### 2. Semantic Field Mapping
- Automatic field matching using vector embeddings
- Manual drag-and-drop mapping for corrections
- Confidence scoring for each mapping

### 3. Schema Validation
- Required field checking
- Data type validation (email, date, numeric)
- Format validation
- Row-level error reporting

### 4. Dual Export
- **CSV Export**: Transformed data in Eightfold format
- **XML Export**: EF_Employee_List XML structure with nested elements (email_list, phone_list, etc.)

### 5. SFTP Upload
- Store SFTP credentials
- Upload exported files directly to SFTP server

---

## Tech Stack

**Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
**Backend:** FastAPI (Python 3.11+)
**Vector DB:** ChromaDB with Sentence Transformers
**Processing:** Pandas + Pydantic

---

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+

### Setup Instructions

**1. Backend Setup:**
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# CRITICAL: Build vector database (required for semantic matching)
# This creates the ChromaDB vector database - takes ~30 seconds
python build_vector_db.py

# Start backend server
python -m uvicorn main:app --reload --port 8000
```

**2. Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Start frontend server
npm run dev
```

**3. Access Application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Common Setup Issues

**500 Error when uploading files:**
- ❌ Forgot to run `python build_vector_db.py`
- ✅ Run it in the `backend/` folder before starting the server

**Import errors in Python:**
- ❌ Wrong directory or virtual environment not activated
- ✅ Make sure you're in `backend/` folder when running pip install

**Port already in use:**
- Change port: `uvicorn main:app --port 8001`

---

## Project Structure

```
SnapMap/
├── frontend/              # React frontend
│   └── src/
│       ├── components/    # UI components
│       ├── services/      # API client
│       └── contexts/      # State management
├── backend/               # FastAPI backend
│   └── app/
│       ├── api/endpoints/ # API routes
│       ├── services/      # Business logic
│       └── schemas/       # Entity schemas (JSON)
└── docs/                  # Documentation
```

---

## How It Works

### Semantic Mapping
Uses pre-computed vector embeddings to match field names by meaning:
- "emp_id" → "EMPLOYEE_ID" (0.92 similarity)
- "worker_num" → "EMPLOYEE_ID" (0.87 similarity)
- Runs locally, <1ms per field

### Validation
Rule-based validation checks:
- Missing required fields
- Invalid data formats
- Data quality issues

---

## API Documentation

See [docs/api-contracts/API_CONTRACTS.md](docs/api-contracts/API_CONTRACTS.md) for complete API specifications.

**Key Endpoints:**
- `POST /api/upload` - Upload file
- `POST /api/auto-map` - Auto-map fields
- `POST /api/transform/export` - Export CSV
- `POST /api/transform/export-xml` - Export XML
- `POST /api/sftp/upload/{id}` - Upload via SFTP

---

## Testing

```bash
# Backend tests
cd backend
python test_xml_functionality.py

# Frontend
cd frontend
npm run test
```

---

## License

MIT
