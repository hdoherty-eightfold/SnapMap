# SnapMap - HR Data Transformation Tool

> Transform HR data files into Eightfold-compatible formats with semantic field mapping and schema validation.

## What It Does

Upload CSV/Excel files → Auto-map fields → Validate data → Export as CSV or XML → Upload via SFTP

**Core Technology:**
- Semantic field matching using vector embeddings (ChromaDB + Sentence Transformers)
- Schema validation for data quality
- No AI/LLMs - just fast, local vector similarity matching

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

### Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python build_vector_db.py  # One-time setup
python -m uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:5173

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
