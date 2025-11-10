# Field Mapping Quick Reference

## TL;DR

**Accuracy:** 75% (up from 13.64%)
**Status:** Production Ready ✓
**Test:** `python test_enhanced_mapping.py`

## How to Add New Field Mappings

### Option 1: Add Alias (Recommended - No Code Changes)

Edit: `c:\Code\SnapMap\backend\app\schemas\field_aliases.json`

```json
{
  "EMAIL": [
    "YourNewFieldName",    // <- Add here
    "WorkEmails",
    "Email"
  ]
}
```

**Restart not required** - changes load automatically.

## Matching Methods (Priority Order)

| Method | Confidence | Example |
|--------|-----------|---------|
| Exact | 100% | `FirstName` → `FIRST_NAME` |
| Alias | 95% | `PersonID` → `CANDIDATE_ID` |
| Partial | 85-90% | `WorkEmails` → `EMAIL` |
| Semantic | 70-85% | `Biography` → `SUMMARY` |
| Fuzzy | 70-84% | `EmailAddr` → `EMAIL` |

## Common Tasks

### Test a Specific Field

```python
from app.services.field_mapper import get_field_mapper

mapper = get_field_mapper()
confidence, method = mapper.calculate_match("PersonID", "CANDIDATE_ID")
print(f"{confidence:.2f} ({method})")  # 0.95 (alias)
```

### Map All Fields

```python
from app.services.field_mapper import get_field_mapper
from app.services.schema_manager import get_schema_manager

mapper = get_field_mapper()
schema = get_schema_manager().get_schema("candidate")

source_fields = ["PersonID", "FirstName", "WorkEmails"]
mappings = mapper.auto_map(source_fields, schema, min_confidence=0.70)

for m in mappings:
    print(f"{m.source} → {m.target} ({m.confidence:.2f})")
```

### Lower Confidence Threshold

```python
# Default: 0.70 (70%)
# For more suggestions (with manual review):
mappings = mapper.auto_map(source_fields, schema, min_confidence=0.60)

# For high-precision only:
mappings = mapper.auto_map(source_fields, schema, min_confidence=0.85)
```

## Troubleshooting

### Field Not Mapping?

1. **Check confidence:**
   ```python
   confidence, method = mapper.calculate_match("YourField", "TARGET_FIELD")
   print(confidence)  # If <0.70, add alias
   ```

2. **Add to alias dictionary:**
   ```json
   "TARGET_FIELD": ["YourField", ...]
   ```

3. **Test again:**
   ```bash
   python test_enhanced_mapping.py
   ```

### Wrong Field Mapped?

**Cause:** Multiple fields match with similar confidence.

**Fix:** Add explicit alias (95%) to outrank fuzzy/semantic (70-85%).

### No Mappings at All?

**Cause:** All below 70% threshold.

**Fix:** Temporarily lower threshold to see options:
```python
mappings = mapper.auto_map(source_fields, schema, min_confidence=0.50)
# Review, then add best matches to alias dictionary
```

## Files to Know

| File | Purpose |
|------|---------|
| `app/schemas/field_aliases.json` | Synonym dictionary (edit here!) |
| `app/services/field_mapper.py` | Core matching logic |
| `test_enhanced_mapping.py` | Test suite |
| `FIELD_MAPPING_GUIDE.md` | Full guide |

## Test Results

```
✓ PersonID           → CANDIDATE_ID    (95%, alias)
✓ WorkEmails         → EMAIL           (95%, alias)
✓ WorkPhones         → PHONE           (95%, alias)
✓ FirstName          → FIRST_NAME      (100%, exact)
✓ LastName           → LAST_NAME       (100%, exact)

Accuracy: 75% (Target: 70%) ✓ PASSED
```

## Quick Test

```bash
cd c:\Code\SnapMap\backend
python test_enhanced_mapping.py

# Should show: "ALL TESTS PASSED ✓"
```

---

**Need Help?** See `FIELD_MAPPING_GUIDE.md` for detailed instructions.
