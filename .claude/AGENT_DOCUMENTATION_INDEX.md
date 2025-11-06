# SnapMap Agent Documentation Index

## Overview

This document provides an index of all agent documentation files in the SnapMap multi-agent system. Each agent follows the standardized FEATURE_TEMPLATE structure for consistency and maintainability.

**Documentation Created**: 2025-11-06
**Total Agents**: 7 feature agents + 1 template
**Total Lines**: 3,435 lines of documentation
**Architecture**: Based on wheelstrategy multi-agent pattern

---

## Agent Documentation Files

### 1. Feature Template
**Location**: `.claude/FEATURE_TEMPLATE.md`
**Lines**: 344
**Status**: Template
**Purpose**: Standard template for all feature agent documentation

**Sections**:
- Agent Identity
- Role & Responsibilities
- Feature Capabilities
- Dependencies
- Architecture & Implementation
- Communication Patterns
- Error Handling
- Performance Considerations
- Testing Checklist
- Maintenance
- Integration Points
- Questions This Agent Can/Cannot Answer

---

### 2. Upload Agent
**Location**: `features/upload/AGENT.md`
**Lines**: 428
**Status**: Active
**Domain**: File Upload & Parsing

**Key Capabilities**:
- Parse CSV and Excel files (.csv, .xlsx, .xls)
- Auto-detect column data types
- Store files in memory with unique file_id
- Generate sample data preview (first 10 rows)
- Validate file size (100MB limit)

**Implementation**:
- Backend: `backend/app/api/endpoints/upload.py`
- Services: `backend/app/services/file_parser.py`, `file_storage.py`
- Frontend: `frontend/src/components/upload/FileUpload.tsx`

---

### 3. Mapping Agent
**Location**: `features/mapping/AGENT.md`
**Lines**: 450
**Status**: Active
**Domain**: Semantic Field Mapping

**Key Capabilities**:
- Semantic field matching using vector embeddings (sentence-transformers)
- Auto-map source fields to target schema with confidence scores
- Provide top 3 alternative mappings per field
- Cache embeddings for fast retrieval
- Fallback to fuzzy matching when embeddings unavailable

**Implementation**:
- Backend: `backend/app/api/endpoints/automapping.py`
- Services: `backend/app/services/semantic_matcher.py` (PRIMARY), `field_mapper.py` (FALLBACK)
- Frontend: `frontend/src/components/mapping/FieldMapping.tsx`
- Model: all-MiniLM-L6-v2 (384-dim embeddings)

---

### 4. Validation Agent
**Location**: `features/validation/AGENT.md`
**Lines**: 473
**Status**: Active
**Domain**: Data Quality Validation

**Key Capabilities**:
- Schema validation against Eightfold entity schemas
- Header validation with fuzzy typo detection
- Required field validation
- Data type validation (email, date, numeric)
- Invalid character detection
- Max length validation
- Severity-based issue classification (critical, warning, info)

**Implementation**:
- Backend: `backend/app/api/endpoints/validate.py`
- Services: `backend/app/services/csv_validator.py` (551 lines)
- Frontend: `frontend/src/components/review/IssueReview.tsx`

---

### 5. Transform Agent
**Location**: `features/transform/AGENT.md`
**Lines**: 443
**Status**: Active
**Domain**: Data Transformation

**Key Capabilities**:
- CSV transformation to Eightfold format
- XML transformation (EF_Employee_List structure)
- Date format conversion (YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS)
- Auto-generate timestamps for required fields
- Handle list fields (email_list, phone_list)
- Transformation preview functionality

**Implementation**:
- Backend: `backend/app/api/endpoints/transform.py` (332 lines)
- Services: `backend/app/services/transformer.py` (CSV), `xml_transformer.py` (XML - 310 lines)
- Frontend: `frontend/src/components/export/PreviewCSV.tsx`, `PreviewXML.tsx`

---

### 6. Export Agent
**Location**: `features/export/AGENT.md`
**Lines**: 430
**Status**: Active
**Domain**: File Export & Download

**Key Capabilities**:
- Export CSV files with UTF-8 encoding
- Export XML files (Eightfold format)
- Stream file downloads to browser
- Generate filenames automatically or use user-provided
- Set proper Content-Disposition headers
- Handle files up to 100MB

**Implementation**:
- Backend: `backend/app/api/endpoints/transform.py` (export endpoints)
- Uses: FastAPI StreamingResponse, io.StringIO
- Frontend: Export buttons in PreviewCSV.tsx and PreviewXML.tsx

---

### 7. SFTP Agent
**Location**: `features/sftp/AGENT.md`
**Lines**: 464
**Status**: Active
**Domain**: SFTP File Transfer

**Key Capabilities**:
- SFTP credential management (CRUD operations)
- Connection testing via paramiko
- File upload to remote SFTP servers
- Credential persistence (JSON with base64 encoding)
- Support multiple credential sets
- Connection status tracking

**Implementation**:
- Backend: `backend/app/api/endpoints/sftp.py`
- Services: `backend/app/services/sftp_manager.py` (322 lines)
- Frontend: `frontend/src/components/sftp/SFTPCredentialManager.tsx`, `SFTPUploadPage.tsx`
- Storage: `/tmp/snapmap_sftp/credentials.json`

**CRITICAL NOTE**: Password storage uses base64 encoding (NOT SECURE for production). Must implement proper encryption (Fernet, KMS, Vault) before production deployment.

---

### 8. Enhancement Agent
**Location**: `features/enhancement/AGENT.md`
**Lines**: 403
**Status**: Planned (Template for Future Implementation)
**Domain**: System Health & Improvement Recommendations

**Planned Capabilities**:
- System health monitoring across all agents
- Feature usage analytics
- Error pattern analysis
- Performance tracking
- AI-driven improvement recommendations
- Alerting system
- Analytics dashboards (Grafana/Prometheus)

**Implementation Status**: NOT YET IMPLEMENTED - This is a template for future development when system reaches production scale.

---

## Documentation Standards

All agent documentation follows the **FEATURE_TEMPLATE** structure:

1. **Agent Identity**: Name, version, status, owner, domain, location
2. **Role & Responsibilities**: Primary duties, data sources, success criteria
3. **Feature Capabilities**: CAN/CANNOT do lists
4. **Dependencies**: Required/optional dependencies, external services
5. **Architecture & Implementation**: Key files with line numbers, current state
6. **Communication Patterns**: Incoming/outgoing requests, data flow diagrams
7. **Error Handling**: Common errors, response formats, validation rules
8. **Performance Considerations**: Targets, optimizations, bottlenecks
9. **Testing Checklist**: Unit/integration/edge case/performance tests
10. **Maintenance**: Update triggers, monitoring metrics, health checks
11. **Integration Points**: Agent-to-agent and external system integration
12. **Questions Can/Cannot Answer**: Scope boundaries

---

## Agent Communication Protocol

All agents follow the **AGENT_INTERACTION_PROTOCOL.md**:

- **Central Coordination**: All inter-agent communication flows through Main Orchestrator
- **Stateless Communication**: Agents don't maintain state about other agents
- **Standard Request/Response**: JSON format with request_id, timestamp, status
- **Error Transparency**: All errors reported with actionable recovery steps
- **Documentation-First**: Changes to capabilities require doc updates
- **Quality Gates**: Validation checks before agent handoff

---

## Implementation Summary

| Agent | Status | Lines | Backend Files | Frontend Files | Key Dependencies |
|-------|--------|-------|---------------|----------------|------------------|
| Upload | Active | 428 | upload.py, file_parser.py | FileUpload.tsx | pandas, fastapi |
| Mapping | Active | 450 | automapping.py, semantic_matcher.py | FieldMapping.tsx | sentence-transformers |
| Validation | Active | 473 | validate.py, csv_validator.py | IssueReview.tsx | pandas, re |
| Transform | Active | 443 | transform.py, transformer.py, xml_transformer.py | PreviewCSV.tsx, PreviewXML.tsx | pandas, xml.etree |
| Export | Active | 430 | transform.py (export endpoints) | PreviewCSV/XML.tsx | fastapi, io.StringIO |
| SFTP | Active | 464 | sftp.py, sftp_manager.py | SFTPCredentialManager.tsx | paramiko, json |
| Enhancement | Planned | 403 | NOT IMPLEMENTED | NOT IMPLEMENTED | prometheus, grafana |

---

## File Structure

```
C:\Code\SnapMap\
├── .claude\
│   ├── FEATURE_TEMPLATE.md          (344 lines - Standard template)
│   ├── MAIN_AGENT.md                (Existing - Main Orchestrator)
│   ├── AGENT_INTERACTION_PROTOCOL.md (Existing - Communication protocol)
│   └── AGENT_DOCUMENTATION_INDEX.md (This file - Index)
│
├── features\
│   ├── upload\
│   │   └── AGENT.md                 (428 lines - Upload Agent)
│   ├── mapping\
│   │   └── AGENT.md                 (450 lines - Mapping Agent)
│   ├── validation\
│   │   └── AGENT.md                 (473 lines - Validation Agent)
│   ├── transform\
│   │   └── AGENT.md                 (443 lines - Transform Agent)
│   ├── export\
│   │   └── AGENT.md                 (430 lines - Export Agent)
│   ├── sftp\
│   │   └── AGENT.md                 (464 lines - SFTP Agent)
│   └── enhancement\
│       └── AGENT.md                 (403 lines - Enhancement Agent - PLANNED)
│
├── backend\
│   └── app\
│       ├── api\endpoints\           (API endpoints)
│       ├── services\                (Business logic)
│       ├── models\                  (Pydantic models)
│       └── schemas\                 (Entity schemas)
│
└── frontend\
    └── src\
        ├── components\              (React components)
        └── services\                (API clients)
```

---

## Quick Reference

### Agent-to-Agent Dependencies

```
User Request
    ↓
Main Orchestrator
    ↓
Upload Agent (parse file)
    ↓
Mapping Agent (auto-map fields)
    ↓
Validation Agent (validate data)
    ↓
Transform Agent (transform data)
    ↓
Export Agent (generate file)
    ↓
SFTP Agent (upload file)
    ↓
Enhancement Agent (monitor health) [PLANNED]
```

### Performance Targets Summary

| Agent | Target Response Time | Throughput |
|-------|---------------------|------------|
| Upload | <2s (100MB files) | 10 concurrent |
| Mapping | <5s (50 fields) | 20 concurrent |
| Validation | <10s (10K rows) | 15 concurrent |
| Transform | <3s (10K rows) | 20 concurrent |
| Export | <5s (10K rows) | 25 concurrent |
| SFTP | <10s (10MB files) | 5 concurrent |
| Enhancement | <1s (health check) | N/A |

---

## Known Issues & Technical Debt

### Critical
1. **SFTP Password Storage**: Base64 encoding is NOT secure - must implement proper encryption before production
2. **SFTP Explorer Backend**: UI exists but backend APIs not implemented

### High Priority
1. **Entity Type Support**: Only Employee entity type fully tested (16 schemas exist)
2. **User Feedback Learning**: Mapping accuracy doesn't improve from user corrections
3. **Business Logic Validation**: No cross-field validation rules

### Medium Priority
1. **Transformation Templates**: Users can't save/reuse mappings and transformations
2. **Batch Processing**: No support for processing multiple files at once
3. **SSH Key Authentication**: SFTP only supports password auth

### Low Priority
1. **File Compression**: Large exports not compressed
2. **Streaming Upload**: Files >100MB not supported
3. **Custom Validation Rules**: Users can't define their own validators

---

## Next Steps for Development

1. **Implement proper SFTP password encryption** (CRITICAL - before production)
2. **Test all 16 entity types** (currently only Employee tested)
3. **Implement SFTP Explorer backend APIs**
4. **Add transformation templates** (save/reuse mappings)
5. **Implement Enhancement Agent** (when system reaches production scale)
6. **Add user feedback learning** to Mapping Agent
7. **Implement business logic validation** rules
8. **Add batch file processing** support

---

## Maintenance Schedule

### Weekly
- Review error logs from all agents
- Check performance metrics against SLAs
- Update agent documentation for any code changes

### Monthly
- Review and prioritize technical debt items
- Update agent capabilities documentation
- Rebuild semantic embeddings if schemas changed

### Quarterly
- Full integration testing of all agent pipelines
- Performance optimization review
- Security audit (especially SFTP password storage)

---

## Version History

### Version 1.0.0 (2025-11-06)
- Created comprehensive agent documentation for all 7 feature areas
- Established FEATURE_TEMPLATE as standard
- Documented Upload, Mapping, Validation, Transform, Export, SFTP agents
- Created Enhancement Agent template (planned implementation)
- Total: 3,435 lines of agent documentation
- Based documentation on actual codebase implementation

---

## Contact & Support

**Documentation Owner**: SnapMap Core Team
**Last Updated**: 2025-11-06
**Questions**: Refer to individual agent AGENT.md files for specific questions
**Main Orchestrator**: See `.claude/MAIN_AGENT.md`
**Communication Protocol**: See `.claude/AGENT_INTERACTION_PROTOCOL.md`

---

**Note**: This documentation is based on the actual SnapMap codebase implementation as of 2025-11-06. All line numbers and file paths are verified against the current code. As the system evolves, keep this documentation updated by following the maintenance schedule.
