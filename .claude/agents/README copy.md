# Claude Code Agents - Wheel Strategy Project

This directory contains specialized agent definitions for the Wheel Strategy trading platform. Each agent is a focused expert that can be invoked to help with specific tasks.

## Agent Directory

### Quality & Testing
- **[qa-tester.md](qa-tester.md)** - Quality assurance and testing (MANDATORY before delivery)
- **[code-reviewer.md](code-reviewer.md)** - Code quality and best practices review

### Architecture & Design
- **[architect.md](architect.md)** - System architecture and design planning

### Development (Coming Soon)
- **python-expert.md** - Python code implementation and optimization
- **database-expert.md** - Database design and query optimization
- **frontend-expert.md** - Streamlit UI development

### Specialized (Coming Soon)
- **performance-expert.md** - Performance profiling and optimization
- **security-expert.md** - Security audit and hardening
- **error-detective.md** - Bug investigation and debugging

## How to Use Agents

### Manual Invocation

When you need an agent, invoke it like this:

```
"Use the QA Tester agent to test the changes in dashboard.py"

"Have the Code Reviewer agent review the new premium scanner feature"

"Ask the Architect agent to design the real-time alert system"
```

### Automatic Workflows

Agents are automatically invoked in standard workflows:

**Bug Fix Workflow**:
1. Error Detective → identifies root cause
2. Python Expert → implements fix
3. QA Tester → verifies fix (MANDATORY)
4. Code Reviewer → quality check

**New Feature Workflow**:
1. Architect → designs solution
2. Python Expert / Frontend Expert → implement
3. Database Expert → handles schema (if needed)
4. QA Tester → comprehensive testing (MANDATORY)
5. Code Reviewer → final review

**Optimization Workflow**:
1. Performance Expert → profiles and identifies bottlenecks
2. Database Expert → optimizes queries
3. Python Expert → implements improvements
4. QA Tester → verifies improvements (MANDATORY)

## Agent Principles

### The Golden Rule
**NEVER deliver code without QA Tester approval**

Every code change must pass through the QA Tester agent before reaching the user.

### Agent Responsibilities

Each agent:
- Has a specific domain of expertise
- Provides structured output
- Follows defined protocols
- Maintains high standards
- Coordinates with other agents

### Quality Gates

**Mandatory Gates** (Must Pass):
1. ✅ QA Tester approval (for ALL code changes)
2. ✅ Code Reviewer approval (for major features)
3. ✅ Architect approval (for system changes)

**Optional Gates** (Recommended):
- Performance Expert review (for critical paths)
- Security Expert review (for sensitive code)

## Agent Communication

Agents can reference each other:

```markdown
**QA Tester** → "Found security concern, recommend Security Expert review"

**Architect** → "Design complete, ready for Python Expert implementation"

**Code Reviewer** → "Performance concern detected, suggest Performance Expert analysis"
```

## Creating New Agents

To add a new agent:

1. Create `[agent-name].md` in this directory
2. Follow the standard template:
   - Role & Priority
   - Mission
   - Responsibilities
   - Process/Checklist
   - Report Format
   - When to Invoke
3. Add to README.md directory
4. Document in AGENT_WORKFLOW_SPEC.md

### Agent Template

```markdown
# [Agent Name]

**Role**: [Primary function]
**Priority**: CRITICAL/HIGH/MEDIUM/LOW

## Mission
[What this agent does]

## Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]

## Process
[Step-by-step workflow]

## Report Format
[Expected output structure]

## When to Invoke
- ✅ [Scenario 1]
- ✅ [Scenario 2]

## Example
[Concrete usage example]
```

## Best Practices

### For Users
1. **Be specific** - Tell agents exactly what you need
2. **Provide context** - Share relevant files, errors, requirements
3. **Trust the process** - Agents follow proven workflows
4. **Review outputs** - Agents advise, you decide

### For Agents
1. **Stay focused** - Stick to your domain
2. **Be thorough** - Follow your checklist
3. **Be clear** - Provide actionable feedback
4. **Collaborate** - Recommend other agents when needed

## Workflow Integration

### Standard Development Cycle

```
User Request
    ↓
[Architect] Plans solution (if complex)
    ↓
[Python/Frontend/Database Expert] Implements
    ↓
[QA Tester] Tests (MANDATORY)
    ↓
[Code Reviewer] Reviews quality
    ↓
Delivery to User
    ↓
[Performance Expert] Monitors (optional)
```

### Emergency Debugging

```
Production Issue
    ↓
[Error Detective] Identifies root cause
    ↓
[Python Expert] Implements hotfix
    ↓
[QA Tester] Fast-track testing
    ↓
[Code Reviewer] Post-deployment review
```

## Agent Statistics

- **Total Agents**: 3 (active), 6 (planned)
- **Mandatory Agents**: QA Tester
- **Coverage**: Development, Testing, Review, Architecture
- **Success Rate**: Tracked per agent in execution history

## Contributing

To improve agents:
1. Test the agent workflow
2. Identify gaps or inefficiencies
3. Propose improvements
4. Update agent definitions
5. Document changes

---

**Last Updated**: 2025-10-27
**Version**: 1.0
**Status**: Active Development

**Remember**: Agents work best when given clear instructions and sufficient context!
