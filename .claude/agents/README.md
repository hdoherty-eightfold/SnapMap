# Claude Agents System
## ETL UI - HR Data Transformation Tool

This folder contains the multi-agent system for the ETL UI project. Each agent is a specialist in their respective module and can be called upon for specific workflows.

## Agent Architecture

### Main Coordinator Agent
**File**: [MAIN_AGENT.md](MAIN_AGENT.md)

The Main Coordinator Agent orchestrates all feature-specific agents and ensures successful integration across modules. It:
- Understands the full system architecture
- Routes requests to appropriate specialist agents
- Coordinates multi-module changes
- Maintains system integrity
- Provides high-level guidance

**When to use**: For tasks that span multiple modules, architectural questions, or general project guidance.

### Feature-Specific Agents

#### 1. Frontend Core Agent
**File**: [MODULE_1_FRONTEND_CORE_AGENT.md](MODULE_1_FRONTEND_CORE_AGENT.md)
**Specialization**: Core UI components, file upload, data preview, export UI
**Owns**:
- `frontend/src/components/upload/FileUpload.tsx`
- `frontend/src/components/preview/DataPreview.tsx`
- `frontend/src/components/export/TransformPreview.tsx`
- `frontend/src/contexts/AppContext.tsx`
- `frontend/src/services/api.ts`

**When to use**: File upload issues, preview components, export UI, global state management, API client changes.

#### 2. Mapping Engine Agent
**File**: [MODULE_2_MAPPING_ENGINE_AGENT.md](MODULE_2_MAPPING_ENGINE_AGENT.md)
**Specialization**: Field mapping interface, visual feedback, manual mapping UX
**Owns**:
- `frontend/src/components/mapping/FieldMapping.tsx`
- Mapping UI/UX logic
- Confidence score visualization

**When to use**: Mapping interface improvements, visual enhancements, manual mapping workflow, confidence display issues.

#### 3. Transformation Engine Agent
**File**: [MODULE_3_TRANSFORMATION_ENGINE_AGENT.md](MODULE_3_TRANSFORMATION_ENGINE_AGENT.md)
**Specialization**: Data transformation pipeline, validation, export backend
**Owns**:
- `backend/app/services/transformer.py`
- `backend/app/services/validator.py`
- `backend/app/services/file_parser.py`
- `backend/app/api/endpoints/transform.py`
- `backend/app/api/endpoints/validate.py`
- `backend/app/api/endpoints/upload.py`

**When to use**: Transformation logic, date conversion, validation rules, CSV export, file parsing.

#### 4. Schema & Auto-Mapping Agent
**File**: [MODULE_4_SCHEMA_AUTOMAPPING_AGENT.md](MODULE_4_SCHEMA_AUTOMAPPING_AGENT.md)
**Specialization**: Auto-mapping algorithm, schema management, fuzzy matching
**Owns**:
- `backend/app/services/field_mapper.py` ⭐ (Core algorithm)
- `backend/app/services/schema_manager.py`
- `backend/app/schemas/employee_schema.json`
- `backend/app/schemas/field_aliases.json`
- `backend/app/api/endpoints/automapping.py`
- `backend/app/api/endpoints/schema.py`

**When to use**: Auto-mapping accuracy, schema changes, alias updates, fuzzy matching improvements, confidence scoring.

## How to Use the Agents

### Single-Module Tasks
For tasks affecting only one module, delegate directly to the specialist agent:

**Example**: "Improve the file upload UI to show upload progress"
→ Delegate to **FRONTEND_CORE_AGENT**

**Example**: "Add a new transformation rule to convert phone numbers"
→ Delegate to **TRANSFORMATION_AGENT**

**Example**: "Update the schema to include a new DEPARTMENT field"
→ Delegate to **SCHEMA_AUTOMAPPING_AGENT**

### Multi-Module Tasks
For tasks affecting multiple modules, coordinate through the Main Agent:

**Example**: "Add a new field and ensure it flows through the entire pipeline"
1. **MAIN_AGENT** coordinates
2. **SCHEMA_AUTOMAPPING_AGENT** updates schema and aliases
3. **TRANSFORMATION_AGENT** adds transformation rules if needed
4. **MAPPING_ENGINE_AGENT** verifies UI displays new field
5. **FRONTEND_CORE_AGENT** updates TypeScript types

### Integration Tasks
For tasks requiring API contract changes:

**Example**: "Change the auto-map API to return additional metadata"
1. **MAIN_AGENT** coordinates
2. **SCHEMA_AUTOMAPPING_AGENT** updates backend endpoint
3. **FRONTEND_CORE_AGENT** updates API client and TypeScript types
4. **MAPPING_ENGINE_AGENT** updates UI to display new metadata

## Agent Communication Protocol

When one agent needs to coordinate with another:

```markdown
@[TARGET_AGENT_NAME]
Task: [Clear description of what needs to be done]
Context: [Why this is needed, user's goal]
Scope: [Which files/components need changes]
Integration Points: [What other modules are affected]
Testing: [How to verify it works]
Dependencies: [What needs to happen first]
```

Example:
```markdown
@TRANSFORMATION_AGENT
Task: Add validation for phone number format (XXX-XXX-XXXX)
Context: User wants to ensure phone numbers are properly formatted
Scope: Update validator.py to add phone number regex validation
Integration Points: Validation results displayed in FieldMapping.tsx
Testing: Upload file with various phone formats, verify validation messages appear
Dependencies: None
```

## Workflow Integration

The agents map directly to the 4-step user workflow:

| Workflow Step | Primary Agent | Supporting Agents |
|---------------|---------------|-------------------|
| **Step 0: Upload** | Frontend Core Agent | Transformation Agent (upload endpoint) |
| **Step 1: Map Fields** | Mapping Engine Agent | Schema & Auto-Mapping Agent |
| **Step 2: Preview** | Frontend Core Agent | Transformation Agent (preview endpoint) |
| **Step 3: Export** | Frontend Core Agent | Transformation Agent (export endpoint) |

## Quick Reference

### Frontend Issues → Frontend Core Agent
- File upload problems
- Styling/layout issues
- State management
- API client errors
- TypeScript type errors

### Mapping UI → Mapping Engine Agent
- Mapping interface UX
- Visual feedback
- Confidence scores
- Manual mapping interaction

### Data Processing → Transformation Agent
- Transformation logic
- Validation rules
- Date/format conversion
- CSV export
- File parsing

### Auto-Mapping → Schema & Auto-Mapping Agent
- Mapping accuracy
- Algorithm improvements
- Schema changes
- Alias dictionary updates
- Fuzzy matching

### Cross-Cutting → Main Agent
- Architecture changes
- Multi-module features
- Integration issues
- Performance optimization
- End-to-end workflow

## Testing the Agent System

To verify the agents work correctly:

1. **Isolated Module Test**: Ask an agent to make a change within its scope
   - Example: "Add a loading spinner to the upload button" → Frontend Core Agent

2. **Integration Test**: Ask Main Agent to coordinate a multi-module change
   - Example: "Add support for a new file format (JSON)" → Main Agent coordinates all agents

3. **Cross-Agent Communication**: Verify agents can request help from each other
   - Example: Mapping Engine Agent requests schema change from Schema Agent

## Agent Maintenance

### When to Update Agents

Update agent specifications when:
- New files are added to their scope
- API contracts change
- New integration points are created
- Responsibilities shift between modules
- New features are added

### Agent Version Control

All agent files are versioned with the project. When making significant changes:
1. Document the change in the agent file
2. Update integration points in Main Agent
3. Test affected workflows
4. Update this README if agent responsibilities change

## Best Practices

1. **Use the Right Agent**: Choose the specialist agent for specific tasks
2. **Coordinate Early**: Involve Main Agent for multi-module changes
3. **Document Integration**: Keep integration points clear
4. **Test End-to-End**: Verify changes work across the full workflow
5. **Update Promptly**: Keep agent specs current with code changes

## Current Project Status

✅ **All Modules Complete** - 100%
- Backend: All 5 API endpoints working
- Frontend: All 4 workflow steps implemented
- Auto-mapping: 3-tier algorithm achieving target accuracy
- Integration: Full end-to-end workflow functional

**Ready to Run**:
```bash
# Terminal 1
cd backend && uvicorn main:app --reload

# Terminal 2
cd frontend && npm run dev
```

Access at: http://localhost:5173

---

## Need Help?

- **General questions**: Start with Main Agent
- **Specific module**: Go directly to the specialist agent
- **Bug fixes**: Identify affected module(s) and delegate accordingly
- **New features**: Discuss with Main Agent for scoping and delegation
