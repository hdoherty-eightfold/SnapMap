# SnapMap Agent Interaction Protocol

## Version 1.0.0 | Last Updated: 2025-11-06

## Purpose

This document defines the **standardized communication protocol** for all agents in the SnapMap HR Data Transformation Platform. Following this protocol ensures consistency, maintainability, and seamless collaboration between agents.

---

## Protocol Overview

### Core Principles

1. **Single Responsibility**: Each agent owns a specific domain
2. **Central Coordination**: All inter-agent communication flows through Main Orchestrator
3. **Stateless Communication**: Agents don't maintain state about other agents
4. **Documentation-First**: Changes to capabilities must update agent documentation
5. **Error Transparency**: All errors must be reported with actionable recovery steps

---

## Standard Agent Greeting

When an agent is invoked, it must identify itself using this format:

```markdown
🤖 **[AGENT NAME]**
📋 **Domain**: [Feature/Technical Domain]
📂 **Location**: [File path]
📊 **Status**: [Active | Development | Deprecated]

**Capabilities**:
✓ [Key capability 1]
✓ [Key capability 2]
✓ [Key capability 3]

**Dependencies**:
→ [Required agent/service 1]
→ [Required agent/service 2]

Ready to assist with [brief description of what this agent does].
```

### Example

```markdown
🤖 **Upload Agent**
📋 **Domain**: File Upload & Parsing
📂 **Location**: features/upload/AGENT.md
📊 **Status**: Active

**Capabilities**:
✓ Parse CSV and Excel files
✓ Detect entity types automatically
✓ Store files in temporary storage

**Dependencies**:
→ ChromaDB (entity detection)
→ Pandas (file parsing)

Ready to assist with file upload and entity detection.
```

---

## Communication Flow

### Pattern 1: User → Main Agent → Feature Agent

```
┌──────┐
│ User │ Makes request
└───┬──┘
    │
    ↓
┌─────────────────┐
│  Main Agent     │ Analyzes request
│                 │ Determines which feature agent to invoke
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Feature Agent  │ Executes task
│                 │ Returns structured response
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Main Agent     │ Aggregates results
│                 │ Formats response
└────────┬────────┘
         │
         ↓
┌──────┐
│ User │ Receives response
└──────┘
```

### Pattern 2: Feature Agent → Main Agent → Another Feature Agent

```
┌──────────────────┐
│  Feature Agent A │ Needs data from Feature Agent B
└────────┬─────────┘
         │
         ↓ Request via Main Agent
┌─────────────────┐
│  Main Agent     │ Routes request
└────────┬────────┘
         │
         ↓
┌──────────────────┐
│  Feature Agent B │ Provides data
└────────┬─────────┘
         │
         ↓ Response via Main Agent
┌─────────────────┐
│  Main Agent     │ Delivers data
└────────┬────────┘
         │
         ↓
┌──────────────────┐
│  Feature Agent A │ Continues processing
└──────────────────┘
```

**Key Rule**: Feature agents NEVER communicate directly with each other.

---

## Request/Response Format

### Standard Request Structure

```json
{
  "request_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "source_agent": "agent-name",
  "target_agent": "agent-name",
  "action": "action-verb",
  "payload": {
    // Action-specific data
  },
  "context": {
    "file_id": "optional-file-id",
    "session_id": "optional-session-id",
    "user_id": "optional-user-id"
  }
}
```

### Standard Response Structure

```json
{
  "request_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "source_agent": "agent-name",
  "status": "success | error | warning",
  "data": {
    // Response data
  },
  "errors": [
    {
      "code": "ERROR_CODE",
      "message": "Human-readable error",
      "severity": "critical | warning | info",
      "recovery_suggestion": "How to fix"
    }
  ],
  "metadata": {
    "processing_time_ms": 123,
    "rows_processed": 1000
  }
}
```

---

## Agent Handoff Protocol

When one agent completes its work and another agent needs to continue, use this handoff format:

```markdown
### 🔄 Agent Handoff

**From**: [Source Agent Name]
**To**: [Target Agent Name]
**Timestamp**: [ISO-8601]

**Context**:
- What was accomplished
- Current state of data
- Any warnings or notes

**Deliverables**:
- file_id: abc123
- mappings: [list of mappings]
- validation_report: [link or summary]

**Action Required**:
- [What the next agent should do]
- [Any special considerations]

**Priority**: High | Medium | Low

**Estimated Effort**: [time estimate]
```

### Example

```markdown
### 🔄 Agent Handoff

**From**: Upload Agent
**To**: Mapping Agent
**Timestamp**: 2025-11-06T14:23:15Z

**Context**:
- Successfully uploaded employee_data.csv (5,234 rows)
- Detected entity type: Employee (95% confidence)
- No parsing errors

**Deliverables**:
- file_id: abc123-def456
- entity_type: employee
- columns: ['emp_id', 'first_name', 'last_name', 'email', 'hire_date']

**Action Required**:
- Generate semantic field mappings for all 5 columns
- Target schema: Employee (11 fields)

**Priority**: High

**Estimated Effort**: <5 seconds
```

---

## Error Handling Protocol

### Error Classification

| Severity | Description | Action |
|----------|-------------|--------|
| **Critical** | System cannot continue | Block pipeline, return error to user |
| **Warning** | Can continue with degraded functionality | Log warning, continue processing |
| **Info** | Informational message | Log for audit, continue normally |

### Error Response Format

```json
{
  "status": "error",
  "errors": [
    {
      "code": "UPLOAD_FILE_TOO_LARGE",
      "message": "File size 150MB exceeds maximum 100MB",
      "severity": "critical",
      "field": "file",
      "row": null,
      "recovery_suggestion": "Reduce file size or split into multiple files",
      "documentation_link": "https://docs.snapmap.com/errors/UPLOAD_FILE_TOO_LARGE"
    }
  ]
}
```

### Common Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| `UPLOAD_FILE_TOO_LARGE` | Critical | File exceeds size limit |
| `UPLOAD_INVALID_FORMAT` | Critical | Unsupported file format |
| `MAPPING_LOW_CONFIDENCE` | Warning | Field mapping confidence <70% |
| `VALIDATION_MISSING_REQUIRED` | Critical | Required field missing |
| `VALIDATION_INVALID_FORMAT` | Warning | Data format issue |
| `TRANSFORM_DATA_LOSS` | Critical | Data would be lost in transformation |
| `EXPORT_ENCODING_ERROR` | Warning | Character encoding issue |
| `SFTP_CONNECTION_FAILED` | Critical | Cannot connect to SFTP server |

---

## Documentation Update Protocol

### When to Update Agent Documentation

Every agent must update its `AGENT.md` file when:

1. **New capabilities are added**
   ```markdown
   ## Capabilities (Updated: 2025-11-06)
   ✅ What This Agent CAN Do
   + NEW: Support for Excel 2007+ format (.xlsx)
   ```

2. **Limitations change**
   ```markdown
   ❌ What This Agent CANNOT Do
   - REMOVED: Cannot parse .xlsx files (now supported)
   ```

3. **Dependencies change**
   ```markdown
   ## Dependencies (Updated: 2025-11-06)
   + Added: openpyxl library for Excel support
   ```

4. **Error handling changes**
   ```markdown
   ## Error Handling (Updated: 2025-11-06)
   + NEW: Handle Excel sheet selection errors
   ```

### Documentation Commit Message Format

```
[AGENT-UPDATE] [Agent Name] - Brief description

- Added: [new capability]
- Updated: [changed behavior]
- Fixed: [bug fix]
- Removed: [deprecated feature]

Affects: [list of dependent agents]
Breaking: Yes/No
```

---

## Quality Gates

### Before Agent Handoff

Every agent must verify before handing off:

- [ ] Output data is valid and complete
- [ ] All errors are properly structured
- [ ] Context is sufficient for next agent
- [ ] Documentation is up-to-date
- [ ] Logs are written for audit trail

### Before User Response

Main Agent must verify before responding to user:

- [ ] All pipeline stages completed successfully
- [ ] Errors are aggregated and formatted
- [ ] Response time is within SLA
- [ ] User-facing messages are clear
- [ ] Next steps are provided

---

## Testing Protocol

### Agent Integration Testing

Every agent must pass these tests before deployment:

1. **Successful Path**: Agent completes task successfully
2. **Error Path**: Agent handles errors gracefully
3. **Timeout Path**: Agent handles timeouts
4. **Handoff Path**: Next agent receives valid data
5. **Rollback Path**: Agent can undo changes if needed

### Test Template

```python
def test_agent_successful_path():
    """Test agent completes task successfully"""
    request = create_test_request()
    response = agent.execute(request)
    assert response.status == "success"
    assert response.data is not None

def test_agent_error_path():
    """Test agent handles errors gracefully"""
    request = create_invalid_request()
    response = agent.execute(request)
    assert response.status == "error"
    assert len(response.errors) > 0
    assert response.errors[0].recovery_suggestion is not None
```

---

## Performance SLAs

### Response Time Targets

| Agent | Target | Max |
|-------|--------|-----|
| Upload Agent | <2s | 5s |
| Mapping Agent | <3s | 10s |
| Validation Agent | <5s | 15s |
| Transform Agent | <3s | 10s |
| Export Agent | <5s | 15s |
| SFTP Agent | <10s | 30s |
| Main Agent (coordination) | <1s | 2s |

### Resource Limits

- **Memory**: Max 500MB per agent
- **CPU**: Max 50% of single core
- **File Size**: Max 100MB
- **Concurrent Requests**: Max 10 per agent

---

## Monitoring & Observability

### Required Metrics

Every agent must emit:

1. **Request Count**: Total requests processed
2. **Success Rate**: % of successful requests
3. **Error Rate**: % of failed requests
4. **Average Response Time**: Mean processing time
5. **P95 Response Time**: 95th percentile
6. **Active Requests**: Current in-flight requests

### Logging Format

```json
{
  "timestamp": "2025-11-06T14:23:15Z",
  "level": "INFO",
  "agent": "upload-agent",
  "request_id": "abc123",
  "action": "parse_file",
  "duration_ms": 1234,
  "status": "success",
  "metadata": {
    "file_size": 5234567,
    "rows": 10000
  }
}
```

---

## Version History

### Version 1.0.0 (2025-11-06)
- Initial protocol definition
- Standard greeting format
- Request/response structures
- Error handling protocol
- Documentation update protocol
- Quality gates
- Performance SLAs
