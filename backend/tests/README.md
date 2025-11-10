# SnapMap Test Suite

Comprehensive automated tests for all SnapMap data transformation fixes.

## Overview

This test suite validates:
- ✓ Delimiter auto-detection (comma, pipe, tab, semicolon)
- ✓ Field mapping accuracy (>=70% for Siemens files)
- ✓ Character encoding preservation (Turkish, Spanish, German, French)
- ✓ Multi-value field handling (|| separator)
- ✓ Data loss validation (1213 rows in → 1213 rows out)
- ✓ End-to-end integration

## Quick Start

### Run All Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Run Specific Test Module
```bash
# Delimiter detection
python -m pytest tests/test_delimiter_detection.py -v

# Field mapping
python -m pytest tests/test_field_mapping_accuracy.py -v

# Character encoding
python -m pytest tests/test_character_encoding.py -v

# Multi-value fields
python -m pytest tests/test_multi_value_fields.py -v

# Data validation
python -m pytest tests/test_data_loss_validation.py -v

# End-to-end
python -m pytest tests/test_siemens_end_to_end.py -v
```

### Run with Coverage
```bash
# Requires: pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

## Test Statistics

- **Total Tests:** 117
- **Pass Rate:** 79% (92 passed, 11 failed, 14 skipped)
- **Execution Time:** ~54 seconds
- **Coverage:** ~85%

## Test Modules

### 1. test_delimiter_detection.py (14 tests)
Tests automatic delimiter detection for various CSV formats.

**Key Tests:**
- Comma-delimited CSV (standard)
- Pipe-delimited CSV (Siemens format)
- Tab-delimited TSV
- Semicolon-delimited CSV
- Quoted strings with delimiters
- Multi-value field detection
- Special character detection

### 2. test_field_mapping_accuracy.py (11 tests)
Tests semantic field mapping with >=70% accuracy target.

**Key Tests:**
- Siemens file mapping threshold (>=70%)
- PersonID → CANDIDATE_ID mapping
- WorkEmails → EMAIL mapping
- WorkPhones → PHONE mapping
- Confidence scores >= 0.80
- Case-insensitive matching
- Batch mapping performance

**Note:** Requires vector embeddings. Run `python build_vector_db.py` first.

### 3. test_character_encoding.py (12 tests)
Tests international character preservation throughout the pipeline.

**Key Tests:**
- Turkish: Türkiye, Kayır, İstanbul
- Spanish: Torreón, García, Señor
- German: München, Größe
- French: Français, Élève
- End-to-end: CSV → Parse → Transform → XML

### 4. test_multi_value_fields.py (15 tests)
Tests handling of fields with || separator.

**Key Tests:**
- Parse "email1@test.com||email2@test.com"
- Generate XML with <email_list><email>...</email></email_list>
- Test with 2, 3, 5+ values
- Empty values handling
- Special characters in values
- Comma-separated fallback

### 5. test_data_loss_validation.py (15 tests)
Tests data integrity throughout the ETL pipeline.

**Key Tests:**
- 1213 row file → 1213 rows preserved
- Data loss detection
- HTTP 400 if rows lost
- Error message shows specific row numbers
- Null value detection
- Duplicate detection

### 6. test_siemens_end_to_end.py (15 tests)
Complete integration test with actual Siemens candidate file.

**Test Steps:**
1. Upload test_siemens_candidates.csv
2. Auto-detect pipe delimiter
3. Map fields (expect 70%+)
4. Validate data
5. Transform to XML
6. Verify XML validity
7. Check character encoding
8. Confirm 1213 records in → 1213 out

## Test Fixtures

Located in `conftest.py`:

- `sample_csv_comma_delimited` - Standard CSV
- `sample_csv_pipe_delimited` - Siemens format
- `sample_csv_with_special_chars` - International characters
- `sample_dataframe_simple` - Basic DataFrame
- `sample_dataframe_multi_value` - Multi-value fields
- `sample_dataframe_special_chars` - UTF-8 characters
- `sample_field_mappings` - Field mapping configs
- `siemens_field_names` - Common Siemens fields

## Test Markers

Use markers to run specific test groups:

```bash
# Skip slow tests
pytest tests/ -v -m "not slow"

# Run only integration tests
pytest tests/ -v -m "integration"

# Skip tests requiring Siemens file
pytest tests/ -v -m "not requires_siemens_file"
```

## Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
addopts = -v --strict-markers --tb=short
markers =
    integration: Integration tests
    slow: Slow running tests
    requires_siemens_file: Tests requiring actual Siemens file
```

## Troubleshooting

### Failed Tests: Field Mapping

**Issue:** Semantic matching tests fail with low confidence scores.

**Solution:**
```bash
cd backend
python build_vector_db.py
```

This rebuilds embeddings for all entity schemas.

### Skipped Tests: End-to-End

**Issue:** Siemens end-to-end tests are skipped.

**Solution:** Ensure `test_siemens_candidates.csv` exists at:
```
backend/test_siemens_candidates.csv
```

### Import Errors

**Issue:** `ModuleNotFoundError` when running tests.

**Solution:** Run from backend directory:
```bash
cd backend
python -m pytest tests/ -v
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Build embeddings
        run: |
          cd backend
          python build_vector_db.py
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --tb=short
```

## Contributing

When adding new tests:

1. **Use descriptive test names**
   ```python
   def test_turkish_characters_preserved_in_xml():
   ```

2. **Include docstrings**
   ```python
   def test_something():
       """Test that X does Y when Z happens"""
   ```

3. **Follow AAA pattern**
   - Arrange: Setup test data
   - Act: Execute operation
   - Assert: Verify results

4. **Use fixtures for common data**
   ```python
   def test_something(sample_csv_comma_delimited):
       df, metadata = parser.parse_file(sample_csv_comma_delimited, "test.csv")
   ```

## Test Results

Full test report available at: `IMPLEMENTATION_TEST_REPORT.md`

## License

Part of the SnapMap project.
