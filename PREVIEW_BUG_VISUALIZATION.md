# Transformation Preview Bug - Visual Analysis

## The Bug in Pictures

### What SHOULD Happen (How Export Works)

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  PreviewCSV.tsx sends:                                         │
│  {                                                             │
│    file_id: "abc-123",                                        │
│    mappings: [...10 mappings...],                            │
│    entity_name: "employee",                                   │
│    sample_size: 50                                           │
│  }                                                           │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Export endpoint)                    │
│  /transform/export                                             │
│                                                                │
│  ✅ Step 1: Check if source_data is None                      │
│     if source_data is None and request.file_id:              │
│                                                               │
│  ✅ Step 2: Retrieve from storage                            │
│     storage = get_file_storage()                             │
│     df = storage.retrieve_dataframe(request.file_id)         │
│                                                              │
│  ✅ Step 3: Convert to dict                                 │
│     source_data = df.to_dict('records')                     │
│     # Now has 5 rows of data!                              │
│                                                            │
│  ✅ Step 4: Transform                                      │
│     engine.transform_data(source_data, mappings, schema)  │
│     # Transforms 5 rows → 5 rows                         │
└───────────────────┬───────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RESPONSE                                    │
│  {                                                             │
│    "transformed_data": [...5 rows...],                        │
│    "row_count": 5,                                           │
│    "transformations_applied": [...]                         │
│  }                                                          │
│  ✅ SUCCESS: 5 rows in, 5 rows out                         │
└─────────────────────────────────────────────────────────────┘
```

---

### What ACTUALLY Happens (Current Preview Endpoint)

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  PreviewCSV.tsx sends:                                         │
│  {                                                             │
│    file_id: "abc-123",                                        │
│    mappings: [...10 mappings...],                            │
│    entity_name: "employee",                                   │
│    sample_size: 50                                           │
│  }                                                           │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                BACKEND (Preview endpoint - BROKEN)              │
│  /transform/preview                                            │
│                                                                │
│  ❌ Step 1: SKIPPED - No file_id check!                      │
│     # Code jumps straight to transformation                  │
│                                                               │
│  ❌ Step 2: Transform with None                              │
│     engine.transform_data(                                   │
│         request.source_data,  # ← This is None!            │
│         request.mappings,                                   │
│         schema                                             │
│     )                                                      │
└───────────────────┬───────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              TRANSFORMATION ENGINE                              │
│  transformer.py                                                │
│                                                                │
│  Line 40: source_df = pd.DataFrame(source_data)              │
│           source_df = pd.DataFrame(None)                     │
│                                                              │
│  Result: Empty DataFrame                                    │
│  ┌──────────┐                                              │
│  │ 0 rows   │                                             │
│  │ 0 cols   │                                            │
│  └──────────┘                                           │
│                                                        │
│  Line 48: output_df = pd.DataFrame(columns=[...])    │
│                                                      │
│  Result: DataFrame with columns but no rows        │
│  ┌────────┬────────┬────────┬─────────────────┐   │
│  │  NAME  │ EMAIL  │  ...   │ LAST_ACTIVITY_TS │  │
│  ├────────┼────────┼────────┼─────────────────┤  │
│  │ (no rows)                                  │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  Line 74-76: Auto-generate LAST_ACTIVITY_TS    │
│  (adds column but still 0 rows)                │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RESPONSE                                    │
│  {                                                             │
│    "transformed_data": [],  ← Empty array!                    │
│    "row_count": 0,         ← Zero rows!                       │
│    "transformations_applied": [                              │
│      "LAST_ACTIVITY_TS: Auto-generated..."                  │
│    ]                                                        │
│  }                                                         │
│  ❌ FAILURE: 5 rows in file, but 0 rows returned          │
└─────────────────────────────────────────────────────────────┘
```

---

## Side-by-Side Code Comparison

### Export Endpoint (✅ WORKING)
```python
# Lines 104-126 in transform.py

# Get source data - either from request or from stored file
source_data = request.source_data

if source_data is None and request.file_id:
    # ✅ Retrieve full data from storage using file_id
    storage = get_file_storage()
    df = storage.retrieve_dataframe(request.file_id)

    if df is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {...}}
        )

    # Convert DataFrame to list of dicts
    source_data = df.to_dict('records')

elif source_data is None:
    raise HTTPException(
        status_code=400,
        detail={"error": {...}}
    )

# Get schema
schema_manager = get_schema_manager()
schema = schema_manager.get_schema(request.entity_name)

# Transform all data
engine = get_transformation_engine()
transformed_df, _ = engine.transform_data(
    source_data,  # ✅ Has actual data!
    request.mappings,
    schema
)
```

### Preview Endpoint (❌ BROKEN)
```python
# Lines 34-45 in transform.py

try:
    # ❌ NO file_id check - missing entirely!

    # Get schema
    schema_manager = get_schema_manager()
    schema = schema_manager.get_schema(request.entity_name)

    # Transform data
    engine = get_transformation_engine()
    transformed_df, transformations = engine.transform_data(
        request.source_data,  # ❌ This is None!
        request.mappings,
        schema
    )
```

---

## The Missing Code

The preview endpoint is missing **22 lines of code** that exist in the export endpoint:

```python
# This code exists in export but NOT in preview:

source_data = request.source_data

if source_data is None and request.file_id:
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

    source_data = df.to_dict('records')

elif source_data is None:
    raise HTTPException(...)
```

---

## Impact Analysis

### User Experience

```
User uploads file (5 rows)
    ↓
Auto-mapping finds 10 field matches
    ↓
User proceeds to Preview
    ↓
Preview shows:
┌─────────────────────────────────┐
│ Input Rows: 5                  │
│ Fields Mapped: 10              │
│ Output Rows: 0  ← ❌ WRONG!   │
│                                │
│ ⚠️ "No transformed data -     │
│    check mappings"            │
└────────────────────────────────┘
    ↓
User is confused:
- "I have 10 fields mapped!"
- "Why are there 0 rows?"
- "My mappings must be wrong..."
    ↓
❌ User loses confidence in the system
```

### But Export Works!

```
Same user clicks "Download CSV"
    ↓
Export endpoint uses file_id correctly
    ↓
Returns 5 rows with all 10 fields mapped
    ↓
✅ User downloads valid CSV file
    ↓
User is even MORE confused:
- "Preview said 0 rows..."
- "But export has 5 rows??"
- "Is the system broken?"
```

---

## Why This Bug Exists

### Timeline (Hypothesis)

```
1. Initial implementation:
   - Upload sends full source_data to preview
   - Preview endpoint works fine
   - No file storage yet

2. Performance optimization added:
   - File storage service created
   - Upload now stores files and returns file_id
   - Export endpoint updated to use file_id
   - ✅ Export works great!

3. Preview endpoint forgotten:
   - Frontend updated to send file_id
   - ❌ Backend preview endpoint NOT updated
   - Preview breaks silently (no errors)
   - Bug ships to production
```

---

## Evidence Trail

### 1. Frontend Console Logs
```javascript
// PreviewCSV.tsx line 39-44
console.log('[PreviewCSV] Loading preview with:', {
  file_id: uploadedFile.file_id,        // ✅ Has value
  entity_name: selectedEntityType,      // ✅ Has value
  mappings_count: mappings.length,      // ✅ Has value (10)
  sample_size: 50                       // ✅ Has value
});
// NOTE: No source_data logged - because it's not sent!
```

### 2. Backend Receives
```python
# What Pydantic parses:
PreviewRequest(
    mappings=[...10 mappings...],
    source_data=None,           # ← Not provided by frontend
    file_id="abc-123",          # ← Provided by frontend
    sample_size=50,
    entity_name="employee"
)
```

### 3. Transformation Engine Receives
```python
# Line 42 in transform.py calls:
engine.transform_data(
    None,           # ← source_data is None!
    [...],          # ← mappings (valid)
    schema          # ← schema (valid)
)

# Line 40 in transformer.py:
source_df = pd.DataFrame(None)
# Creates empty DataFrame:
# - 0 rows
# - 0 columns
```

### 4. Result
```python
# Line 48 in transformer.py:
output_df = pd.DataFrame(columns=target_columns)
# Has columns but 0 rows

# Line 54-68: Apply mappings
# for source_col, target_col in mapping_dict.items():
#     if source_col in source_df.columns:  # ← False! source_df has no columns
#         # This block never executes

# Line 101: return output_df, transformations
# Returns DataFrame with 0 rows
```

---

## Fix Verification Steps

After applying fix:

1. ✅ Upload file with 5 rows
2. ✅ Auto-map 10 fields
3. ✅ Navigate to Preview
4. ✅ Backend receives file_id
5. ✅ Backend retrieves data from storage
6. ✅ Backend transforms 5 rows
7. ✅ Frontend displays 5 output rows
8. ✅ User sees correct preview
9. ✅ Export also works (already working)

---

## Conclusion

**The bug is a simple omission**: The `/transform/preview` endpoint is missing the file retrieval logic that was successfully implemented in `/transform/export`.

**Fix complexity**: LOW (copy 22 lines of working code)

**Fix risk**: LOW (identical pattern already proven in export)

**User impact**: HIGH (preview appears completely broken)

**Recommended priority**: URGENT (core feature completely broken)
