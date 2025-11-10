# Performance Engineering Documentation

This directory contains comprehensive performance testing, analysis, and optimization documentation for the SnapMap application.

## Documents

### 1. [Performance Report](../../PERFORMANCE_REPORT.md)
**Latest Test Results:** 2025-11-07

Comprehensive benchmark results covering:
- Small files (100 rows)
- Medium files (1,000 rows)
- Large files (10,000 rows)
- Production scenario (Siemens file with 1,213 rows, special characters, multi-value fields)

**Key Findings:**
- ✅ All performance targets met or exceeded
- ✅ Complete pipeline: 6.31s for 10,000 rows
- ✅ Memory usage: < 50 MB peak
- ✅ Excellent scalability (near-linear)

### 2. [Optimization Guide](OPTIMIZATION_GUIDE.md)
**For:** Tech Leads, DevOps Engineers, Performance Engineers

Detailed guide covering:
- Bottleneck analysis with profiling data
- Optimization strategies and implementations
- Production deployment recommendations
- Monitoring and alerting setup
- Scalability analysis and projections
- Memory management strategies
- Future optimization roadmap

### 3. [Quick Reference](QUICK_REFERENCE.md)
**For:** Developers

Quick tips and code patterns:
- Performance do's and don'ts
- Common pitfalls to avoid
- Code examples and anti-patterns
- Quick debugging checklist
- Performance targets reference

## Running Performance Tests

### Prerequisites
```bash
cd backend
pip install -r requirements.txt
python build_vector_db.py  # Build embeddings
```

### Execute Tests
```bash
python performance_test.py
```

### Output Files
- `PERFORMANCE_REPORT.md` - Human-readable report
- `performance_results.json` - Machine-readable results for CI/CD

### Test Scenarios
1. **Small File (100 rows)**
   - Basic functionality test
   - Validates minimal overhead
   - Target: < 1s per operation

2. **Medium File (1,000 rows)**
   - Typical user scenario
   - Balanced load test
   - Target: < 3s per operation

3. **Large File (10,000 rows)**
   - Stress test
   - Scalability validation
   - Target: < 10s complete pipeline

4. **Siemens File (1,213 rows)**
   - Real-world production scenario
   - Special characters (Turkish, Spanish)
   - Multi-value fields (|| separator)
   - 52+ fields
   - Target: < 10s complete pipeline

## Optimization Implementations

### Available Optimized Services

#### 1. Optimized File Parser
**File:** `backend/app/services/file_parser_optimized.py`

**Features:**
- Sample-based encoding detection (10KB sample vs entire file)
- Single-pass delimiter detection
- Chunked reading for large files (> 5MB)
- C engine for CSV parsing
- 40-60% faster for large files

**Usage:**
```python
from app.services.file_parser_optimized import get_optimized_file_parser

parser = get_optimized_file_parser()
df, metadata = parser.parse_file(file_content, filename)
```

#### 2. Optimized XML Transformer
**File:** `backend/app/services/xml_transformer_optimized.py`

**Features:**
- String concatenation (3-5x faster than ElementTree)
- Batch processing (1000 rows per batch)
- Streaming output for very large files
- XML escaping optimization

**Usage:**
```python
from app.services.xml_transformer_optimized import get_optimized_xml_transformer

transformer = get_optimized_xml_transformer()
xml = transformer.transform_csv_to_xml(df, mappings)

# For very large files (50k+ rows):
transformer.transform_csv_to_xml_streaming(df, mappings, '/tmp/output.xml')
```

### Integration Steps

To enable optimized services in production:

1. **Update upload endpoint:**
```python
# In app/api/endpoints/upload.py
from app.services.file_parser_optimized import get_optimized_file_parser

parser = get_optimized_file_parser()  # Instead of get_file_parser()
```

2. **Update transform endpoint:**
```python
# In app/api/endpoints/transform.py
from app.services.xml_transformer_optimized import get_optimized_xml_transformer

xml_transformer = get_optimized_xml_transformer()  # Instead of get_xml_transformer()
```

3. **Test thoroughly:**
```bash
# Run full test suite
pytest backend/tests/

# Run performance benchmarks
python backend/performance_test.py

# Verify results
cat PERFORMANCE_REPORT.md
```

## Performance Monitoring

### Key Metrics

Monitor these metrics in production:

1. **Request Latency**
   - P50: Median response time
   - P95: 95th percentile
   - P99: 99th percentile
   - Target: P95 < 10s

2. **Memory Usage**
   - Current: Active memory
   - Peak: Maximum observed
   - Target: Peak < 500 MB

3. **Throughput**
   - Requests per second
   - Files processed per hour
   - Target: > 100 files/hour

4. **Error Rate**
   - Parse errors
   - Transformation errors
   - Target: < 1%

5. **Cache Hit Rate**
   - Embedding cache
   - File cache
   - Target: > 70%

### Monitoring Setup

**Recommended Tools:**
- Application: Prometheus + Grafana
- Logging: ELK Stack or CloudWatch
- APM: New Relic or DataDog
- Uptime: Pingdom or UptimeRobot

**Example Grafana Dashboard:**
- Request latency over time
- Memory usage trends
- Error rate graph
- Throughput metrics
- Cache hit rate

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Performance Tests

on:
  pull_request:
    branches: [ master ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  performance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Build embeddings
        run: |
          cd backend
          python build_vector_db.py

      - name: Run performance tests
        run: |
          cd backend
          python performance_test.py

      - name: Check performance targets
        run: |
          # Verify all tests passed
          python scripts/check_targets.py

      - name: Upload performance report
        uses: actions/upload-artifact@v2
        with:
          name: performance-report
          path: PERFORMANCE_REPORT.md

      - name: Comment PR with results
        uses: actions/github-script@v5
        with:
          script: |
            // Post performance results as PR comment
```

## Troubleshooting

### Common Issues

#### Issue: Tests fail with "File not found"
**Solution:** Run `python build_vector_db.py` first to create embeddings

#### Issue: Import errors
**Solution:** Ensure you're in the `backend/` directory and dependencies are installed

#### Issue: Memory errors during tests
**Solution:** Close other applications, or reduce test file sizes in `performance_test.py`

#### Issue: Slow performance on first run
**Solution:** First run loads models into memory. Subsequent runs will be faster.

### Getting Help

1. Check existing documentation
2. Review performance report for insights
3. Run profiling to identify bottlenecks
4. Consult optimization guide for solutions

## Best Practices

### Development
- ✅ Profile before optimizing
- ✅ Measure impact of changes
- ✅ Run performance tests before committing
- ✅ Document optimization decisions

### Code Review
- ✅ Check for performance anti-patterns
- ✅ Verify vectorized operations used
- ✅ Confirm memory cleanup
- ✅ Validate against performance targets

### Deployment
- ✅ Run full performance test suite
- ✅ Compare results with baseline
- ✅ Monitor metrics post-deployment
- ✅ Have rollback plan ready

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-07 | Initial performance testing and optimization |

## Contributors

- Performance Engineering Team
- Backend Development Team

---

**Last Updated:** 2025-11-07
**Next Review:** 2025-12-07 (Monthly)
