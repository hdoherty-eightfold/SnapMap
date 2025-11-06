# Mapping Agent

## Version 1.0.0 | Last Updated: 2025-11-06

---

## Agent Identity

**Name**: Mapping Agent
**Version**: 1.0.0
**Status**: Active
**Owner**: SnapMap Core Team
**Domain**: Semantic Field Mapping
**Location**: `features/mapping/AGENT.md`

---

## 1. Role & Responsibilities

### Primary Responsibilities

1. **Semantic Field Matching**: Use vector embeddings to match source fields to target schema fields
2. **Auto-Mapping**: Automatically generate field mappings with confidence scores
3. **Manual Mapping Support**: Allow users to override auto-mappings
4. **Alternative Suggestions**: Provide top 3 alternative mappings for each field
5. **Confidence Scoring**: Calculate similarity scores (0.0-1.0) for each mapping
6. **Embedding Management**: Build and cache vector embeddings for all entity schemas

### Data Sources

- **Vector Embeddings**: Pre-computed embeddings for target schema fields (cached in `backend/app/embeddings/`)
- **Sentence Transformers**: all-MiniLM-L6-v2 model (384-dim embeddings)
- **Entity Schemas**: 16 entity type schemas with field definitions
- **Field Aliases**: Manual alias dictionary for common field name variations
- **Source File Columns**: Column names from uploaded files

### Success Criteria

- **Mapping Speed**: <5 seconds for 50+ source columns
- **Accuracy**: >85% correct mappings for common HR fields
- **Confidence Threshold**: Only suggest mappings with >70% confidence
- **Coverage**: Auto-map >80% of required fields

---

## 2. Feature Capabilities

### What This Agent CAN Do

1. **Semantic matching using vector embeddings** (cosine similarity on sentence embeddings)
2. **Auto-map all source fields** in a single batch request
3. **Generate confidence scores** (0.0-1.0) based on semantic similarity
4. **Provide alternative mappings** (top 3 alternatives per field)
5. **Handle field name variations** (underscores, camelCase, spaces, special characters)
6. **Build and cache embeddings** for all entity schemas
7. **Fall back to fuzzy matching** if embeddings unavailable
8. **Support manual mapping overrides** (user can change any mapping)
9. **Normalize field names** for comparison (remove special chars, lowercase)
10. **Use field metadata** (display names, descriptions) to improve matching
11. **Handle 1:1 mappings** (each target field mapped only once)
12. **Return structured Mapping objects** with source, target, confidence, method, alternatives

### What This Agent CANNOT Do

1. **Validate data quality** (delegates to Validation Agent)
2. **Transform data** (delegates to Transform Agent)
3. **Create new target fields** (schemas are fixed)
4. **Map multiple source fields to one target** (1:1 only)
5. **Learn from user corrections** (no ML training, static embeddings)
6. **Detect entity types** (assumes entity type provided by user or auto-detection)
7. **Handle complex transformations** (e.g., split/merge fields)
8. **Map to nested structures** (flat field mapping only)
9. **Make autonomous mapping decisions** (always provides confidence scores for user review)

---

## 3. Dependencies

### Required Dependencies

- **sentence-transformers**: Embedding model - `pip install sentence-transformers`
  - Model: `all-MiniLM-L6-v2` (lightweight, 384-dim, fast)
- **numpy**: Vector operations - `import numpy as np`
- **schema_manager**: Entity schema access - `backend/app/services/schema_manager.py`
- **field_mapper**: Fuzzy fallback - `backend/app/services/field_mapper.py`
- **Mapping model**: Response schema - `backend/app/models/mapping.py`

### Optional Dependencies

- **Levenshtein**: Fuzzy string matching (fallback) - Falls back to SequenceMatcher if missing
- **Field aliases**: Manual alias dictionary (`backend/app/schemas/field_aliases.json`)

### External Services

None (all processing is local, no API calls)

---

## 4. Architecture & Implementation

### Key Files & Code Locations

#### Backend
- **API Endpoints**: `backend/app/api/endpoints/automapping.py`
  - `POST /automapping/map`: Auto-map fields (Lines 15-85)
  - `POST /automapping/rebuild-embeddings`: Rebuild vector embeddings (Lines 88-120)

- **Services**:
  - `backend/app/services/semantic_matcher.py` (Lines 1-353) **PRIMARY**
    - `find_best_match()`: Semantic matching (Lines 192-249)
    - `map_fields_batch()`: Batch mapping (Lines 251-298)
    - `build_entity_embeddings()`: Build/cache embeddings (Lines 111-177)
    - `cosine_similarity()`: Vector similarity (Lines 188-190)

  - `backend/app/services/field_mapper.py` (Lines 1-254) **FALLBACK**
    - `auto_map()`: Fuzzy matching fallback (Lines 57-124)
    - `calculate_match()`: Levenshtein/fuzzy scoring (Lines 182-219)

- **Models**: `backend/app/models/mapping.py`
  - `Mapping`: Mapping object (source, target, confidence, method, alternatives)
  - `Alternative`: Alternative mapping suggestion

#### Frontend
- **Components**: `frontend/src/components/mapping/FieldMapping.tsx`
  - Auto-mapping UI (Lines 1-400)
  - Manual mapping editor
  - Confidence indicator
  - Alternative suggestions dropdown
  - Visual connection lines between source/target

- **API Client**: `frontend/src/services/api.ts`
  - `autoMapFields()`: Call auto-mapping endpoint

### Current State

#### Implemented Features
- [x] Semantic matching with sentence-transformers
- [x] Vector embedding caching (pickle files)
- [x] Batch field mapping
- [x] Confidence scoring (cosine similarity)
- [x] Top 3 alternative suggestions
- [x] Fuzzy matching fallback
- [x] Manual mapping overrides
- [x] Field name normalization
- [x] Display name and description matching
- [x] Visual mapping UI with connection lines

#### In Progress
None currently

#### Planned
- [ ] User feedback learning: Learn from manual corrections (Priority: High)
- [ ] Entity type detection: Auto-detect entity type from column names (Priority: Medium)
- [ ] Multi-language support: Match fields in non-English languages (Priority: Low)
- [ ] Complex mapping rules: Support split/merge operations (Priority: Low)
- [ ] Mapping templates: Save/reuse common mappings (Priority: High)

---

## 5. Communication Patterns

### Incoming Requests (FROM)

**User (via Frontend)**
- **Action**: Auto-map fields
- **Payload**: `{ source_fields: string[], entity_name: string, min_confidence?: number }`
- **Response**: `{ mappings: Mapping[], stats: { total, auto_mapped, manual_required } }`

**Main Orchestrator**
- **Action**: Generate field mappings
- **Payload**: File ID or source columns
- **Response**: List of Mapping objects

### Outgoing Requests (TO)

**Schema Manager**
- **Action**: Get target schema
- **Purpose**: Retrieve field definitions for target entity
- **Frequency**: Always (every mapping request)

**File Storage**
- **Action**: Retrieve source columns
- **Purpose**: Get column names from uploaded file
- **Frequency**: When file_id provided instead of explicit columns

### Data Flow Diagram

```
┌─────────────────────────┐
│  Upload Agent           │
│  - file_id              │
│  - columns: [...]       │
└───────────┬─────────────┘
            │
            ↓ source columns
┌────────────────────────────────────┐
│  Mapping Agent                     │
│  1. Load entity embeddings (cache) │
│  2. Compute source embeddings      │
│  3. Cosine similarity (all pairs)  │
│  4. Rank by similarity             │
│  5. Apply 1:1 constraint           │
│  6. Generate alternatives          │
│  7. Return Mapping objects         │
└───────────┬────────────────────────┘
            │
            ↓ mappings with confidence
┌─────────────────────────┐
│  Frontend UI            │
│  - Show auto-mappings   │
│  - Confidence badges    │
│  - Allow overrides      │
│  - Show alternatives    │
└─────────────────────────┘
```

---

## 6. Error Handling

### Common Errors

| Error Code | Severity | Description | Recovery |
|------------|----------|-------------|----------|
| `MAPPING_LOW_CONFIDENCE` | Warning | Field mapping confidence <70% | Manually verify mapping |
| `MAPPING_NO_MATCH` | Warning | No good match found for source field | Skip field or map manually |
| `SCHEMA_NOT_FOUND` | Critical | Target entity schema not found | Verify entity name |
| `EMBEDDINGS_NOT_FOUND` | Warning | Embeddings not cached | Rebuild embeddings or use fuzzy fallback |
| `MODEL_LOAD_ERROR` | Critical | Cannot load sentence-transformers model | Install sentence-transformers |
| `EMPTY_SOURCE_FIELDS` | Critical | No source fields provided | Provide at least 1 source field |

### Error Response Format

```json
{
  "status": "success",
  "mappings": [
    {
      "source": "emp_id",
      "target": "EMPLOYEE_ID",
      "confidence": 0.95,
      "method": "semantic",
      "alternatives": [
        {"target": "USER_ID", "confidence": 0.72}
      ]
    }
  ],
  "warnings": [
    {
      "code": "MAPPING_LOW_CONFIDENCE",
      "message": "Field 'middle_name' has low confidence (0.65)",
      "field": "middle_name",
      "suggestion": "Manually verify this mapping"
    }
  ]
}
```

### Validation Rules

1. **Confidence Threshold**
   - **Severity**: Warning
   - **Rule**: Confidence >= 0.70 (70%)
   - **Action**: Flag for manual review if <70%

2. **1:1 Mapping Constraint**
   - **Severity**: Critical
   - **Rule**: Each target field mapped to at most one source field
   - **Action**: Skip duplicate targets, suggest alternatives

3. **Required Fields Coverage**
   - **Severity**: Warning
   - **Rule**: All required target fields should be mapped
   - **Action**: Warn user if required fields unmapped

---

## 7. Performance Considerations

### Performance Targets

- **Response Time**: <5s for 50 source fields
- **Throughput**: 20 concurrent mapping requests
- **Memory Usage**: Max 100MB (embedding cache + computation)
- **CPU Usage**: Max 70% during embedding generation

### Optimization Strategies

1. **Embedding caching**: Pre-compute and cache all entity embeddings (pickle files)
2. **Batch embedding**: Compute all source embeddings in single batch (faster than one-by-one)
3. **Lazy loading**: Load embeddings only when needed for specific entity
4. **Numpy optimization**: Use vectorized operations for similarity calculation
5. **Background initialization**: Pre-build common entity embeddings on startup

### Bottlenecks & Limitations

- **Embedding computation**: Initial embedding generation takes 5-10s per entity
- **Model download**: First run downloads 90MB model (one-time)
- **Memory for large schemas**: 100+ field schemas consume more memory
- **CPU-bound**: Embedding computation is CPU-intensive (not GPU-accelerated)

---

## 8. Testing Checklist

### Unit Tests
- [ ] Semantic matching returns top match
- [ ] Confidence scores are 0.0-1.0
- [ ] 1:1 mapping constraint enforced
- [ ] Alternative suggestions provided
- [ ] Fuzzy fallback when embeddings unavailable
- [ ] Field name normalization works
- [ ] Handle empty source fields list
- [ ] Handle unknown entity types

### Integration Tests
- [ ] Upload → Mapping pipeline
- [ ] Mapping → Validation pipeline
- [ ] Manual mapping override
- [ ] Rebuild embeddings for all entities
- [ ] Cache hit/miss behavior

### Edge Cases
- [ ] Source field matches multiple targets equally
- [ ] All source fields unmapped (confidence <70%)
- [ ] 100+ source fields
- [ ] Special characters in field names
- [ ] Identical source and target field names
- [ ] Entity with 1 required field only

### Performance Tests
- [ ] Test with 10 source fields
- [ ] Test with 50 source fields
- [ ] Test with 100+ source fields
- [ ] Test 10 concurrent mapping requests
- [ ] Measure embedding cache hit rate

---

## 9. Maintenance

### When to Update This Document

- New embedding model adopted
- Confidence threshold changed
- New entity schemas added
- Mapping algorithm improved
- Alternative suggestion count changed
- User feedback learning implemented

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Auto-mapping accuracy | >85% | <75% |
| Average mapping time | <3s | >10s |
| Confidence score avg | >0.80 | <0.65 |
| Required field coverage | >90% | <70% |
| Embedding cache hit rate | >95% | <80% |

### Health Check Endpoint

**Endpoint**: `GET /health/mapping`
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "sentence_transformers": "ok",
    "embeddings_cache": "ok",
    "schema_manager": "ok"
  },
  "stats": {
    "cached_entities": 16,
    "model_name": "all-MiniLM-L6-v2",
    "avg_mapping_time_ms": 2850
  }
}
```

---

## 10. Integration Points

### With Other Agents

| Agent | Integration Type | Data Exchanged |
|-------|------------------|----------------|
| Upload Agent | Request | Source columns, file_id |
| Validation Agent | Response | Mappings for validation |
| Transform Agent | Response | Mappings for transformation |
| Main Orchestrator | Request/Response | Mapping requests, results |

### With External Systems

- **File System**: Embedding cache (pickle files in `backend/app/embeddings/`)
- **HuggingFace Hub**: Model download (one-time, all-MiniLM-L6-v2)

---

## 11. Questions This Agent Can Answer

1. "Auto-map my source fields to Eightfold Employee schema"
2. "What's the confidence score for this mapping?"
3. "Show me alternative mappings for this field"
4. "Which fields couldn't be mapped automatically?"
5. "What mapping method was used?" (semantic vs fuzzy)
6. "How many fields were auto-mapped?"
7. "Which required fields are missing mappings?"
8. "Can I override an auto-mapping?"
9. "How does semantic matching work?"
10. "Why did this field map to that target?"

---

## 12. Questions This Agent CANNOT Answer

1. "Is my data valid?" - Validation Agent
2. "Transform my data using these mappings" - Transform Agent
3. "What entity type is this file?" - Main Orchestrator (future: auto-detection)
4. "Create a new target field" - Schemas are fixed
5. "Learn from my corrections" - Not implemented (future feature)
6. "Map multiple sources to one target" - 1:1 constraint
7. "Fix validation errors" - Validation Agent

---

## Version History

### Version 1.0.0 (2025-11-06)
- Initial Mapping Agent documentation
- Semantic matching with sentence-transformers
- Vector embedding caching
- Batch field mapping
- Confidence scoring with alternatives
- Fuzzy matching fallback
- Manual override support

---

## Notes & Assumptions

- **Assumption 1**: Entity type known before mapping (provided by user or auto-detected upstream)
- **Assumption 2**: Source fields are flat (no nested structures)
- **Assumption 3**: Embeddings are static (no online learning from user feedback)
- **Known Issue 1**: Initial embedding generation takes 5-10s (acceptable, one-time cost)
- **Technical Debt 1**: No user feedback learning - mappings don't improve over time
- **Technical Debt 2**: Entity type detection not implemented - relies on user selection
- **Technical Debt 3**: Mapping templates not supported - users can't save/reuse common mappings
