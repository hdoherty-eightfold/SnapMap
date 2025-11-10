# Preview Transformation Fix Specification

**Bug ID**: Preview shows 0 output rows
**Severity**: CRITICAL
**Root Cause**: Missing file_id retrieval logic in `/transform/preview` endpoint
**Files to Modify**: 1 file (backend)
**Lines to Add**: ~25 lines

---

## File to Modify

**File**: `c:\Code\SnapMap\backend\app\api\endpoints\transform.py`

**Function**: `preview_transformation`

**Lines**: 34-45 (current broken implementation)

---

## Current Code (BROKEN)

```python
# Lines 34-45
try:
    # Get schema
    schema_manager = get_schema_manager()
    schema = schema_manager.get_schema(request.entity_name)

    # Transform data
    engine = get_transformation_engine()
    transformed_df, transformations = engine.transform_data(
        request.source_data,  # ❌ BUG: This is None when file_id is provided
        request.mappings,
        schema
    )

    # Get sample
    sample_size = min(request.sample_size or 5, len(transformed_df))
    sample_df = transformed_df.head(sample_size)

    return PreviewResponse(
        transformed_data=sample_df.to_dict('records'),
        transformations_applied=transformations,
        row_count=len(transformed_df),
        warnings=[]
    )
```

---

## Fixed Code

```python
# Lines 34-68 (after fix)
try:
    # Get source data - either from request or from stored file
    source_data = request.source_data

    if source_data is None and request.file_id:
        # Retrieve full data from storage using file_id
        storage = get_file_storage()
        df = storage.retrieve_dataframe(request.file_id)

        if df is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": f"File with ID '{request.file_id}' not found or expired",
                    },
                    "status": 404
                }
            )

        # Convert DataFrame to list of dicts
        source_data = df.to_dict('records')

    elif source_data is None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "MISSING_SOURCE_DATA",
                    "message": "Either 'source_data' or 'file_id' must be provided",
                },
                "status": 400
            }
        )

    # Get schema
    schema_manager = get_schema_manager()
    schema = schema_manager.get_schema(request.entity_name)

    # Transform data
    engine = get_transformation_engine()
    transformed_df, transformations = engine.transform_data(
        source_data,  # ✅ FIX: Now has actual data from file_id
        request.mappings,
        schema
    )

    # Get sample
    sample_size = min(request.sample_size or 5, len(transformed_df))
    sample_df = transformed_df.head(sample_size)

    return PreviewResponse(
        transformed_data=sample_df.to_dict('records'),
        transformations_applied=transformations,
        row_count=len(transformed_df),
        warnings=[]
    )
```

---

## Diff View

```diff
 try:
+    # Get source data - either from request or from stored file
+    source_data = request.source_data
+
+    if source_data is None and request.file_id:
+        # Retrieve full data from storage using file_id
+        storage = get_file_storage()
+        df = storage.retrieve_dataframe(request.file_id)
+
+        if df is None:
+            raise HTTPException(
+                status_code=404,
+                detail={
+                    "error": {
+                        "code": "FILE_NOT_FOUND",
+                        "message": f"File with ID '{request.file_id}' not found or expired",
+                    },
+                    "status": 404
+                }
+            )
+
+        # Convert DataFrame to list of dicts
+        source_data = df.to_dict('records')
+
+    elif source_data is None:
+        raise HTTPException(
+            status_code=400,
+            detail={
+                "error": {
+                    "code": "MISSING_SOURCE_DATA",
+                    "message": "Either 'source_data' or 'file_id' must be provided",
+                },
+                "status": 400
+            }
+        )
+
     # Get schema
     schema_manager = get_schema_manager()
     schema = schema_manager.get_schema(request.entity_name)

     # Transform data
     engine = get_transformation_engine()
     transformed_df, transformations = engine.transform_data(
-        request.source_data,  # ❌ BUG
+        source_data,  # ✅ FIX
         request.mappings,
         schema
     )
```

---

## Implementation Notes

### Changes Required

1. **Add file retrieval logic** (lines to insert after line 34):
   - Check if `source_data` is `None` and `file_id` is provided
   - Retrieve DataFrame from file storage
   - Handle file not found (404 error)
   - Convert DataFrame to list of dicts

2. **Add validation** (lines to insert after file retrieval):
   - Check if both `source_data` and `file_id` are `None`
   - Return 400 error with clear message

3. **Update transformation call** (line 42):
   - Change `request.source_data` to `source_data` variable

### Import Statement

Ensure this import exists at the top of the file (already present):
```python
from app.services.file_storage import get_file_storage
```

---

## Testing Steps

### Before Fix
```bash
# Start backend
cd backend
python -m uvicorn main:app --reload

# Run test
python ../test_preview_debug.py

# Expected: 0 rows returned
```

### After Fix
```bash
# Run same test
python ../test_preview_debug.py

# Expected: Actual rows returned (if valid file_id exists)
# Or 404 error if file not found
```

### Manual Testing
1. Upload a CSV file with 5 rows
2. Navigate through auto-mapping
3. Go to Preview page
4. Verify: Output Rows should be 5 (not 0)
5. Verify: Transformed data table shows 5 rows
6. Click "Download CSV"
7. Verify: CSV contains 5 rows
8. Click "Transform to XML"
9. Verify: XML preview shows 5 records

---

## Edge Cases to Handle

### Case 1: Valid file_id
```python
# Input
{
  "file_id": "valid-uuid",
  "source_data": None,
  "mappings": [...],
  "entity_name": "employee"
}

# Expected Output
{
  "transformed_data": [...rows...],
  "row_count": 5,
  "transformations_applied": [...]
}
```

### Case 2: Invalid/expired file_id
```python
# Input
{
  "file_id": "expired-uuid",
  "source_data": None,
  "mappings": [...],
  "entity_name": "employee"
}

# Expected Output (404 Error)
{
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "File with ID 'expired-uuid' not found or expired"
  },
  "status": 404
}
```

### Case 3: No file_id, no source_data
```python
# Input
{
  "file_id": None,
  "source_data": None,
  "mappings": [...],
  "entity_name": "employee"
}

# Expected Output (400 Error)
{
  "error": {
    "code": "MISSING_SOURCE_DATA",
    "message": "Either 'source_data' or 'file_id' must be provided"
  },
  "status": 400
}
```

### Case 4: Both file_id and source_data provided
```python
# Input
{
  "file_id": "some-uuid",
  "source_data": [{...}],
  "mappings": [...],
  "entity_name": "employee"
}

# Expected Behavior
# Use source_data (takes precedence)
# This is the current behavior - source_data checked first
```

---

## Verification Checklist

After implementing the fix:

- [ ] Code compiles without errors
- [ ] Import statement for `get_file_storage` exists
- [ ] File retrieval logic matches export endpoint exactly
- [ ] Error handling for file not found (404)
- [ ] Error handling for missing data (400)
- [ ] Variable name changed from `request.source_data` to `source_data`
- [ ] Backend restarts successfully
- [ ] Test script shows rows returned (not 0)
- [ ] Manual test: Upload file → Preview shows correct row count
- [ ] Manual test: Preview shows transformed data in table
- [ ] Manual test: Export still works correctly
- [ ] Manual test: XML transformation still works

---

## Rollback Plan

If the fix causes issues:

1. **Immediate Rollback**:
   ```bash
   git checkout backend/app/api/endpoints/transform.py
   # Restart backend
   ```

2. **Symptoms of Regression**:
   - Preview endpoint returns 500 errors
   - File not found errors for valid uploads
   - Export endpoint breaks (unlikely - separate code)

3. **Debug Steps**:
   - Check backend logs for exceptions
   - Verify `file_storage.py` service is working
   - Test file storage directly: `storage.retrieve_dataframe(file_id)`

---

## Related Issues to Monitor

### 1. File Expiration
- Files expire after 1 hour (file_storage.py line 165)
- If user uploads, waits 1+ hour, then previews: 404 error
- This is expected behavior (not a bug)

### 2. Frontend Type Mismatch
- TypeScript types don't include `file_id` and `entity_name`
- Not critical (JavaScript is permissive)
- Consider updating `frontend/src/types/index.ts` lines 103-107

### 3. XML Preview Endpoint
- Already has file_id handling (lines 245-253)
- Uses `storage.get_dataframe()` (alias of `retrieve_dataframe()`)
- Should continue working after fix

---

## Performance Considerations

### Memory Impact
- **Before**: No data loaded (0 rows) - minimal memory
- **After**: Full dataset loaded for preview - same as export
- Sample size limits preview to 50 rows (default)
- Full dataset stays in memory briefly during transformation

### Disk I/O
- **Added**: 1 parquet file read per preview request
- File storage uses efficient parquet format
- Typical file read: <100ms for small datasets

### API Response Time
- **Before**: ~50ms (no data to process)
- **After**: ~200-500ms (includes file retrieval + transformation)
- Still acceptable for user experience
- Same performance as export endpoint

---

## Code Quality

### Pattern Consistency
✅ **AFTER FIX**: Preview endpoint matches Export endpoint pattern
- Both check for `file_id`
- Both retrieve from storage
- Both handle file not found
- Both validate missing data

### Error Handling
✅ **IMPROVED**:
- Clear error messages
- Proper HTTP status codes (404, 400)
- Structured error responses
- Helpful messages for debugging

### Maintainability
✅ **IMPROVED**:
- Consistent code patterns across endpoints
- Future developers will see same pattern
- Easier to add features (applies to all endpoints)

---

## Documentation Updates Needed

After fix is applied:

1. **API Documentation** (`docs/API_REFERENCE.md`):
   - Update `/transform/preview` endpoint description
   - Add note about `file_id` parameter
   - Add 404 error response example

2. **Changelog** (`docs/CHANGELOG.md`):
   ```markdown
   ## [Unreleased]
   ### Fixed
   - Preview transformation now correctly retrieves data using file_id
   - Preview endpoint no longer returns 0 rows when file_id is provided
   ```

3. **Developer Guide** (`docs/DEVELOPER_GUIDE.md`):
   - Add pattern for file_id handling
   - Document file storage service usage

---

## Estimated Implementation Time

- **Code Changes**: 5 minutes (copy from export endpoint)
- **Testing**: 10 minutes (manual + automated)
- **Verification**: 5 minutes (checklist)
- **Documentation**: 10 minutes (update docs)

**Total**: ~30 minutes

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaks preview endpoint | LOW | HIGH | Copy exact pattern from working export endpoint |
| Breaks export endpoint | VERY LOW | HIGH | Changes are isolated to preview function |
| File not found errors | LOW | MEDIUM | Proper error handling with 404 response |
| Performance degradation | LOW | LOW | Same pattern as export (already in production) |
| Memory issues | VERY LOW | MEDIUM | Sample size limits data loaded |

**Overall Risk**: LOW (well-understood fix, proven pattern)

---

## Success Metrics

After deploying fix:

1. **Preview Accuracy**:
   - Output row count matches input row count
   - Transformed data displays correctly
   - No more "No transformed data" errors

2. **User Satisfaction**:
   - Users can preview before export
   - Confidence in transformation results
   - Reduced support tickets

3. **System Reliability**:
   - Error rates for preview endpoint decrease
   - Successful preview requests increase
   - Export functionality unaffected

---

**Fix Priority**: URGENT
**Complexity**: LOW
**Risk**: LOW
**Impact**: HIGH
**Recommended**: Implement immediately
