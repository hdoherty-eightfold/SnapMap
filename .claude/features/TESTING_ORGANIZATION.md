# SnapMap Testing Organization

## Overview
All testing information is now centralized within feature specifications. Each feature spec contains detailed testing documentation including test files, coverage, and performance benchmarks.

## Test File Organization

### Feature-Based Test Structure
```
backend/tests/features/
├── upload/
│   ├── test_delimiter_detection.py
│   ├── test_delimiter_encoding.py
│   └── test_character_encoding.py
├── mapping/
│   ├── test_field_mapping_accuracy.py
│   ├── test_enhanced_mapping.py
│   └── test_enhanced_mapper.py
├── export/
│   ├── test_data_loss_validation.py
│   ├── test_multi_value_fields.py
│   └── test_xml_functionality.py
├── review/
│   └── test_multi_value_and_validation.py
└── sftp/
    └── test_sftp_persistence.py
```

### Legacy Tests (Archived)
```
docs/archive/legacy-tests/
├── test_siemens_*.py           # Siemens-specific tests
├── test_complete_workflow.py   # Old integration tests
├── test_api_fix.py             # Legacy API tests
├── performance_test.py         # Old performance tests
└── test_*.py                   # Various scattered tests
```

## Testing Standards

### Per-Feature Testing Requirements
Each feature must have:
1. **Unit Tests** - Core functionality testing
2. **Performance Benchmarks** - Speed and memory usage targets
3. **Error Handling Tests** - Failure scenario coverage
4. **Integration Tests** - Cross-feature compatibility

### Test Documentation in Feature Specs
Each `.claude/features/{feature}/SPEC.md` contains:
- **Test Files**: List of specific test files and their purpose
- **Test Coverage**: What functionality is tested
- **Performance Benchmarks**: Speed and accuracy targets
- **Integration Tests**: Cross-feature test requirements

## Running Tests

### By Feature
```bash
# Upload feature tests
pytest backend/tests/features/upload/

# Mapping feature tests
pytest backend/tests/features/mapping/

# Export feature tests
pytest backend/tests/features/export/
```

### All Features
```bash
# Run all feature tests
pytest backend/tests/features/

# Run with coverage
pytest backend/tests/features/ --cov=backend/app
```

### Integration Tests
```bash
# End-to-end workflow tests
pytest backend/tests/test_siemens_end_to_end.py
```

## Test Maintenance

### Adding New Tests
1. **Identify Feature**: Determine which feature the test belongs to
2. **Follow Naming**: Use descriptive names (e.g., `test_{functionality}_validation.py`)
3. **Update Spec**: Add test info to the feature's SPEC.md file
4. **Integration Check**: Ensure test doesn't break other features

### Modifying Existing Tests
1. **Check Dependencies**: Review MAIN_ORCHESTRATOR.md for feature interactions
2. **Update Documentation**: Modify feature SPEC.md if test behavior changes
3. **Cross-Feature Impact**: Run related feature tests to ensure no regressions

## Test Coverage Targets

### Per Feature Minimums
- **Upload**: >95% encoding detection, >98% delimiter detection
- **Mapping**: >75% semantic matching accuracy
- **Export**: 100% data loss prevention, >95% format compliance
- **Review**: >90% issue detection accuracy
- **SFTP**: >99% connection reliability
- **Settings**: 100% configuration validation
- **Layout**: >95% UI component coverage

### Overall Project
- **Total Test Coverage**: >85%
- **Critical Path Coverage**: >95%
- **Integration Test Coverage**: >80%

## Benefits of New Organization

### Before
- Tests scattered across multiple locations
- No clear feature ownership
- Difficult to maintain
- Unclear test coverage per feature

### After
- Feature-based test organization
- Clear ownership and documentation
- Easy to maintain and extend
- Comprehensive coverage tracking
- Single source of truth in feature specs