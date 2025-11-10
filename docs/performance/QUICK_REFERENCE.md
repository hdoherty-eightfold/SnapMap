# Performance Optimization Quick Reference

> Quick tips and code patterns for maintaining high performance

## File Upload & Parsing

### DO: Use optimized parser for large files
```python
from app.services.file_parser_optimized import get_optimized_file_parser

parser = get_optimized_file_parser()
df, metadata = parser.parse_file(file_content, filename)
```

### DON'T: Read entire file multiple times
```python
# BAD
chardet.detect(file_content)  # Reads entire file
pd.read_csv(file_content)     # Reads entire file again

# GOOD
sample = file_content[:10240]  # First 10KB only
chardet.detect(sample)
```

---

## Data Transformation

### DO: Use batch operations
```python
# GOOD - Vectorized
df['NEW_FIELD'] = df['OLD_FIELD'].str.upper()

# BAD - Row by row
for idx, row in df.iterrows():
    df.at[idx, 'NEW_FIELD'] = row['OLD_FIELD'].upper()
```

### DO: Release memory after large operations
```python
import gc

# Process large DataFrame
result = transform_data(large_df)

# Clean up
del large_df
gc.collect()
```

---

## XML Generation

### DO: Use optimized XML transformer
```python
from app.services.xml_transformer_optimized import get_optimized_xml_transformer

transformer = get_optimized_xml_transformer()
xml = transformer.transform_csv_to_xml(df, mappings)
```

### DO: Stream for very large files (50k+ rows)
```python
transformer.transform_csv_to_xml_streaming(
    df, mappings, output_file='/tmp/output.xml'
)
```

---

## Semantic Mapping

### DO: Batch field processing
```python
# GOOD - Single batch call
mappings = matcher.map_fields_batch(all_fields, 'employee')

# BAD - Individual calls
mappings = [
    matcher.find_best_match(field, 'employee')
    for field in all_fields
]
```

### DO: Pre-warm embeddings on startup
```python
# In main.py startup event
@app.on_event("startup")
async def startup_event():
    from app.services.semantic_matcher import get_semantic_matcher
    matcher = get_semantic_matcher()
    # Embeddings loaded in background thread automatically
```

---

## Memory Management

### Monitor memory in development
```python
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

### Profile memory leaks
```python
import tracemalloc

tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

---

## Performance Testing

### Run quick performance check
```bash
cd backend
python performance_test.py
```

### Profile specific function
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your function
result = my_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

---

## Common Pitfalls

### ❌ AVOID: String concatenation in loops
```python
# BAD - O(n²) complexity
xml = ""
for row in rows:
    xml += f"<row>{row}</row>"

# GOOD - O(n) complexity
parts = []
for row in rows:
    parts.append(f"<row>{row}</row>")
xml = ''.join(parts)
```

### ❌ AVOID: Loading full file for metadata
```python
# BAD
df = pd.read_csv(file)  # Loads entire file
row_count = len(df)

# GOOD
df = pd.read_csv(file, nrows=0)  # Header only
row_count = estimate_rows_from_size(file_size)
```

### ❌ AVOID: Nested loops with DataFrame operations
```python
# BAD - O(n²)
for i, row1 in df1.iterrows():
    for j, row2 in df2.iterrows():
        if row1['key'] == row2['key']:
            # ...

# GOOD - O(n)
merged = pd.merge(df1, df2, on='key')
```

---

## Performance Targets (Reference)

| Operation | File Size | Target | Current |
|-----------|-----------|--------|---------|
| Upload/Parse | 100 rows | < 1s | 0.06s ✓ |
| Upload/Parse | 1,000 rows | < 2s | 0.53s ✓ |
| Upload/Parse | 10,000 rows | < 10s | 6.47s ✓ |
| Semantic Mapping | Any | < 5s | 1-2s ✓ |
| Transform | 1,000 rows | < 2s | 0.03s ✓ |
| XML Export | 1,000 rows | < 2s | 0.50s ✓ |
| Complete Pipeline | 10,000 rows | < 10s | 6.31s ✓ |

---

## Quick Debugging

### Slow request? Check these:
1. File size: `len(file_content) / 1024 / 1024` MB
2. Row count: `len(df)`
3. Column count: `len(df.columns)`
4. Memory: `psutil.Process().memory_info().rss / 1024 / 1024` MB
5. Encoding: `chardet.detect(file_content[:10240])`

### Memory leak? Check these:
1. Are DataFrames being deleted after use?
2. Is garbage collection being triggered?
3. Are file handles being closed?
4. Are there circular references?

---

## When to Optimize

### ✅ Optimize when:
- Performance tests fail targets
- User complaints about speed
- Memory usage > 500 MB
- Request timeout errors
- Profiling shows clear hotspot

### ⛔ Don't optimize when:
- Performance targets are met
- Code becomes less readable
- Optimization is premature
- No measured bottleneck
- Maintenance cost too high

---

**Remember:** Measure first, optimize second. Profile to find bottlenecks before making changes.
