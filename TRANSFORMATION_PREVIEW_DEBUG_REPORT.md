# Transformation Preview Debug Report

**Issue**: Transformation Preview page shows 0 output rows when there are 5 input rows and 10 fields mapped.

**User Report**:
- Input Rows: 5
- Fields Mapped: 10
- Output Rows: 0
- Error message: "No transformed data - check mappings"

---

## Investigation Summary

### 1. Frontend Code Analysis (PreviewCSV.tsx)

**Location**: `c:\Code\SnapMap\frontend\src\components\export\PreviewCSV.tsx`

**Lines 46-51**: The entity_name fix IS PRESENT
```typescript
const response = await previewTransform({
  mappings,
  file_id: uploadedFile.file_id,
  entity_name: selectedEntityType, // ✅ CRITICAL FIX: Added missing entity_name parameter
  sample_size: 50,
});
```

**What the frontend sends**:
- `mappings`: Array of field mappings
- `file_id`: Unique identifier for the uploaded file
- `entity_name`: Selected entity type (e.g., "employee")
- `sample_size`: Number of rows to preview (50)
- `source_data`: **NOT SENT** (undefined/omitted)

---

### 2. Backend API Analysis (transform.py)

**Location**: `c:\Code\SnapMap\backend\app\api\endpoints\transform.py`

#### /transform/preview Endpoint (BROKEN)

**Lines 19-56**: The preview endpoint

**Problem identified at lines 39-45**:
```python
# Transform data
engine = get_transformation_engine()
transformed_df, transformations = engine.transform_data(
    request.source_data,  # ❌ BUG: This is None when file_id is provided
    request.mappings,
    schema
)
```

**The bug**:
- The endpoint directly uses `request.source_data` without checking if it's `None`
- When `file_id` is provided (frontend's approach), `source_data` is `None`
- The transformation engine receives `None` as input data

---

#### /transform/export Endpoint (WORKING)

**Lines 87-189**: The export endpoint

**Lines 104-126 show the CORRECT implementation**:
```python
# Get source data - either from request or from stored file
source_data = request.source_data

if source_data is None and request.file_id:
    # ✅ CORRECT: Retrieve full data from storage using file_id
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
    raise HTTPException(...)
```

---

### 3. Data Flow Analysis

**Current (Broken) Flow**:
```
Frontend (PreviewCSV.tsx)
  ↓
  Sends: { file_id, mappings, entity_name, sample_size }
  (NO source_data)
  ↓
Backend (/transform/preview)
  ↓
  Line 42: engine.transform_data(request.source_data, ...)
  ↓
  request.source_data = None
  ↓
TransformationEngine.transform_data()
  ↓
  Line 40: source_df = pd.DataFrame(None)
  ↓
  Creates EMPTY DataFrame (0 rows, 0 columns)
  ↓
  Line 48: output_df = pd.DataFrame(columns=target_columns)
  ↓
  output_df has columns but 0 rows
  ↓
Backend Response
  ↓
  {
    "transformed_data": [],           // ❌ Empty array
    "transformations_applied": [...], // ✅ Has transformations
    "row_count": 0,                   // ❌ Zero rows
    "warnings": []
  }
  ↓
Frontend displays: "No transformed data - check mappings"
```

---

### 4. Root Cause Identification

**ROOT CAUSE**: The `/transform/preview` endpoint is missing the file retrieval logic that exists in the `/transform/export` endpoint.

**Specific Issue**:
1. Frontend correctly sends `file_id` instead of full `source_data` (to avoid sending large datasets)
2. Backend `/transform/preview` endpoint does NOT check for `file_id` and retrieve data
3. Backend passes `None` to the transformation engine
4. Transformation engine creates an empty DataFrame from `None`
5. Result: 0 rows transformed

---

### 5. Evidence

#### Test Confirmation

**File**: `c:\Code\SnapMap\test_preview_debug.py`

**Test Result**:
```json
{
  "transformed_data": [],
  "transformations_applied": [
    "LAST_ACTIVITY_TS: Auto-generated with current timestamp"
  ],
  "row_count": 0,
  "warnings": []
}
```

**Observation**: Even though transformations are applied (LAST_ACTIVITY_TS auto-generation), there are 0 rows because the input DataFrame was empty.

---

### 6. Backend Model Analysis

**Location**: `c:\Code\SnapMap\backend\app\models\transform.py`

**PreviewRequest Model (Lines 11-17)**:
```python
class PreviewRequest(BaseModel):
    """Request for transformation preview"""
    mappings: List[Mapping] = Field(..., description="Field mappings")
    source_data: Optional[List[Dict[str, Any]]] = Field(None, description="Source data rows (optional if file_id provided)")
    file_id: Optional[str] = Field(None, description="File ID from upload (alternative to source_data)")
    sample_size: Optional[int] = Field(5, description="Number of rows to preview")
    entity_name: Optional[str] = Field("employee", description="Entity type to transform to")
```

**Key Points**:
- `source_data` is **Optional** (can be None)
- `file_id` is **Optional** (alternative to source_data)
- The model correctly defines both options
- The **endpoint implementation** doesn't honor this design

---

### 7. Comparison: Preview vs Export

| Aspect | /transform/preview | /transform/export |
|--------|-------------------|-------------------|
| **Checks if source_data is None** | ❌ No | ✅ Yes |
| **Retrieves from file_id** | ❌ No | ✅ Yes |
| **Handles missing file** | ❌ No | ✅ Yes (404 error) |
| **Validates file_id** | ❌ No | ✅ Yes |
| **Result** | ❌ 0 rows | ✅ Works correctly |

---

## Detailed Findings

### Is the entity_name parameter being sent?
✅ **YES** - The frontend sends `entity_name: selectedEntityType` at line 49 of PreviewCSV.tsx

### What does the backend receive?
The backend receives:
```json
{
  "mappings": [...],
  "file_id": "some-uuid",
  "entity_name": "employee",
  "sample_size": 50,
  "source_data": null
}
```

### What does the backend return?
```json
{
  "transformed_data": [],
  "transformations_applied": [
    "LAST_ACTIVITY_TS: Auto-generated with current timestamp"
  ],
  "row_count": 0,
  "warnings": []
}
```

### Are there any errors in the transformation process?
❌ **NO EXPLICIT ERRORS** - The transformation "succeeds" but operates on an empty dataset.

The transformation engine correctly:
1. Creates an empty source DataFrame from `None`
2. Creates an empty output DataFrame with target columns
3. Applies auto-generation for LAST_ACTIVITY_TS (but to 0 rows)
4. Returns 0 rows successfully

---

## Fix Required

**Location**: `c:\Code\SnapMap\backend\app\api\endpoints\transform.py`

**Lines to modify**: 34-45

**Add file retrieval logic** (copy from export endpoint):

```python
try:
    # Get source data
    source_data = request.source_data

    # If source_data is None, retrieve from file_id
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

    # Transform data (now with actual data!)
    engine = get_transformation_engine()
    transformed_df, transformations = engine.transform_data(
        source_data,  # Now has actual data
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

## Additional Observations

### Frontend Types Mismatch

**Location**: `c:\Code\SnapMap\frontend\src\types\index.ts`

**Lines 103-107**:
```typescript
export interface PreviewRequest {
  mappings: Mapping[];
  source_data: Record<string, any>[]; // ❌ Not optional
  sample_size?: number;
  // ❌ Missing: file_id
  // ❌ Missing: entity_name
}
```

**Issue**: The frontend TypeScript type doesn't match the backend Pydantic model.

**Backend model has**:
- `source_data: Optional[...]`
- `file_id: Optional[str]`
- `entity_name: Optional[str]`

**Frontend type has**:
- `source_data: Required`
- No `file_id`
- No `entity_name`

**Impact**: TypeScript won't catch the missing fields, but the code works because:
1. The api.ts service is untyped for these fields
2. JavaScript/TypeScript allows extra properties
3. The backend Pydantic model is more permissive

---

## Summary

### Root Cause
The `/transform/preview` endpoint doesn't retrieve data from `file_id` when `source_data` is `None`.

### Why It Happens
The endpoint was likely implemented before the file storage feature was added, and wasn't updated when `/transform/export` got the file retrieval logic.

### Impact
- Users see 0 output rows in preview
- Preview appears broken even though mappings are correct
- Export endpoint works fine (has the correct logic)

### Files Affected
1. `backend/app/api/endpoints/transform.py` - Lines 34-45 need file retrieval logic
2. `frontend/src/types/index.ts` - Lines 103-107 should add optional file_id and entity_name

---

## Next Steps (DO NOT IMPLEMENT - REPORTING ONLY)

1. Add file retrieval logic to `/transform/preview` endpoint (mirror `/transform/export`)
2. Update frontend TypeScript types to match backend Pydantic models
3. Test with actual file upload and preview workflow
4. Verify both preview and export work correctly

---

**Report Generated**: 2025-11-08
**Investigated By**: Debug Agent
**Status**: Root cause identified, fix not applied (as requested)
