# Testing Strategy

**Project**: ETL UI - HR Data Transformation Tool
**Version**: 1.0
**Last Updated**: November 2, 2025

## Overview

This document outlines the testing strategy for the ETL UI project, including unit tests, integration tests, and end-to-end testing procedures.

---

## Testing Pyramid

```
        /\
       /  \  E2E Tests (5%)
      /────\
     /      \ Integration Tests (25%)
    /────────\
   /          \ Unit Tests (70%)
  /────────────\
```

### Test Distribution
- **Unit Tests** (70%): Test individual functions and components
- **Integration Tests** (25%): Test module interactions and API endpoints
- **E2E Tests** (5%): Test complete user workflows

---

## Unit Testing

### Frontend Unit Tests

**Framework**: Vitest + React Testing Library

**Location**: `frontend/src/**/*.test.tsx`

#### What to Test

1. **Components**
   - Renders correctly
   - Handles props correctly
   - User interactions (clicks, inputs)
   - Conditional rendering

2. **Hooks**
   - State management
   - Side effects
   - Return values

3. **Utils**
   - Pure functions
   - Edge cases
   - Error handling

#### Example: Button Component Test

```typescript
// frontend/src/components/common/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

#### Example: API Client Test

```typescript
// frontend/src/services/api.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from './api';
import axios from 'axios';

vi.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('uploads file successfully', async () => {
    const mockFile = new File(['content'], 'test.csv', { type: 'text/csv' });
    const mockResponse = {
      data: {
        filename: 'test.csv',
        row_count: 10,
        column_count: 5
      }
    };

    mockedAxios.post.mockResolvedValue(mockResponse);

    const result = await apiClient.uploadFile(mockFile);

    expect(result.filename).toBe('test.csv');
    expect(result.row_count).toBe(10);
  });
});
```

### Backend Unit Tests

**Framework**: pytest

**Location**: `backend/app/**/*_test.py`

#### What to Test

1. **Services**
   - Business logic
   - Data transformations
   - Algorithm correctness

2. **Utils**
   - Helper functions
   - Data validation
   - Format conversion

#### Example: Field Mapper Test

```python
# backend/app/services/field_mapper_test.py
import pytest
from app.services.field_mapper import FieldMapper
from app.models.schema import EntitySchema

def test_exact_match():
    mapper = FieldMapper()
    confidence, method = mapper.calculate_match("EMAIL", "EMAIL")

    assert confidence == 1.0
    assert method == "exact"

def test_alias_match():
    mapper = FieldMapper()
    confidence, method = mapper.calculate_match("EmpID", "EMPLOYEE_ID")

    assert confidence >= 0.95
    assert method == "alias"

def test_fuzzy_match():
    mapper = FieldMapper()
    confidence, method = mapper.calculate_match("FirstNme", "FIRST_NAME")

    assert confidence >= 0.70
    assert method == "fuzzy"

def test_auto_map_accuracy():
    mapper = FieldMapper()
    schema = get_employee_schema()

    source_fields = [
        "EmpID", "FirstName", "LastName", "Email",
        "HireDate", "JobTitle", "Department", "Phone"
    ]

    mappings = mapper.auto_map(source_fields, schema)

    # Should map at least 80% of fields
    assert len(mappings) >= 6
    assert len(mappings) / len(source_fields) >= 0.80
```

#### Example: Transformation Test

```python
# backend/app/services/transformer_test.py
import pytest
import pandas as pd
from app.services.transformer import TransformationEngine

def test_date_format_conversion():
    engine = TransformationEngine()

    source_df = pd.DataFrame({
        'HireDate': ['10/30/2020', '05/15/2019']
    })

    result = engine.convert_date_column(
        source_df['HireDate'],
        target_format='YYYY-MM-DD'
    )

    assert result[0] == '2020-10-30'
    assert result[1] == '2019-05-15'

def test_field_mapping():
    engine = TransformationEngine()

    source_df = pd.DataFrame({
        'EmpID': ['E001', 'E002'],
        'FirstName': ['John', 'Jane']
    })

    mappings = [
        {'source': 'EmpID', 'target': 'EMPLOYEE_ID'},
        {'source': 'FirstName', 'target': 'FIRST_NAME'}
    ]

    result_df = engine.transform_data(source_df, mappings, schema)

    assert 'EMPLOYEE_ID' in result_df.columns
    assert 'FIRST_NAME' in result_df.columns
    assert result_df['EMPLOYEE_ID'][0] == 'E001'
```

---

## Integration Testing

### Frontend Integration Tests

Test component interactions and state management.

```typescript
// frontend/src/components/upload/FileUpload.integration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FileUpload } from './FileUpload';
import { AppContextProvider } from '../../contexts/AppContext';
import * as api from '../../services/api';

vi.mock('../../services/api');

describe('FileUpload Integration', () => {
  it('uploads file and updates context', async () => {
    const mockResponse = {
      filename: 'test.csv',
      row_count: 10,
      columns: ['EmpID', 'FirstName']
    };

    vi.spyOn(api, 'uploadFile').mockResolvedValue(mockResponse);

    render(
      <AppContextProvider>
        <FileUpload />
      </AppContextProvider>
    );

    const file = new File(['content'], 'test.csv', { type: 'text/csv' });
    const input = screen.getByLabelText('Upload file');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.csv')).toBeInTheDocument();
      expect(screen.getByText('10 rows')).toBeInTheDocument();
    });
  });
});
```

### Backend Integration Tests

Test API endpoints with FastAPI TestClient.

```python
# backend/app/api/endpoints/upload_test.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from io import BytesIO

client = TestClient(app)

def test_upload_csv_file():
    # Create test CSV file
    csv_content = b"EmpID,FirstName,LastName\nE001,John,Doe\nE002,Jane,Smith"
    files = {'file': ('test.csv', BytesIO(csv_content), 'text/csv')}

    response = client.post('/api/upload', files=files)

    assert response.status_code == 200
    data = response.json()
    assert data['filename'] == 'test.csv'
    assert data['row_count'] == 2
    assert data['column_count'] == 3
    assert 'EmpID' in data['columns']

def test_upload_invalid_file():
    files = {'file': ('test.txt', BytesIO(b"invalid"), 'text/plain')}

    response = client.post('/api/upload', files=files)

    assert response.status_code == 400
    assert 'error' in response.json()
```

---

## End-to-End Testing

### Manual E2E Test Cases

#### Test Case 1: Complete Workflow - Happy Path

**Steps**:
1. Open application (http://localhost:5173)
2. Upload `test_workday_export.csv`
3. Click "Continue to Mapping"
4. Click "Auto-Map" button
5. Verify 8+ fields are auto-mapped
6. Manually map remaining fields
7. Click "Preview Transformation"
8. Verify before/after data
9. Click "Download CSV"
10. Verify file downloads

**Expected Result**: ✅ All steps complete successfully

#### Test Case 2: Validation Error Handling

**Steps**:
1. Upload `test_data.csv`
2. Click "Auto-Map"
3. Leave required field unmapped
4. Click "Preview"
5. Verify error message shown
6. Map missing field
7. Click "Preview" again
8. Verify validation passes

**Expected Result**: ✅ Error message shown, then clears after fix

#### Test Case 3: Large File Upload

**Steps**:
1. Upload `large_dataset_1000_rows.csv`
2. Wait for processing
3. Verify no errors
4. Click "Auto-Map"
5. Verify mapping completes < 5 seconds

**Expected Result**: ✅ Handles 1000 rows smoothly

---

## Mock Data

### Test Data Files

Create these test files in `scripts/test_data/`:

#### 1. Workday Format

```csv
# workday_export.csv
Worker_ID,Legal_First_Name,Legal_Last_Name,Email_Address,Hire_Date,Job_Profile,Cost_Center,Work_Phone,Work_Location
W001,John,Doe,john@company.com,10/30/2020,Software Engineer,ENG001,+1-555-0100,San Francisco
W002,Jane,Smith,jane@company.com,05/15/2019,Senior Engineer,ENG001,+1-555-0101,San Francisco
W003,Mike,Johnson,mike@company.com,12/01/2021,Product Manager,PROD001,+1-555-0102,New York
```

#### 2. SuccessFactors Format

```csv
# successfactors_export.csv
userId,firstName,lastName,email,hireDate,title,division,businessPhone
SF001,Sarah,Williams,sarah@company.com,03/15/2020,Designer,Design,+1-555-0103
SF002,David,Brown,david@company.com,08/22/2018,Tech Lead,Engineering,+1-555-0104
```

#### 3. Oracle HCM Format

```csv
# oracle_export.csv
EmpNum,FName,LName,EmailAddr,DateHired,Position,Dept,PhoneNum
O001,Lisa,Garcia,lisa@company.com,11/10/2021,Analyst,Analytics,+1-555-0105
O002,Tom,Martinez,tom@company.com,07/05/2019,Manager,Operations,+1-555-0106
```

### Mock Data for Unit Tests

```typescript
// frontend/src/mocks/testData.ts

export const MOCK_UPLOAD_RESPONSE = {
  filename: 'workday_export.csv',
  row_count: 150,
  column_count: 12,
  columns: [
    'EmpID', 'FirstName', 'LastName', 'Email',
    'HireDate', 'JobTitle', 'Department', 'Phone',
    'Location', 'Manager', 'Skill1', 'Skill2'
  ],
  sample_data: [
    {
      EmpID: 'E001',
      FirstName: 'John',
      LastName: 'Doe',
      Email: 'john@company.com',
      HireDate: '10/30/2020',
      JobTitle: 'Software Engineer',
      Department: 'Engineering',
      Phone: '+1-555-0100',
      Location: 'San Francisco',
      Manager: 'Jane Smith',
      Skill1: 'Python',
      Skill2: 'JavaScript'
    }
  ],
  data_types: {
    EmpID: 'string',
    FirstName: 'string',
    LastName: 'string',
    Email: 'email',
    HireDate: 'date',
    JobTitle: 'string',
    Department: 'string',
    Phone: 'string',
    Location: 'string',
    Manager: 'string',
    Skill1: 'string',
    Skill2: 'string'
  },
  file_size: 52428
};

export const MOCK_SCHEMA = {
  entity_name: 'employee',
  display_name: 'Employee',
  description: 'Employee master data',
  fields: [
    {
      name: 'EMPLOYEE_ID',
      display_name: 'Employee ID',
      type: 'string',
      required: true,
      max_length: 50,
      example: 'E001',
      description: 'Unique employee identifier'
    },
    // ... more fields
  ]
};
```

---

## Test Coverage Goals

### Minimum Coverage Requirements

- **Frontend**: 60% code coverage
- **Backend**: 70% code coverage
- **Critical paths**: 90% coverage
  - Auto-mapping algorithm
  - Data transformation
  - Validation logic

### Measuring Coverage

#### Frontend
```bash
cd frontend
npm run test -- --coverage
```

#### Backend
```bash
cd backend
pytest --cov=app --cov-report=html
```

---

## Testing Schedule

### Day 1-2: Unit Tests as You Code
- Write unit tests for each function
- Aim for 50%+ coverage

### Day 3: First Integration Tests
- Test API endpoints
- Test component integration
- Backend + Frontend integration

### Day 5: Comprehensive Testing
- Increase coverage to 60%+
- Test edge cases
- Manual E2E testing

### Day 6: Bug Fixes
- Fix issues found in testing
- Regression testing
- Performance testing

### Day 7: Final Testing
- Complete E2E test suite
- Practice demo flow 3-4 times
- Record backup video

---

## Testing Checklist

### Before Integration
- [ ] All unit tests pass
- [ ] No console errors
- [ ] Mock data works correctly

### Before Demo
- [ ] E2E test cases pass
- [ ] Demo flow tested 3+ times
- [ ] Error handling tested
- [ ] Performance acceptable (< 5 sec)
- [ ] No critical bugs

### Production Ready
- [ ] 60%+ code coverage
- [ ] All edge cases tested
- [ ] No known critical bugs
- [ ] Performance benchmarks met

---

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Remember**: "Done is better than perfect" - Focus on critical path testing, not 100% coverage!

*Last Updated: November 2, 2025*
