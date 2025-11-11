# Upload Feature Specification

## Overview
File upload functionality with support for CSV, XML, and Excel files up to 100MB with automatic delimiter and encoding detection.

## Components
- `frontend/src/components/upload/FileUpload.tsx`
- `backend/app/api/endpoints/upload.py`

## Key Functionality
1. **File Type Detection**: Automatic detection of CSV, pipe-delimited, TSV, Excel formats
2. **Encoding Detection**: UTF-8, UTF-8-BOM, Latin-1, Windows-1252 support
3. **Delimiter Detection**: Auto-detection of pipe (|), comma, tab, semicolon
4. **File Size Validation**: Up to 100MB with optimized memory usage
5. **Preview Generation**: Initial data preview for validation

## API Endpoints
- `POST /upload` - Upload and process file
- `GET /upload/status/{upload_id}` - Check upload status

## Dependencies
- FastAPI for backend processing
- React dropzone for frontend upload
- Pandas for file processing
- CharDet for encoding detection

## Testing
**Location:** `backend/tests/features/upload/`

**Test Files:**
- `test_delimiter_detection.py` - Tests auto-detection of pipe (|), comma, tab, semicolon delimiters
- `test_delimiter_encoding.py` - Tests encoding detection with various delimiters
- `test_character_encoding.py` - Tests UTF-8, UTF-8-BOM, Latin-1, Windows-1252 support

**Test Coverage:**
- File format detection (CSV, TSV, pipe-delimited, Excel)
- Encoding detection accuracy (>95% success rate)
- Delimiter auto-detection (>98% accuracy)
- File size validation (up to 100MB)
- Error handling for corrupted files
- Memory optimization for large files

**Performance Benchmarks:**
- 10MB file: <2 seconds processing
- 50MB file: <10 seconds processing
- 100MB file: <20 seconds processing

## Configuration
- Max file size: 100MB (configurable in `backend/app/core/config.py`)
- Supported formats: CSV, TSV, pipe-delimited, Excel (.xlsx, .xls)

## Error Handling
- File size exceeded
- Unsupported file format
- Corrupted file detection
- Network timeout handling