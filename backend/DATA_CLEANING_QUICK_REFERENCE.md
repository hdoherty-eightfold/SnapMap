# Data Cleaning Quick Reference Guide

## Quick Commands

### 1. Analyze File (No Changes)
```bash
python siemens_data_cleaner.py "path/to/file.csv" --analyze-only
```

### 2. Clean File (Default Output)
```bash
python siemens_data_cleaner.py "path/to/file.csv"
# Creates: file_cleaned.csv
```

### 3. Clean with Custom Output
```bash
python siemens_data_cleaner.py "path/to/file.csv" --output "cleaned_file.csv"
```

### 4. Full Analysis with Report
```bash
python siemens_data_cleaner.py "path/to/file.csv" \
  --output "cleaned.csv" \
  --report "quality_report.json"
```

---

## Common Data Issues & Fixes

### Issue 1: Custom Delimiters in Fields

**BEFORE:**
```
'' Home street: %123 Main St% , Home city: %Boston%, Home zip code: %02101% ''
```

**AFTER:**
```
street=123 Main St; city=Boston; zip=02101
```

**Fix Applied:** Parse custom format and convert to semicolon-separated key-value pairs

---

### Issue 2: Quote Artifacts

**BEFORE:**
```
''Some text here''
```

**AFTER:**
```
Some text here
```

**Fix Applied:** Remove double single quotes

---

### Issue 3: Phone Number Leading Quotes

**BEFORE:**
```
'+1 555-123-4567
'+44 20 1234 5678
```

**AFTER:**
```
+1 555-123-4567
+44 20 1234 5678
```

**Fix Applied:** Strip leading single quotes

---

### Issue 4: Multiline Fields

**BEFORE:**
```
Line 1
Line 2
Line 3
```

**AFTER:**
```
Line 1 Line 2 Line 3
```

**Fix Applied:** Replace newlines with spaces, normalize multiple spaces

---

### Issue 5: Special Characters

**BEFORE:**
```
"Smart quotes" and — dashes
```

**AFTER:**
```
"Straight quotes" and - dashes
```

**Fix Applied:** Normalize Unicode characters to ASCII equivalents where safe

---

## Interpreting the Analysis Report

### Sample Output Explanation

```
DATA QUALITY ANALYSIS REPORT
================================================================================

File Statistics:
  Total Rows: 1,169          ← Number of data records
  Total Fields: 22           ← Number of columns

Issues Detected:
  Encoding Issues:
    - Extended ASCII: 622     ← Latin characters (á, é, ü, etc.)
    - High Unicode: 293       ← Chinese, Arabic, Turkish special chars
  Quote Issues: 1,114         ← Double single quotes found
  Custom Delimiter: 1,114     ← Percentage sign delimiters
  Phone Format: 52            ← Leading quote on phone numbers
  Multiline: 7                ← Fields with newlines

Top 10 Empty Fields:         ← Fields with high empty rates
  WorkPhones: 1,163 (99.5%)  ← Normal for candidate data
  ...
```

### What Empty Fields Mean

- **High empty rates (>80%) are NORMAL** for candidate databases
- External candidates often don't provide:
  - Work contact information
  - Current work emails
  - Availability dates
- **No action needed** for empty fields

---

## Testing Cleaned Data

### 1. Quick Parse Test (Python)
```python
import csv

with open('cleaned_file.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    row_count = 0
    for row in reader:
        row_count += 1
        # Should complete without errors
    print(f"Successfully parsed {row_count} rows")
```

### 2. Verify Row Count
```bash
# Count lines in both files
wc -l original.csv cleaned.csv

# Should be close (cleaned may have fewer if multiline issues were fixed)
```

### 3. Spot Check Data
```python
import csv

with open('cleaned_file.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    for i, row in enumerate(reader):
        if i < 5:  # Check first 5 rows
            print(f"\nRow {i+1}:")
            print(f"  Name: {row['FirstName']} {row['LastName']}")
            print(f"  Email: {row['HomeEmails']}")
            print(f"  Location: {row['HomeLocation'][:80]}...")
```

---

## Common Issues & Solutions

### Problem: Script fails with encoding error

**Solution:**
```bash
# Ensure file is UTF-8 encoded
file -i your_file.csv

# If not UTF-8, convert first:
iconv -f ISO-8859-1 -t UTF-8 input.csv > input_utf8.csv
```

### Problem: Wrong delimiter detected

**Solution:**
```bash
# Specify delimiter explicitly
python siemens_data_cleaner.py file.csv --delimiter ","
```

### Problem: Want to preserve original format

**Solution:**
```bash
# Use --analyze-only to see what would change
python siemens_data_cleaner.py file.csv --analyze-only

# Review the report before cleaning
```

---

## Understanding the Quality Report (JSON)

### Sample quality_report.json Structure

```json
{
  "total_rows": 1169,
  "total_fields": 22,
  "issues": {
    "encoding_issues": 2,        ← Types of encoding issues
    "quote_issues": 1114,         ← Count of quote problems
    "delimiter_issues": 1114,     ← Count of custom delimiter uses
    "phone_format_issues": 52,    ← Phone numbers with issues
    "multiline_issues": 7,        ← Fields spanning multiple lines
    "malformed_rows": 0           ← Rows that don't match header
  },
  "encoding_details": {
    "extended_ascii": 622,        ← European characters
    "high_unicode": 293           ← Asian/Middle Eastern chars
  },
  "empty_fields": {
    "WorkPhones": 1163,           ← Per-field empty counts
    "WorkEmails": 1152,
    ...
  },
  "special_chars": {
    "U+00FC": 165,                ← Unicode point: count
    "U+00E9": 72,
    ...
  },
  "problematic_fields": [
    "HomeLocation",               ← Fields that need attention
    "Summary"
  ]
}
```

---

## Performance Notes

| File Size | Record Count | Processing Time |
|-----------|--------------|-----------------|
| <1 MB | <2,000 | <5 seconds |
| 1-10 MB | 2,000-20,000 | 5-30 seconds |
| 10-50 MB | 20,000-100,000 | 30-120 seconds |

**Memory Usage:** Approximately 2x file size during processing

---

## Best Practices

### 1. Always Analyze First
```bash
# See what will change before cleaning
python siemens_data_cleaner.py file.csv --analyze-only
```

### 2. Keep Original Files
```bash
# Never overwrite originals
python siemens_data_cleaner.py original.csv --output cleaned.csv
```

### 3. Generate Reports
```bash
# Document what changed
python siemens_data_cleaner.py file.csv --output cleaned.csv --report report.json
```

### 4. Test Before Production
```bash
# Clean a sample first
head -100 large_file.csv > sample.csv
python siemens_data_cleaner.py sample.csv
# Verify results, then process full file
```

### 5. Validate After Cleaning
```python
# Write simple validation script
import csv

with open('cleaned.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    for row in reader:
        # Add your validation checks
        assert row['PersonID'].isdigit()
        assert '@' in row['HomeEmails'] if row['HomeEmails'] else True
```

---

## Integration Examples

### Use in Python Script
```python
from siemens_data_cleaner import SiemensDataCleaner
from pathlib import Path

# Create cleaner instance
cleaner = SiemensDataCleaner(Path('input.csv'))

# Analyze
report = cleaner.analyze()

# Clean if issues found
if report.quote_issues > 0 or report.delimiter_issues > 0:
    cleaned_file = cleaner.clean(Path('output.csv'))
    print(f"Cleaned file: {cleaned_file}")
```

### Use in Data Pipeline
```bash
#!/bin/bash
# data_pipeline.sh

INPUT="raw_candidates.csv"
CLEANED="cleaned_candidates.csv"
REPORT="quality_report.json"

# Step 1: Clean data
python siemens_data_cleaner.py "$INPUT" --output "$CLEANED" --report "$REPORT"

# Step 2: Validate cleaned data
python validate_candidates.py "$CLEANED"

# Step 3: Import to database
python import_to_db.py "$CLEANED"

# Step 4: Archive
mv "$INPUT" "archive/$(date +%Y%m%d)_$INPUT"
```

---

## Troubleshooting

### Issue: Output file is smaller than input
**Cause:** Multiline issues were fixed (records were split across lines)
**Action:** Compare row counts, not file sizes

### Issue: Characters look wrong after cleaning
**Cause:** Console encoding doesn't support UTF-8
**Action:** View in UTF-8 capable editor (VS Code, Notepad++, etc.)

### Issue: Parser still fails on cleaned file
**Cause:** Different delimiter expected
**Action:** Check if your parser expects comma vs pipe delimiter

---

## Script Options Reference

```
usage: siemens_data_cleaner.py [-h] [-o OUTPUT] [-r REPORT] [-a] [-d DELIMITER] input_file

positional arguments:
  input_file            Input CSV file to process

optional arguments:
  -h, --help            Show help message
  -o, --output OUTPUT   Output file for cleaned data
  -r, --report REPORT   Output file for JSON quality report
  -a, --analyze-only    Only analyze, do not clean
  -d, --delimiter DELIMITER
                        CSV delimiter (default: |)
```

---

## Related Documentation

- **Full Analysis:** `SIEMENS_DATA_QUALITY_ANALYSIS.md`
- **Script Source:** `siemens_data_cleaner.py`
- **Sample Output:** `siemens_quality_report.json`

---

**Last Updated:** 2025-11-07
**Script Version:** 1.0
