# Feature Agent Template

## Version 1.0.0 | Last Updated: [DATE]

---

## Agent Identity

**Name**: [Agent Name]
**Version**: [X.Y.Z]
**Status**: [Active | Development | Planned | Deprecated]
**Owner**: [Team/Individual Name]
**Domain**: [Feature Area]
**Location**: `features/[feature-name]/AGENT.md`

---

## 1. Role & Responsibilities

### Primary Responsibilities

1. **[Responsibility 1]**: [Description]
2. **[Responsibility 2]**: [Description]
3. **[Responsibility 3]**: [Description]

### Data Sources

- **[Source 1]**: [Description]
- **[Source 2]**: [Description]
- **[Source 3]**: [Description]

### Success Criteria

- **[Metric 1]**: [Target value]
- **[Metric 2]**: [Target value]
- **[Metric 3]**: [Target value]

---

## 2. Feature Capabilities

### What This Agent CAN Do

1. **[Capability 1]**: [Detailed description]
2. **[Capability 2]**: [Detailed description]
3. **[Capability 3]**: [Detailed description]
4. **[Capability 4]**: [Detailed description]
5. **[Capability 5]**: [Detailed description]

### What This Agent CANNOT Do

1. **[Limitation 1]**: [Reason why not]
2. **[Limitation 2]**: [Reason why not]
3. **[Limitation 3]**: [Reason why not]
4. **[Limitation 4]**: [Reason why not]

---

## 3. Dependencies

### Required Dependencies

- **[Dependency 1]**: [Purpose] - [Location/Package]
- **[Dependency 2]**: [Purpose] - [Location/Package]
- **[Dependency 3]**: [Purpose] - [Location/Package]

### Optional Dependencies

- **[Optional 1]**: [Purpose] - [Fallback behavior]
- **[Optional 2]**: [Purpose] - [Fallback behavior]

### External Services

- **[Service 1]**: [Purpose, connection details]
- **[Service 2]**: [Purpose, connection details]

---

## 4. Architecture & Implementation

### Key Files & Code Locations

#### Backend
- **API Endpoints**: `backend/app/api/endpoints/[feature].py` (Lines X-Y)
  - `[endpoint_1]`: [Purpose]
  - `[endpoint_2]`: [Purpose]

- **Services**: `backend/app/services/[feature]_service.py` (Lines X-Y)
  - `[function_1]`: [Purpose]
  - `[function_2]`: [Purpose]

- **Models**: `backend/app/models/[feature].py` (Lines X-Y)
  - `[Model1]`: [Purpose]
  - `[Model2]`: [Purpose]

#### Frontend
- **Components**: `frontend/src/components/[feature]/[Component].tsx`
  - `[Component1]`: [Purpose] (Lines X-Y)
  - `[Component2]`: [Purpose] (Lines X-Y)

- **API Client**: `frontend/src/services/api.ts`
  - `[apiFunction1]`: [Purpose] (Lines X-Y)

### Current State

#### Implemented Features
- [x] [Feature 1]
- [x] [Feature 2]
- [x] [Feature 3]

#### In Progress
- [ ] [Feature 4]: [Status/Blockers]
- [ ] [Feature 5]: [Status/Blockers]

#### Planned
- [ ] [Feature 6]: [Priority, expected timeline]
- [ ] [Feature 7]: [Priority, expected timeline]

---

## 5. Communication Patterns

### Incoming Requests (FROM)

**Main Orchestrator**
- **Action**: `[action_name]`
- **Payload**: `{ [field]: [type], ... }`
- **Response**: `{ [field]: [type], ... }`

**[Other Agent Name]**
- **Action**: `[action_name]`
- **Payload**: `{ [field]: [type], ... }`
- **Response**: `{ [field]: [type], ... }`

### Outgoing Requests (TO)

**[Target Agent 1]**
- **Action**: `[action_name]`
- **Purpose**: [Why this agent needs this data]
- **Frequency**: [Always | Sometimes | Rarely]

**[Target Agent 2]**
- **Action**: `[action_name]`
- **Purpose**: [Why this agent needs this data]
- **Frequency**: [Always | Sometimes | Rarely]

### Data Flow Diagram

```
┌────────────────┐
│  [Input From]  │
└────────┬───────┘
         │
         ↓
┌────────────────────────┐
│  [This Agent]          │
│  - [Process 1]         │
│  - [Process 2]         │
│  - [Process 3]         │
└────────┬───────────────┘
         │
         ↓
┌────────────────┐
│ [Output To]    │
└────────────────┘
```

---

## 6. Error Handling

### Common Errors

| Error Code | Severity | Description | Recovery |
|------------|----------|-------------|----------|
| `[ERROR_CODE_1]` | Critical | [What causes this] | [How to fix] |
| `[ERROR_CODE_2]` | Warning | [What causes this] | [How to fix] |
| `[ERROR_CODE_3]` | Info | [What causes this] | [How to fix] |

### Error Response Format

```json
{
  "status": "error",
  "errors": [
    {
      "code": "[ERROR_CODE]",
      "message": "[Human-readable message]",
      "severity": "[critical|warning|info]",
      "field": "[affected field]",
      "row": "[affected row if applicable]",
      "recovery_suggestion": "[How to fix]"
    }
  ]
}
```

### Validation Rules

1. **[Rule 1]**: [Description]
   - **Severity**: [Critical | Warning | Info]
   - **Action**: [What happens if violated]

2. **[Rule 2]**: [Description]
   - **Severity**: [Critical | Warning | Info]
   - **Action**: [What happens if violated]

---

## 7. Performance Considerations

### Performance Targets

- **Response Time**: [Target] ms
- **Throughput**: [Target] requests/sec
- **Memory Usage**: Max [X] MB
- **CPU Usage**: Max [X]% of single core

### Optimization Strategies

1. **[Strategy 1]**: [How it improves performance]
2. **[Strategy 2]**: [How it improves performance]
3. **[Strategy 3]**: [How it improves performance]

### Bottlenecks & Limitations

- **[Bottleneck 1]**: [Description, impact, mitigation]
- **[Bottleneck 2]**: [Description, impact, mitigation]

---

## 8. Testing Checklist

### Unit Tests
- [ ] [Test case 1]
- [ ] [Test case 2]
- [ ] [Test case 3]

### Integration Tests
- [ ] [Integration test 1]
- [ ] [Integration test 2]
- [ ] [Integration test 3]

### Edge Cases
- [ ] [Edge case 1]
- [ ] [Edge case 2]
- [ ] [Edge case 3]

### Performance Tests
- [ ] Test with [X] rows
- [ ] Test with [Y] concurrent users
- [ ] Test error handling under load

---

## 9. Maintenance

### When to Update This Document

- New features are added to this agent
- Dependencies change
- Error handling patterns change
- Performance characteristics change
- API contracts change

### Monitoring Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| [Metric 1] | [Target] | [When to alert] |
| [Metric 2] | [Target] | [When to alert] |
| [Metric 3] | [Target] | [When to alert] |

### Health Check Endpoint

**Endpoint**: `[health check URL]`
**Expected Response**:
```json
{
  "status": "healthy",
  "version": "X.Y.Z",
  "dependencies": {
    "[dep1]": "ok",
    "[dep2]": "ok"
  }
}
```

---

## 10. Integration Points

### With Other Agents

| Agent | Integration Type | Data Exchanged |
|-------|------------------|----------------|
| [Agent 1] | [Request/Response] | [Data description] |
| [Agent 2] | [Event-based] | [Data description] |
| [Agent 3] | [Batch] | [Data description] |

### With External Systems

- **[System 1]**: [Purpose, authentication method]
- **[System 2]**: [Purpose, authentication method]

---

## 11. Questions This Agent Can Answer

1. "[Example question 1]"
2. "[Example question 2]"
3. "[Example question 3]"
4. "[Example question 4]"
5. "[Example question 5]"

---

## 12. Questions This Agent CANNOT Answer

1. "[Out of scope question 1]" - [Why/Which agent can answer]
2. "[Out of scope question 2]" - [Why/Which agent can answer]
3. "[Out of scope question 3]" - [Why/Which agent can answer]

---

## Version History

### Version X.Y.Z ([DATE])
- [Change 1]
- [Change 2]
- [Change 3]

### Version X.Y.Z-1 ([DATE])
- [Change 1]
- [Change 2]

---

## Notes & Assumptions

- **[Assumption 1]**: [Description]
- **[Assumption 2]**: [Description]
- **[Known Issue 1]**: [Description, workaround]
- **[Technical Debt 1]**: [Description, plan to resolve]
