# SnapMap User Guide

**Version:** 2.0.0
**Last Updated:** November 7, 2025

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Uploading Files](#uploading-files)
3. [Understanding Delimiter Detection](#understanding-delimiter-detection)
4. [Field Mapping](#field-mapping)
5. [Validation & Error Handling](#validation--error-handling)
6. [Character Encoding](#character-encoding)
7. [Multi-Value Fields](#multi-value-fields)
8. [Exporting Data](#exporting-data)
9. [SFTP Upload](#sftp-upload)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)

---

## Getting Started

### 5-Minute Quick Start

**Goal**: Transform an HR data file into Eightfold-compatible format

**Steps**:
1. Open SnapMap in your browser: http://localhost:5173
2. Drag and drop your CSV or Excel file
3. Review the automatic field mappings
4. Adjust mappings if needed (drag and drop)
5. Click "Validate Data"
6. Export as CSV or XML
7. (Optional) Upload to SFTP server

**That's it!** Your data is transformed and ready for Eightfold.

### What You'll Need

- **Input File**: CSV, pipe-delimited, TSV, or Excel (.xlsx, .xls)
- **File Size**: Up to 100MB
- **Browser**: Modern browser (Chrome, Firefox, Edge, Safari)
- **Internet**: Not required (runs locally after setup)

---

## Uploading Files

### Supported File Formats

SnapMap accepts the following formats:

| Format | Extension | Example Delimiter | Notes |
|--------|-----------|-------------------|-------|
| CSV | `.csv` | Comma (`,`) | Most common format |
| Pipe-delimited | `.csv`, `.txt` | Pipe (`\|`) | Siemens standard |
| Tab-delimited | `.tsv`, `.txt` | Tab (`\t`) | Excel export format |
| Semicolon | `.csv` | Semicolon (`;`) | European Excel format |
| Excel | `.xlsx`, `.xls` | N/A | Direct Excel support |

### How to Upload

#### Method 1: Drag and Drop (Recommended)
1. Click on the upload area
2. Drag your file from File Explorer/Finder
3. Drop it in the upload zone
4. Wait for processing (typically 1-5 seconds)

#### Method 2: File Browser
1. Click "Browse Files"
2. Navigate to your file
3. Select and click "Open"
4. Wait for processing

### What Happens During Upload

```
[Your File] → Auto-detect delimiter → Auto-detect encoding → Parse data → Preview
```

**Processing Steps**:
1. **File Validation**: Check file type and size
2. **Delimiter Detection**: Automatically identify separator (`,`, `|`, `\t`, `;`)
3. **Encoding Detection**: Identify character encoding (UTF-8, Latin-1, Windows-1252)
4. **Data Parsing**: Load data into memory
5. **Multi-Value Detection**: Check for `||` separators (multi-value fields)
6. **Preview Generation**: Show first 5 rows

### Upload Response

After successful upload, you'll see:

```json
{
  "filename": "employees.csv",
  "file_id": "abc123...",
  "row_count": 1213,
  "column_count": 45,
  "detected_delimiter": "|",
  "detected_encoding": "utf-8",
  "columns": ["PERSON ID", "WORK EMAILS", "WORK PHONES", ...]
}
```

**Key Information**:
- **file_id**: Unique identifier for later steps
- **row_count**: Number of data rows (excluding header)
- **column_count**: Number of columns/fields
- **detected_delimiter**: What separator was found
- **detected_encoding**: What character encoding was detected

---

## Understanding Delimiter Detection

### Why It Matters

Different systems export data with different separators:
- **Excel (US)**: Comma (`,`)
- **Excel (Europe)**: Semicolon (`;`)
- **Siemens**: Pipe (`|`)
- **Database exports**: Tab (`\t`)

SnapMap **automatically detects** which delimiter your file uses.

### How It Works

The system analyzes the first few rows and counts occurrences of each delimiter:

```
Row 1: John|Doe|john@example.com
Row 2: Jane|Smith|jane@example.com

Analysis:
- Pipe (|): 2 per row → Winner!
- Comma (,): 0 per row
- Tab (\t): 0 per row
```

### Manual Override

If auto-detection fails:
1. Check the "Detected Format" section
2. Click "Change Delimiter"
3. Select correct delimiter from dropdown
4. File will re-parse automatically

### Common Issues

**Problem**: "Delimiter detection failed"
**Solution**: Your file might be:
- Empty or corrupted
- Single column (no delimiter needed)
- Using an unsupported delimiter

**Problem**: "Wrong delimiter detected"
**Solution**:
- Use manual override
- Check if your data contains quoted strings with commas (e.g., "Last, First")

---

## Field Mapping

### Understanding Automatic Mapping

SnapMap uses **semantic matching** to map your fields to Eightfold fields.

**Example**:
```
Your Field          →  Eightfold Field     (Confidence)
"PERSON ID"         →  "CANDIDATE_ID"      (92%)
"WORK EMAILS"       →  "EMAIL"             (88%)
"FULL NAME"         →  "DISPLAY_NAME"      (85%)
"EMPLOYEE_NUM"      →  "CANDIDATE_ID"      (81%)
```

### How Semantic Matching Works

Instead of exact string matching, SnapMap understands **meaning**:

```
Traditional Matching:
"emp_id" ≠ "EMPLOYEE_ID"  ❌ No match

Semantic Matching:
"emp_id" ≈ "EMPLOYEE_ID"  ✅ 87% confidence
"worker_num" ≈ "EMPLOYEE_ID"  ✅ 81% confidence
"staff_number" ≈ "EMPLOYEE_ID"  ✅ 79% confidence
```

This works because the system uses AI embeddings to understand that "employee", "worker", and "staff" mean similar things.

### Confidence Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100% | Exact or near-exact match | Accept automatically |
| 80-89% | High confidence match | Review recommended |
| 70-79% | Medium confidence | Check carefully |
| Below 70% | Low confidence | Not suggested (manual map) |

### Manual Mapping

If automatic mapping is incorrect or incomplete:

#### Drag and Drop Method
1. Find your source field on the left
2. Drag it to the target field on the right
3. Connection line will appear
4. Repeat for all unmapped fields

#### Click to Map Method
1. Click source field
2. Click target field
3. Mapping is created
4. Click again to remove mapping

### Required Fields

Fields marked with a red asterisk (*) are **required** for Eightfold:

```
CANDIDATE_ID *    (Must be mapped)
FIRST_NAME *      (Must be mapped)
LAST_NAME *       (Must be mapped)
EMAIL             (Optional)
PHONE_NUMBER      (Optional)
```

If required fields are not mapped, you'll see a warning:
```
⚠️ 3 required fields unmapped:
   - CANDIDATE_ID
   - FIRST_NAME
   - LAST_NAME
```

### Entity Types

SnapMap supports multiple entity types:

- **Employee**: Current workforce data
- **Candidate**: Job applicants
- **User**: System users

The system will suggest the most likely entity based on your field names.

### Mapping Statistics

After auto-mapping, you'll see:

```
Mapping Summary:
✅ 42/45 fields mapped (93%)
⚠️ 3 required fields unmapped
ℹ️ 8 target fields unfilled
```

**Tips**:
- Aim for 100% of required fields mapped
- Optional fields can be left unmapped
- Unfilled target fields will be empty in output

---

## Validation & Error Handling

### What Gets Validated

SnapMap validates your data at multiple stages:

#### 1. Upload Validation
- File size (max 100MB)
- File format (CSV, Excel, etc.)
- Character encoding

#### 2. Parsing Validation
- Delimiter detection
- Row count consistency
- Column count consistency

#### 3. Mapping Validation
- Required fields present
- Field types compatible

#### 4. Data Quality Validation
- **Row count**: Input rows = Output rows (no data loss)
- **Field completeness**: % of populated fields
- **Duplicate detection**: Duplicate records flagged
- **Null values**: Missing data in required fields
- **Format validation**: Email, date, phone formats

### Understanding Error Messages

SnapMap provides **actionable** error messages:

#### Example 1: Data Loss Error

```json
{
  "error": {
    "code": "DATA_LOSS_DETECTED",
    "message": "Data loss detected: 44 rows missing (3.6% loss)",
    "lost_rows": 44,
    "total_rows": 1213,
    "loss_percentage": "3.6%",
    "details": {
      "missing_rows": [15, 28, 42, ...],
      "possible_causes": [
        "Duplicate CANDIDATE_ID values",
        "Null values in required fields"
      ]
    }
  }
}
```

**What to do**:
1. Check the missing row numbers in your source file
2. Look for duplicates or null values
3. Clean your data or enable deduplication

#### Example 2: Field Format Error

```json
{
  "error": {
    "code": "INVALID_EMAIL_FORMAT",
    "message": "Invalid email format in row 42",
    "field": "EMAIL",
    "value": "john.doe@",
    "suggestion": "Check email format (must contain @ and domain)"
  }
}
```

**What to do**:
1. Go to row 42 in your source file
2. Fix the email address
3. Re-upload the file

### Validation Options

You can configure validation behavior:

```
☐ Allow duplicates (deduplicate by CANDIDATE_ID)
☐ Skip rows with null required fields
☐ Auto-fix date formats
☑ Strict validation (recommended)
```

### Common Validation Errors

| Error Code | Cause | Solution |
|------------|-------|----------|
| `DATA_LOSS_DETECTED` | Row count mismatch | Check for duplicates or nulls |
| `INVALID_EMAIL_FORMAT` | Malformed email | Fix email format in source |
| `INVALID_DATE_FORMAT` | Unrecognized date | Use ISO format (YYYY-MM-DD) |
| `REQUIRED_FIELD_MISSING` | Required field null | Fill in missing data |
| `DUPLICATE_CANDIDATE_ID` | Duplicate IDs | Enable deduplication or fix IDs |

---

## Character Encoding

### Supported Encodings

SnapMap automatically detects and handles:

1. **UTF-8**: Universal standard (recommended)
2. **UTF-8-BOM**: UTF-8 with byte order mark
3. **Latin-1 (ISO-8859-1)**: Western European characters
4. **Windows-1252 (CP1252)**: Windows default

### International Character Support

SnapMap fully supports special characters from:

#### Turkish
- Characters: ş, ğ, ı, ö, ü, ç, Ş, Ğ, İ, Ö, Ü, Ç
- Example: "Çağlar Şahin" → "Çağlar Şahin" ✅

#### Spanish
- Characters: ñ, á, é, í, ó, ú, ü, Ñ
- Example: "José García" → "José García" ✅

#### German
- Characters: ä, ö, ü, ß, Ä, Ö, Ü
- Example: "Müller Straße" → "Müller Straße" ✅

#### French
- Characters: é, è, ê, ë, à, â, ç, Ç
- Example: "François Léger" → "François Léger" ✅

### Encoding Issues

**Problem**: Characters appear as `�` or `Ã§`
**Cause**: Wrong encoding detected or used
**Solution**:
1. Check your file's encoding in a text editor
2. Re-save as UTF-8 if possible
3. Contact support if issue persists

**Problem**: Turkish ş appears as Ã¾
**Cause**: File is Windows-1252 but detected as UTF-8
**Solution**:
- SnapMap auto-detects this and fixes it
- If not, re-save file as UTF-8

### Best Practices

✅ **DO**:
- Save files as UTF-8 when possible
- Test with a small sample first if using special characters
- Keep a backup of original file

❌ **DON'T**:
- Use ASCII-only encoding for international names
- Mix encodings in the same file
- Manually convert encodings (let SnapMap auto-detect)

---

## Multi-Value Fields

### What Are Multi-Value Fields?

Some fields contain multiple values in a single cell:

```
WORK EMAILS: john@company.com||john.doe@company.com||j.doe@company.com
WORK PHONES: +1-555-0100||+1-555-0101
```

### Separator Standard

SnapMap uses the **double-pipe** (`||`) separator (Siemens standard):

```
Single value:    john@company.com
Multiple values: john@company.com||jane@company.com||admin@company.com
```

### Automatic Detection

During upload, SnapMap automatically detects multi-value fields:

```
Detected multi-value fields:
✅ WORK EMAILS (3 values per row average)
✅ WORK PHONES (2 values per row average)
```

### How They're Transformed

Multi-value fields are converted to nested XML elements:

**Input CSV**:
```csv
CANDIDATE_ID,WORK EMAILS
12345,john@co.com||jane@co.com
```

**Output XML**:
```xml
<employee>
  <candidate_id>12345</candidate_id>
  <email_list>
    <email>john@co.com</email>
    <email>jane@co.com</email>
  </email_list>
</employee>
```

### Supported Multi-Value Fields

- **EMAIL**: Multiple email addresses
- **PHONE_NUMBER**: Multiple phone numbers
- **ADDRESS**: Multiple addresses
- **SKILLS**: Multiple skills/competencies
- Custom fields (any field with `||` separator)

### Formatting Rules

✅ **Correct**:
```
email1@company.com||email2@company.com
```

❌ **Incorrect**:
```
email1@company.com, email2@company.com  (comma, not double-pipe)
email1@company.com | email2@company.com  (single pipe)
email1@company.com;email2@company.com  (semicolon)
```

### Fallback Behavior

If `||` is not detected, SnapMap will try comma-separated values:

```
email1@company.com, email2@company.com
↓
email1@company.com||email2@company.com  (normalized)
```

---

## Exporting Data

### Export Formats

SnapMap supports two export formats:

#### 1. CSV Export
- **Use Case**: Import into Excel, databases, or other systems
- **Format**: Clean, transformed CSV with target schema
- **Encoding**: UTF-8 with BOM (Excel-compatible)
- **Delimiter**: Comma (standard)

#### 2. XML Export
- **Use Case**: Import into Eightfold or SAP SuccessFactors
- **Format**: EF_Employee_List XML structure
- **Schema**: XSD-compliant
- **Multi-Value**: Nested elements for multi-value fields

### How to Export

#### CSV Export
1. Complete field mapping
2. Validate data (click "Validate")
3. Click "Export as CSV"
4. File downloads automatically
5. Filename: `{original_name}_transformed.csv`

#### XML Export
1. Complete field mapping
2. Validate data (click "Validate")
3. Click "Export as XML"
4. File downloads automatically
5. Filename: `{original_name}_transformed.xml`

### CSV Export Example

**Input**:
```csv
PERSON ID|FULL NAME|WORK EMAILS
12345|John Doe|john@co.com
```

**Output**:
```csv
CANDIDATE_ID,DISPLAY_NAME,EMAIL
12345,John Doe,john@co.com
```

Changes:
- Delimiter: `|` → `,`
- Field names: Mapped to Eightfold schema
- Encoding: UTF-8 with BOM
- Clean data: Validated and transformed

### XML Export Example

**Input**:
```csv
PERSON ID|FULL NAME|WORK EMAILS
12345|John Doe|john@co.com||j.doe@co.com
```

**Output**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<EF_Employee_List>
  <employee>
    <candidate_id>12345</candidate_id>
    <display_name>John Doe</display_name>
    <email_list>
      <email>john@co.com</email>
      <email>j.doe@co.com</email>
    </email_list>
  </employee>
</EF_Employee_List>
```

Features:
- Proper XML declaration
- Nested structure for multi-value fields
- UTF-8 encoding
- XSD-compliant structure

### Export Options

```
Format: ○ CSV  ○ XML

Options:
☑ Include header row (CSV only)
☐ Exclude empty fields
☑ Validate before export
☐ Compress output (zip)
```

### Large File Export

For files over 10,000 rows:
- **Streaming export**: Memory-efficient
- **Progress indicator**: Shows % complete
- **Chunked download**: Browser-friendly

```
Exporting... ████████░░ 82% (10,000 / 12,130 rows)
```

---

## SFTP Upload

### What Is SFTP?

SFTP (Secure File Transfer Protocol) lets you upload files directly to a remote server securely.

**Use Cases**:
- Send transformed files to Eightfold's SFTP server
- Upload to SAP SuccessFactors
- Deliver to client's secure server

### Setting Up SFTP Credentials

#### Step 1: Add Credentials
1. Click "SFTP Settings" in sidebar
2. Click "Add New Credential"
3. Fill in the form:

```
Name: Eightfold Production
Host: sftp.eightfold.ai
Port: 22
Username: your_username
Password: ••••••••••
Remote Path: /incoming/employees
```

4. Click "Save"

#### Step 2: Test Connection
1. Find your credential in the list
2. Click "Test Connection"
3. Wait for result:

```
✅ Connection successful
   Server: sftp.eightfold.ai:22
   Remote path: /incoming/employees
   Writable: Yes
```

### Uploading Files

#### Method 1: Direct Upload (After Export)
1. Export your file (CSV or XML)
2. Click "Upload to SFTP"
3. Select credential from dropdown
4. Click "Upload"
5. Wait for confirmation

#### Method 2: Upload from File Browser
1. Go to "SFTP Upload" page
2. Select credential
3. Browse for file
4. Click "Upload"

### Upload Response

```
✅ Upload successful

File: employees_transformed.xml
Size: 2.4 MB
Destination: sftp.eightfold.ai/incoming/employees/employees_transformed.xml
Upload time: 3.2 seconds
```

### Managing Credentials

#### Edit Credentials
1. Click "Edit" next to credential
2. Update fields
3. Click "Save"

**Note**: Password is encrypted and cannot be viewed after saving.

#### Delete Credentials
1. Click "Delete" next to credential
2. Confirm deletion

**Warning**: This cannot be undone.

### Security

- **Encryption**: Passwords encrypted with AES-256
- **Secure Storage**: Credentials stored in encrypted database
- **No Logging**: Passwords never logged or exposed
- **Connection**: SFTP uses SSH encryption (port 22)

### Troubleshooting SFTP

**Problem**: "Connection refused"
**Causes**:
- Wrong host or port
- Firewall blocking connection
- Server is down

**Solution**:
- Verify host and port with server admin
- Check firewall rules
- Try from different network

**Problem**: "Authentication failed"
**Causes**:
- Wrong username or password
- Account locked or expired
- SSH key required (not supported yet)

**Solution**:
- Verify credentials with server admin
- Reset password if needed
- Contact support if SSH key is required

**Problem**: "Permission denied"
**Causes**:
- No write permission on remote path
- Path doesn't exist

**Solution**:
- Verify remote path exists
- Check user permissions with server admin

---

## Troubleshooting

### Common Issues

#### Upload Errors

**Issue**: "File too large (150 MB)"
**Solution**: Split file into smaller chunks (<100MB) or contact admin to increase limit.

**Issue**: "Unsupported file format"
**Solution**: Convert to CSV, TSV, or Excel (.xlsx, .xls).

**Issue**: "Delimiter detection failed"
**Solution**:
1. Check if file has at least 2 columns
2. Try manual delimiter selection
3. Verify file isn't corrupted

#### Mapping Errors

**Issue**: "Low mapping confidence (45%)"
**Solution**:
- Use manual drag-and-drop mapping
- Check if field names are descriptive
- Contact support to add synonyms to dictionary

**Issue**: "Required field not mapped"
**Solution**:
- Manually map the required field
- If source doesn't have this field, add it or contact support for workaround

#### Validation Errors

**Issue**: "Data loss detected: 44 rows missing"
**Solution**:
1. Check error details for row numbers
2. Look for duplicate CANDIDATE_ID values
3. Look for null values in required fields
4. Enable deduplication if duplicates are intentional
5. Clean source data if nulls are errors

**Issue**: "Invalid email format in row 105"
**Solution**:
1. Go to row 105 in source file
2. Fix email format (must be user@domain.com)
3. Re-upload file

#### Export Errors

**Issue**: "Export failed: Memory error"
**Solution**:
- File might be too large
- Contact support for streaming export
- Try splitting into smaller files

**Issue**: "XML validation failed"
**Solution**:
- Check multi-value field formatting
- Verify all required fields are mapped
- Contact support with error details

#### SFTP Errors

**Issue**: "Connection timeout"
**Solution**:
- Check network connectivity
- Verify firewall allows outbound port 22
- Try from different network

**Issue**: "Upload failed: Disk quota exceeded"
**Solution**:
- Contact server admin to increase quota
- Delete old files from remote server

### Getting Help

If you encounter issues not listed here:

1. **Check Logs**: View browser console (F12) for error details
2. **Check API Docs**: http://localhost:8000/api/docs for API-level errors
3. **Create Issue**: GitHub Issues with:
   - Error message (screenshot or text)
   - Steps to reproduce
   - Sample file (if possible)
4. **Contact Support**: support@yourcompany.com

---

## FAQ

### General

**Q: Is my data secure?**
A: Yes. Data is processed locally on the server and not sent to external services. SFTP credentials are encrypted with AES-256.

**Q: Can I use SnapMap offline?**
A: After initial setup, yes. The vector database and all processing are local. Only SFTP uploads require internet.

**Q: What's the maximum file size?**
A: 100MB by default. This can be increased by admin.

**Q: How long are uploaded files stored?**
A: Files are kept in memory for the session only. They are cleared when you close the browser or after 1 hour of inactivity.

### File Formats

**Q: Can I upload Excel files?**
A: Yes, `.xlsx` and `.xls` formats are supported.

**Q: What about Google Sheets?**
A: Export to CSV or Excel first, then upload.

**Q: Can I upload multiple files at once?**
A: Not currently. Upload files one at a time.

### Field Mapping

**Q: Why is the automatic mapping only 60% accurate?**
A: If your field names are very different from standard HR terminology, semantic matching may struggle. Use manual mapping for the rest.

**Q: Can I save my mappings for next time?**
A: Not yet. This feature is planned for a future release.

**Q: What if my source field matches multiple target fields?**
A: The system will suggest the best match. You can view alternative matches by clicking the mapping.

### Validation

**Q: Can I skip validation?**
A: Not recommended. Validation prevents data loss and format errors. However, you can disable specific validation rules in settings.

**Q: What's the difference between "Strict" and "Lenient" validation?**
A:
- **Strict**: Any error prevents export (recommended)
- **Lenient**: Warnings are shown but export is allowed

**Q: Why is my data being deduplicated?**
A: If you enabled "Allow duplicates", rows with duplicate CANDIDATE_ID values are automatically deduplicated, keeping only the first occurrence.

### Export

**Q: Can I export to PDF?**
A: No, only CSV and XML are supported.

**Q: What's the difference between CSV and XML export?**
A:
- **CSV**: Flat structure, easy to open in Excel
- **XML**: Hierarchical structure, required for Eightfold

**Q: Can I customize the XML structure?**
A: No, the XML structure follows the Eightfold XSD schema strictly.

### SFTP

**Q: Can I use SSH key authentication?**
A: Not yet. Only password authentication is currently supported.

**Q: Can I view files on the SFTP server?**
A: Yes, use the "SFTP Explorer" page to browse remote files.

**Q: Can I download files from SFTP?**
A: Not currently. This feature may be added in the future.

### Performance

**Q: How long does it take to process a file?**
A: Typical processing times:
- Small (<1,000 rows): <1 second
- Medium (1,000-10,000 rows): 1-5 seconds
- Large (10,000-100,000 rows): 5-30 seconds

**Q: Why is the upload slow?**
A: Check your network connection. Large files may take time to upload depending on internet speed.

**Q: Can SnapMap handle 1 million rows?**
A: The system is tested up to 100,000 rows. For larger datasets, contact support for custom solutions.

---

## Tips & Best Practices

### Data Preparation

1. **Clean your data first**: Remove duplicates, fix typos
2. **Use descriptive field names**: "Employee ID" is better than "Field1"
3. **Standardize formats**: Use consistent date formats (YYYY-MM-DD)
4. **Test with sample**: Try with 100 rows first, then full file
5. **Keep backups**: Always keep a copy of original file

### Mapping

1. **Review auto-mappings**: Don't blindly trust 100% accuracy
2. **Map required fields first**: Ensure all required fields are mapped
3. **Use consistent naming**: If you always use "emp_id", the system learns
4. **Check confidence scores**: Verify mappings below 80%

### Validation

1. **Run validation before export**: Catch errors early
2. **Read error messages carefully**: They provide actionable guidance
3. **Fix source data**: Don't try to workaround validation errors
4. **Enable strict mode**: Prevent silent data issues

### Export

1. **Choose the right format**: CSV for analysis, XML for Eightfold
2. **Verify row counts**: Input rows should equal output rows
3. **Check character encoding**: Ensure special characters are preserved
4. **Test XML with small file**: Validate XML structure before full export

### SFTP

1. **Test connection first**: Before uploading large files
2. **Use descriptive credential names**: "Eightfold Prod", not "Server 1"
3. **Keep credentials updated**: Change passwords regularly
4. **Monitor uploads**: Check SFTP server to confirm successful uploads

---

## Getting Support

### Self-Service Resources

1. **This User Guide**: Comprehensive how-to documentation
2. **API Documentation**: http://localhost:8000/api/docs
3. **Troubleshooting Guide**: `/docs/TROUBLESHOOTING_GUIDE.md`
4. **FAQ**: See above section

### Contact Support

**Email**: support@yourcompany.com
**Hours**: Monday-Friday, 9 AM - 5 PM EST
**Response Time**: Within 24 hours

**When contacting support, include**:
- Description of issue
- Error message (screenshot or text)
- Steps to reproduce
- Sample file (if applicable and not confidential)

---

*User Guide Version: 2.0.0*
*Last Updated: November 7, 2025*
*Author: SnapMap Team*
