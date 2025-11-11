# SnapMap Feature Orchestrator Agent

## Overview
Main coordination agent that manages interactions between feature modules and maintains system integrity during updates and development.

## Feature Modules
1. **[Upload](./upload/SPEC.md)** - File upload and processing
2. **[Review](./review/SPEC.md)** - Data quality analysis
3. **[Mapping](./mapping/SPEC.md)** - AI-powered field mapping
4. **[Export](./export/SPEC.md)** - Multi-format data export
5. **[SFTP](./sftp/SPEC.md)** - Secure file upload integration
6. **[Settings](./settings/SPEC.md)** - Application configuration
7. **[Layout](./layout/SPEC.md)** - UI navigation and framework

## Inter-Feature Dependencies

### Data Flow
```
Upload → Review → Mapping → Export → SFTP
   ↓       ↓        ↓        ↓       ↓
Settings ← Layout (provides UI for all steps)
```

### Critical Integration Points
1. **Upload → Review**: File metadata and content validation
2. **Review → Mapping**: Data quality metrics inform mapping confidence
3. **Mapping → Export**: Field mappings define transformation rules
4. **Export → SFTP**: Transformed files ready for upload
5. **Settings → All**: Configuration affects all feature behaviors

## Change Management Protocol

### Before Making Changes
1. **Impact Assessment**: Check feature dependencies in this document
2. **API Compatibility**: Ensure backward compatibility of shared APIs
3. **State Management**: Verify global state changes don't break other features
4. **Testing Requirements**: Run affected feature tests

### Safe Update Guidelines
- **Upload Changes**: Test impact on Review data quality analysis
- **Mapping Changes**: Verify Export transformation accuracy
- **Export Changes**: Ensure SFTP receives correct file formats
- **Settings Changes**: Test all features with new configuration options
- **Layout Changes**: Verify all features render correctly in new UI

### Feature Communication
Each feature exposes a standard interface:
- **Status API**: Health check and readiness status
- **Configuration**: Feature-specific settings schema
- **Events**: Success/error/progress events
- **Dependencies**: Required services and data

## Testing Strategy
- **Unit Tests**: Per-feature component testing
- **Integration Tests**: Cross-feature workflow validation
- **E2E Tests**: Complete user journey verification
- **Regression Tests**: Ensure changes don't break existing functionality

## Performance Monitoring
- **Feature Load Times**: Individual feature rendering performance
- **Memory Usage**: Per-feature memory consumption
- **API Response Times**: Feature-specific endpoint performance
- **Error Rates**: Feature-level error tracking

## Error Boundaries
Each feature has isolated error handling to prevent cascading failures:
- Upload errors don't prevent Settings access
- Mapping failures allow manual export
- SFTP errors don't affect local export
- UI errors don't crash backend processing

## Development Workflow
1. **Feature Selection**: Choose appropriate feature module
2. **Spec Review**: Read feature SPEC.md for context
3. **Dependency Check**: Verify impact on other features
4. **Implementation**: Make changes following feature guidelines
5. **Testing**: Run feature and integration tests
6. **Documentation**: Update SPEC.md if behavior changes

## Communication Channels
- **Shared Types**: `frontend/src/types/` for cross-feature interfaces
- **Global Context**: Application state shared across features
- **API Contracts**: Backend endpoints used by multiple features
- **Event System**: Feature-to-feature communication via events

## Rollback Strategy
- **Feature Flags**: Ability to disable individual features
- **Version Compatibility**: Maintain backward-compatible APIs
- **Data Migration**: Safe upgrade/downgrade paths
- **Graceful Degradation**: Core functionality preserved if features fail