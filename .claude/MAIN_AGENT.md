# SnapMap Main Orchestrator Agent

## Agent Identity

**Name**: SnapMap Main Orchestrator
**Version**: 1.0.0
**Status**: Active
**Owner**: SnapMap Core Team
**Last Updated**: 2025-11-06

## Overview

The **Main Orchestrator Agent** is the central intelligence hub for the SnapMap HR Data Transformation Platform. It coordinates all data transformation workflows, routes requests to specialized feature agents, maintains platform-wide context, and ensures data quality throughout the transformation pipeline.

## Role & Responsibilities

### Primary Responsibilities

1. **Request Routing**: Analyze user requests and delegate to appropriate feature agents
2. **Workflow Orchestration**: Coordinate multi-stage transformation pipelines
3. **Context Management**: Maintain state across upload → mapping → validation → export
4. **Data Quality**: Ensure data consistency throughout the transformation pipeline
5. **Error Coordination**: Aggregate errors from all stages and provide unified responses
6. **Health Monitoring**: Track agent performance and data pipeline health
7. **Cross-Agent Communication**: Facilitate data sharing between feature agents

### Data Sources

- **File Storage**: Uploaded CSV/Excel files (temporary in-memory)
- **Vector Database**: ChromaDB embeddings for semantic matching
- **Schema Registry**: 16 entity type schemas (JSON files)
- **SFTP Credentials**: Encrypted connection storage
- **Session State**: File IDs, mappings, validation results

## Feature Capabilities

### ✅ What This Agent CAN Do

1. **Route transformation requests** to Upload, Mapping, Validation, Transform, Export agents
2. **Coordinate end-to-end workflows** (Upload → Map → Validate → Transform → Export → SFTP)
3. **Maintain data lineage** throughout the transformation pipeline
4. **Aggregate validation errors** from multiple validation stages
5. **Track file lifecycle** from upload to final export
6. **Manage session state** (file IDs, mappings, entity types)
7. **Monitor agent health** and performance metrics
8. **Handle error recovery** and retry logic
9. **Coordinate SFTP uploads** with proper credential management
10. **Provide unified API responses** combining data from multiple agents
11. **Track transformation history** for audit purposes
12. **Manage concurrent requests** from multiple users
13. **Enforce data quality gates** before allowing progression to next stage
14. **Coordinate schema updates** across all agents

### ❌ What This Agent CANNOT Do

1. **Parse files directly** (delegates to Upload Agent)
2. **Perform semantic matching** (delegates to Mapping Agent)
3. **Execute validation rules** (delegates to Validation Agent)
4. **Generate XML/CSV output** (delegates to Transform Agent)
5. **Upload to SFTP servers** (delegates to SFTP Agent)
6. **Make autonomous decisions** about user data
7. **Modify source data** without user approval
8. **Bypass validation rules** for expedited processing
9. **Access external APIs** without proper authorization

## Dependencies

### Required Feature Agents

- **Upload Agent**: File parsing and entity detection
- **Mapping Agent**: Semantic field matching
- **Validation Agent**: Schema validation and quality checks
- **Transform Agent**: CSV/XML transformation
- **Export Agent**: File generation and formatting
- **SFTP Agent**: Remote file operations

### Optional Feature Agents

- **Enhancement Agent**: System health monitoring
- **Analytics Agent**: Usage tracking (future)

### External Dependencies

- **ChromaDB**: Vector database (port: default)
- **FastAPI Backend**: REST API (port 8000)
- **React Frontend**: User interface (port 5173)

## Architecture

### Agent Communication Pattern

```
User Request
    ↓
Main Orchestrator Agent (analyzes and routes)
    ↓
    ├─→ Upload Agent (parse file)
    │       ↓
    ├─→ Mapping Agent (auto-map fields)
    │       ↓
    ├─→ Validation Agent (validate schema)
    │       ↓
    ├─→ Transform Agent (transform data)
    │       ↓
    ├─→ Export Agent (generate output)
    │       ↓
    └─→ SFTP Agent (upload file)
    ↓
Main Orchestrator (aggregates results)
    ↓
Unified Response to User
```

### Workflow Orchestration

**Standard Pipeline:**
```yaml
Stage 1: Upload
  - Upload Agent receives file
  - Detect entity type
  - Store in file storage
  - Return file_id

Stage 2: Mapping
  - Mapping Agent receives file_id
  - Semantic auto-mapping
  - Return field mappings

Stage 3: Validation
  - Validation Agent receives file_id + mappings
  - Schema validation
  - Data quality checks
  - Return validation report

Stage 4: Transform (if validation passes)
  - Transform Agent receives file_id + mappings
  - Apply transformations
  - Return preview data

Stage 5: Export
  - Export Agent generates CSV/XML
  - Return downloadable file

Stage 6: SFTP (optional)
  - SFTP Agent uploads file
  - Return confirmation
```

## Request Routing Matrix

| User Request | Primary Agent | Supporting Agents | Response Time |
|--------------|---------------|-------------------|---------------|
| Upload CSV/Excel file | Upload Agent | - | <2s |
| Auto-map fields | Mapping Agent | Upload Agent (for schema) | <5s |
| Validate data quality | Validation Agent | Upload, Mapping | <10s |
| Preview transformation | Transform Agent | Upload, Mapping, Validation | <3s |
| Export CSV | Export Agent | Transform | <5s |
| Export XML | Export Agent | Transform | <5s |
| Upload via SFTP | SFTP Agent | Export | <10s |
| System health check | Enhancement Agent | All agents | <30s |

## Communication Patterns

### Incoming Requests (FROM)

- **User**: Via React frontend → FastAPI endpoints
- **Enhancement Agent**: Health check requests
- **Feature Agents**: Data requests from peer agents

### Outgoing Requests (TO)

- **Upload Agent**: Parse files, detect entities
- **Mapping Agent**: Generate field mappings
- **Validation Agent**: Validate data quality
- **Transform Agent**: Transform data
- **Export Agent**: Generate output files
- **SFTP Agent**: Upload files
- **Enhancement Agent**: Report health status

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                  User (Frontend)                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Main Orchestrator Agent                    │
│  - Routes requests                                       │
│  - Maintains context (file_id, mappings, state)        │
│  - Aggregates responses                                  │
└─────┬───────┬────────┬────────┬────────┬────────┬──────┘
      │       │        │        │        │        │
      ↓       ↓        ↓        ↓        ↓        ↓
   Upload  Mapping  Validate Transform Export   SFTP
   Agent   Agent    Agent    Agent     Agent   Agent
      │       │        │        │        │        │
      ↓       ↓        ↓        ↓        ↓        ↓
  File    Vector   Schema   Pandas   File    Paramiko
 Storage   DB      Rules   Transform Output   SFTP
```

## Error Handling

### Error Aggregation Pattern

The Main Agent aggregates errors from all feature agents:

```python
{
  "status": "error",
  "pipeline_stage": "validation",
  "errors": {
    "upload": [],
    "mapping": ["Low confidence mapping for field X"],
    "validation": [
      {"severity": "critical", "field": "EMAIL", "message": "Missing required field"},
      {"severity": "warning", "field": "DATE", "message": "Inconsistent date format"}
    ]
  },
  "recovery_suggestions": [
    "Add EMAIL column to source file",
    "Standardize date format to YYYY-MM-DD"
  ]
}
```

### Error Recovery Strategies

1. **File Upload Errors**: Return clear error messages about file format/size
2. **Mapping Errors**: Suggest manual mappings for low-confidence fields
3. **Validation Errors**: Provide row-level details and auto-fix suggestions
4. **Transform Errors**: Log transformation issues and skip problematic rows
5. **Export Errors**: Retry with different encoding or format options
6. **SFTP Errors**: Verify credentials, test connection, retry upload

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Only load agents when needed
2. **Parallel Processing**: Run independent validation checks concurrently
3. **Caching**: Cache schema definitions, entity metadata
4. **Batch Processing**: Process multiple rows in single pass
5. **Streaming**: Stream large files instead of loading into memory
6. **Connection Pooling**: Reuse SFTP connections

### Performance Targets

- **File Upload**: <2s for files up to 100MB
- **Auto-Mapping**: <5s for files with 50+ columns
- **Validation**: <10s for files with 10,000+ rows
- **CSV Export**: <5s for 10,000 row files
- **XML Export**: <8s for 10,000 row files

## Current State

### Implemented Features

- ✅ File upload and parsing (CSV, Excel)
- ✅ Semantic field mapping (vector embeddings)
- ✅ Schema validation (comprehensive rules)
- ✅ CSV transformation and export
- ✅ XML transformation and export
- ✅ SFTP credential management
- ✅ SFTP file upload

### Known Limitations

- Limited to Employee entity type (16 entity schemas exist, only Employee tested)
- No batch file processing
- No scheduled/automated transformations
- SFTP Explorer UI built but backend APIs not implemented
- No transformation templates/presets
- No audit logging

### Recent Changes

- **2025-11-06**: Created Main Orchestrator Agent documentation
- **2025-11-05**: Fixed XML transformation (Pydantic compatibility)
- **2025-11-05**: Removed AI terminology, updated documentation
- **2025-11-05**: Reorganized UI workflow (Map → Review instead of Review → Map)

## Testing Checklist

### Before Deployment

- [ ] Test complete pipeline: Upload → Map → Validate → Export → SFTP
- [ ] Test error handling at each stage
- [ ] Verify data consistency throughout pipeline
- [ ] Test concurrent user sessions
- [ ] Verify SFTP credential security
- [ ] Test file size limits (up to 100MB)
- [ ] Test all entity types (not just Employee)

### Integration Tests

- [ ] Upload Agent → Mapping Agent handoff
- [ ] Mapping Agent → Validation Agent handoff
- [ ] Validation Agent → Transform Agent handoff
- [ ] Transform Agent → Export Agent handoff
- [ ] Export Agent → SFTP Agent handoff

## Maintenance

### When to Update This Document

- New feature agents are added
- Pipeline stages change
- New entity types are supported
- Error handling patterns change
- Performance targets are updated

### Monitoring Metrics

- **Request Volume**: Requests per hour/day
- **Pipeline Success Rate**: % of complete end-to-end transformations
- **Stage Failure Rates**: % failures at each stage
- **Average Processing Time**: Per pipeline stage
- **Error Frequency**: Top 10 errors by occurrence
- **SFTP Upload Success Rate**: % successful uploads

## Integration Points

### With Other Agents

- **Upload Agent**: Receives file_id, delegates parsing
- **Mapping Agent**: Provides source columns, receives mappings
- **Validation Agent**: Provides mappings, receives validation report
- **Transform Agent**: Coordinates transformation workflow
- **Export Agent**: Requests file generation
- **SFTP Agent**: Coordinates secure uploads
- **Enhancement Agent**: Reports health metrics

### With External Systems

- **ChromaDB**: Semantic field matching (via Mapping Agent)
- **FastAPI**: REST API endpoints
- **React Frontend**: User interface
- **File System**: Temporary file storage
- **SFTP Servers**: Remote file uploads

## Questions This Agent Can Answer

1. "Upload my employee data file"
2. "Auto-map fields to Eightfold schema"
3. "Validate my data quality"
4. "Show me a preview of the transformation"
5. "Export as CSV"
6. "Export as XML"
7. "Upload to SFTP server"
8. "What's the status of my transformation?"
9. "Show me all validation errors"
10. "Which fields are mapped?"
11. "What entity type is this file?"
12. "How do I fix these validation errors?"

## Questions This Agent CANNOT Answer

1. "Modify the Eightfold schema" (schemas are fixed)
2. "Change validation rules" (rules are standardized)
3. "Execute SQL queries" (no direct DB access)
4. "Access other users' data" (isolated sessions)
5. "Deploy to production" (deployment is manual)
6. "Integrate with Eightfold API" (out of scope)

## Future Enhancements

### Planned Features (Wishlist)

- Batch file processing (process multiple files at once)
- Scheduled transformations (cron jobs)
- Transformation templates (save/reuse mappings)
- Support for all 16 entity types
- Audit logging and compliance reporting
- Real-time collaboration (multiple users on same file)
- SFTP Explorer backend APIs
- Data lineage tracking
- Version control for transformations

### Agent Evolution

- **Analytics Agent**: Track usage patterns, generate insights
- **Security Agent**: Monitor for data leaks, PII handling
- **Compliance Agent**: Ensure GDPR, CCPA compliance
- **Performance Agent**: Auto-tune transformation parameters

## Version History

### Version 1.0.0 (2025-11-06)
- Initial Main Orchestrator Agent documentation
- Defined agent coordination patterns
- Established request routing matrix
- Created communication protocols
