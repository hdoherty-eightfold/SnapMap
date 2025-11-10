# SnapMap Performance Test Report
**Generated:** 2025-11-07 05:43:23
**Python Version:** 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]

---

## Performance Summary

| Scenario | Test | Rows | Time (s) | Memory (MB) | Status |
|----------|------|------|----------|-------------|--------|
| Small File (100 rows) | file_upload_parse | 100 | 0.061 | 2.17 | PASS |
| Small File (100 rows) | semantic_mapping | 100 | 1.009 | 45.14 | PASS |
| Small File (100 rows) | data_transformation | 100 | 0.024 | 0.27 | PASS |
| Small File (100 rows) | xml_export | 100 | 0.071 | 0.08 | PASS |
| Small File (100 rows) | complete_pipeline | 100 | 0.971 | 42.06 | PASS |
| Medium File (1,000 rows) | file_upload_parse | 1,000 | 0.531 | 3.20 | PASS |
| Medium File (1,000 rows) | semantic_mapping | 1,000 | 1.035 | 0.23 | PASS |
| Medium File (1,000 rows) | data_transformation | 1,000 | 0.027 | 0.00 | PASS |
| Medium File (1,000 rows) | xml_export | 1,000 | 0.504 | 0.57 | PASS |
| Medium File (1,000 rows) | complete_pipeline | 1,000 | 1.511 | 3.75 | PASS |
| Large File (10,000 rows) | file_upload_parse | 10,000 | 6.467 | 31.96 | PASS |
| Large File (10,000 rows) | semantic_mapping | 10,000 | 1.455 | -0.51 | PASS |
| Large File (10,000 rows) | data_transformation | 10,000 | 0.137 | 1.86 | PASS |
| Large File (10,000 rows) | xml_export | 10,000 | 5.242 | -10.09 | PASS |
| Large File (10,000 rows) | complete_pipeline | 10,000 | 6.314 | 24.40 | PASS |
| Siemens File (1,213 rows) | file_upload_parse | 1,213 | 5.928 | 2.06 | PASS |
| Siemens File (1,213 rows) | semantic_mapping | 1,213 | 1.017 | 0.21 | PASS |
| Siemens File (1,213 rows) | data_transformation | 1,213 | 0.029 | 0.01 | PASS |
| Siemens File (1,213 rows) | xml_export | 1,213 | 0.564 | 0.06 | PASS |
| Siemens File (1,213 rows) | complete_pipeline | 1,213 | 3.945 | 5.39 | PASS |

---

## Detailed Results

### Small File (100 rows)

#### file_upload_parse
- **Parse Time:** 0.061s
- **File Size:** 0.05 MB
- **Target:** < 1s - PASS
- **Memory Used:** 2.17 MB

#### semantic_mapping
- **Mapping Time:** 1.009s
- **Fields Mapped:** 9/50
- **Time per Field:** 20.17ms
- **Target:** < 2s - PASS
- **Memory Used:** 45.14 MB

#### data_transformation
- **Transform Time:** 0.024s
- **Target:** < 1s - PASS
- **Memory Used:** 0.27 MB

#### xml_export
- **XML Generation Time:** 0.071s
- **XML Size:** 0.02 MB
- **Memory Used:** 0.08 MB

#### complete_pipeline
- **Parse:** 0.064s
- **Mapping:** 0.878s
- **Transform:** 0.017s
- **XML Export:** 0.012s
- **TOTAL:** 0.971s
- **Target:** < 10s - PASS
- **Memory Used:** 42.06 MB

### Medium File (1,000 rows)

#### file_upload_parse
- **Parse Time:** 0.531s
- **File Size:** 0.56 MB
- **Target:** < 2s - PASS
- **Memory Used:** 3.20 MB

#### semantic_mapping
- **Mapping Time:** 1.035s
- **Fields Mapped:** 9/50
- **Time per Field:** 20.70ms
- **Target:** < 3s - PASS
- **Memory Used:** 0.23 MB

#### data_transformation
- **Transform Time:** 0.027s
- **Target:** < 2s - PASS
- **Memory Used:** 0.00 MB

#### xml_export
- **XML Generation Time:** 0.504s
- **XML Size:** 0.24 MB
- **Memory Used:** 0.57 MB

#### complete_pipeline
- **Parse:** 0.474s
- **Mapping:** 0.854s
- **Transform:** 0.089s
- **XML Export:** 0.094s
- **TOTAL:** 1.511s
- **Target:** < 10s - PASS
- **Memory Used:** 3.75 MB

### Large File (10,000 rows)

#### file_upload_parse
- **Parse Time:** 6.467s
- **File Size:** 6.02 MB
- **Target:** < 10s - PASS
- **Memory Used:** 31.96 MB

#### semantic_mapping
- **Mapping Time:** 1.455s
- **Fields Mapped:** 9/50
- **Time per Field:** 29.10ms
- **Target:** < 5s - PASS
- **Memory Used:** -0.51 MB

#### data_transformation
- **Transform Time:** 0.137s
- **Target:** < 5s - PASS
- **Memory Used:** 1.86 MB

#### xml_export
- **XML Generation Time:** 5.242s
- **XML Size:** 2.48 MB
- **Memory Used:** -10.09 MB

#### complete_pipeline
- **Parse:** 4.196s
- **Mapping:** 0.624s
- **Transform:** 0.568s
- **XML Export:** 0.926s
- **TOTAL:** 6.314s
- **Target:** < 10s - PASS
- **Memory Used:** 24.40 MB

### Siemens File (1,213 rows)

#### file_upload_parse
- **Parse Time:** 5.928s
- **File Size:** 2.52 MB
- **Target:** < 10s - PASS
- **Memory Used:** 2.06 MB

#### semantic_mapping
- **Mapping Time:** 1.017s
- **Fields Mapped:** 9/56
- **Time per Field:** 18.16ms
- **Target:** < 5s - PASS
- **Memory Used:** 0.21 MB

#### data_transformation
- **Transform Time:** 0.029s
- **Target:** < 5s - PASS
- **Memory Used:** 0.01 MB

#### xml_export
- **XML Generation Time:** 0.564s
- **XML Size:** 0.30 MB
- **Memory Used:** 0.06 MB

#### complete_pipeline
- **Parse:** 2.932s
- **Mapping:** 0.796s
- **Transform:** 0.109s
- **XML Export:** 0.108s
- **TOTAL:** 3.945s
- **Target:** < 10s - PASS
- **Memory Used:** 5.39 MB

---

## Bottleneck Analysis

### Time Distribution in Complete Pipeline

**Small File (100 rows):**
- Parse: 0.064s (6.6%)
- Mapping: 0.878s (90.4%)
- Transform: 0.017s (1.8%)
- XML Export: 0.012s (1.2%)

**Medium File (1,000 rows):**
- Parse: 0.474s (31.4%)
- Mapping: 0.854s (56.5%)
- Transform: 0.089s (5.9%)
- XML Export: 0.094s (6.2%)

**Large File (10,000 rows):**
- Parse: 4.196s (66.4%)
- Mapping: 0.624s (9.9%)
- Transform: 0.568s (9.0%)
- XML Export: 0.926s (14.7%)

**Siemens File (1,213 rows):**
- Parse: 2.932s (74.3%)
- Mapping: 0.796s (20.2%)
- Transform: 0.109s (2.8%)
- XML Export: 0.108s (2.7%)

---

## Optimization Recommendations

**Semantic Mapping** is a bottleneck (>30% of time). Consider: caching embeddings more aggressively, batch processing optimizations.

**File Parsing** is a bottleneck (>30% of time). Consider: parallel chunk processing, faster CSV library (polars), or streaming parsing.

---

## Memory Usage Analysis

**Peak Memory Usage:** 45.14 MB
**Average Memory for Large Files (10k+ rows):** 9.53 MB

---

## Scalability Assessment

**Time per Row:**
- 100 rows: 9.711ms/row
- 1,000 rows: 1.511ms/row
- 1,213 rows: 3.252ms/row
- 10,000 rows: 0.631ms/row

**Assessment:** Excellent scalability - near-linear performance.

---

## Top Performance Hotspots (From Profiling)
