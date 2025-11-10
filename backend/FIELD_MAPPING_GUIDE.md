# Field Mapping Enhancement Guide

## Quick Start

The enhanced field mapping system automatically maps source CSV fields to target schema fields using a multi-stage approach combining synonym dictionaries, semantic analysis, and fuzzy matching.

**Accuracy:** 75% on Siemens test data (up from 13.64%)

## How It Works

### Matching Priority (High to Low)

1. **Exact Match** (100% confidence)
   - Field names match exactly (case-insensitive)
   - Example: `FirstName` → `FIRST_NAME`

2. **Alias Dictionary** (95% confidence)
   - Field name found in synonym dictionary
   - Example: `PersonID` → `CANDIDATE_ID` (via alias)

3. **Partial Match** (85-90% confidence)
   - Substring or shared word components
   - Example: `WorkEmails` contains `Email` → `EMAIL`

4. **Semantic Embeddings** (70-85% confidence)
   - Vector similarity analysis
   - Example: `Biography` → `SUMMARY` (conceptual match)

5. **Fuzzy String** (70-84% confidence)
   - Levenshtein distance
   - Example: `EmailAddr` → `EMAIL` (close spelling)

## Adding New Field Mappings

### Option 1: Update Synonym Dictionary (Recommended)

**File:** `c:\Code\SnapMap\backend\app\schemas\field_aliases.json`

```json
{
  "TARGET_FIELD_NAME": [
    "SourceVariation1",
    "Source_Variation_2",
    "source-variation-3",
    "SOURCEVARIATON4"
  ]
}
```

**Example - Add support for "ApplicantEmail":**

```json
{
  "EMAIL": [
    "WorkEmails",
    "Email",
    "ApplicantEmail",    // <- Add here
    ...
  ]
}
```

**No code changes required!** The system automatically loads changes.

### Option 2: Extend Word Patterns

For specialized domains, add patterns to `_extract_words()` method:

**File:** `c:\Code\SnapMap\backend\app\services\field_mapper.py`

```python
def _extract_words(self, text: str) -> Set[str]:
    patterns = [
        # Add domain-specific patterns here
        "applicant", "candidate", "resume", "cv",  # Recruiting
        "invoice", "payment", "billing",           # Finance
        "patient", "diagnosis", "treatment",       # Healthcare
        ...
    ]
```

## Testing New Mappings

### Quick Test (Single Field)

```python
from app.services.field_mapper import get_field_mapper

mapper = get_field_mapper()
confidence, method = mapper.calculate_match("PersonID", "CANDIDATE_ID")

print(f"Confidence: {confidence:.2f}, Method: {method}")
# Output: Confidence: 0.95, Method: alias
```

### Full Test (Batch)

```bash
cd c:\Code\SnapMap\backend
python test_enhanced_mapping.py
```

Expected output:
```
✓ PASS PersonID → CANDIDATE_ID (confidence: 0.95)
✓ PASS WorkEmails → EMAIL (confidence: 0.95)
...
Mapping Accuracy: 75.00%
Status: ✓ PASSED
```

## Common Scenarios

### Scenario 1: New Data Source (e.g., Workday)

1. Review source field names from Workday export
2. Add Workday-specific aliases to `field_aliases.json`:

```json
{
  "CANDIDATE_ID": [
    "WorkdayID",
    "WD_Person_ID",
    ...existing aliases...
  ]
}
```

3. Run test with sample Workday data
4. Validate accuracy >= 70%

### Scenario 2: Custom Company Fields

If source uses non-standard naming (e.g., "UserPrimaryEmailAddr"):

1. Add to `field_aliases.json`:

```json
{
  "EMAIL": [
    "UserPrimaryEmailAddr",
    ...existing aliases...
  ]
}
```

2. System will automatically match at 95% confidence

### Scenario 3: Field Not Mapping

**Problem:** Field "EmployeeStartDate" not mapping to "HIRING_DATE"

**Diagnosis:**

```python
mapper = get_field_mapper()
confidence, method = mapper.calculate_match("EmployeeStartDate", "HIRING_DATE")
print(confidence, method)  # Shows current confidence
```

**Solutions:**

1. **Add alias** (if <95%):
   ```json
   "HIRING_DATE": ["EmployeeStartDate", ...]
   ```

2. **Check normalization:**
   ```python
   mapper.normalize_field_name("EmployeeStartDate")  # "employeestartdate"
   mapper.normalize_field_name("HIRING_DATE")        # "hiringdate"
   # No overlap → needs alias
   ```

3. **Check word patterns:**
   ```python
   mapper._extract_words("employeestartdate")  # {"employee", "start", "date"}
   mapper._extract_words("hiringdate")         # {"date"}
   # Only "date" overlaps → partial match ~80%
   ```

## Confidence Thresholds

### Default: 0.70 (70%)

Recommended for most use cases. Balances recall vs precision.

### High Accuracy: 0.85 (85%)

Use when data quality is critical (e.g., financial data):

```python
mappings = mapper.auto_map(
    source_fields,
    target_schema,
    min_confidence=0.85  # Only accept high-confidence matches
)
```

### Maximum Coverage: 0.60 (60%)

Use when manual review is available:

```python
mappings = mapper.auto_map(
    source_fields,
    target_schema,
    min_confidence=0.60  # More suggestions, lower confidence
)
```

## Monitoring & Debugging

### View All Mappings with Details

```python
mappings = mapper.auto_map(source_fields, target_schema)

for m in mappings:
    print(f"{m.source:30} → {m.target:20} ({m.confidence:.2f}, {m.method})")
    if m.alternatives:
        print(f"  Alternatives: {[a.target for a in m.alternatives[:3]]}")
```

### Check Unmapped Fields

```python
mapped_sources = {m.source for m in mappings}
unmapped = [f for f in source_fields if f not in mapped_sources]
print(f"Unmapped: {unmapped}")
```

### Method Distribution

```python
from collections import Counter
methods = Counter(m.method for m in mappings)
print(dict(methods))
# {'alias': 5, 'exact': 2, 'partial': 1, 'semantic': 3}
```

## Performance

- **22 fields:** < 1 second
- **100 fields:** < 3 seconds
- **1000 fields:** < 30 seconds

Caching:
- Alias dictionary: Loaded once at startup
- Semantic embeddings: Cached per schema
- Word patterns: Computed on-demand

## Troubleshooting

### Issue: "No mappings found"

**Cause:** All fields below confidence threshold (default 0.70)

**Fix:** Lower threshold temporarily to see what's available:

```python
mappings = mapper.auto_map(source_fields, target_schema, min_confidence=0.50)
# Review suggestions, add best ones to alias dictionary
```

### Issue: "Wrong field mapped"

**Cause:** Multiple fields match with similar confidence

**Solution:** Add explicit alias for correct mapping (95%) to outrank fuzzy match (70-84%)

### Issue: "Semantic matching failed"

**Cause:** Vector DB model not loaded or corrupted cache

**Fix:**

```bash
cd c:\Code\SnapMap\backend
rm -rf app/data/embeddings_cache/  # Clear cache
# Restart application - will rebuild embeddings
```

## Best Practices

1. **Start with Aliases:** Add known synonyms before relying on semantic matching
2. **Test with Real Data:** Use actual source files, not synthetic examples
3. **Review Alternatives:** Check `mapping.alternatives` for close matches
4. **Iterate:** Add aliases based on production feedback
5. **Document:** Comment unusual aliases in `field_aliases.json`

## Support

For issues or questions:
1. Check this guide
2. Review test results: `python test_enhanced_mapping.py`
3. Examine `docs/architecture/field-mapping-enhancement.md`
4. Review implementation: `app/services/field_mapper.py`
