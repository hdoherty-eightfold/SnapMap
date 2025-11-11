# SnapMap Schema Organization

## Overview
All schemas and sample files are centrally organized under `docs/schemas/` for consistency and maintainability.

## Directory Structure
```
docs/schemas/
├── ef_csv_schema/          # Eightfold CSV schema definitions (.xlsx)
├── ef_xml_schema/          # Eightfold XML schema definitions (.xsd)
├── ef_csv_samples/         # Sample CSV files organized by entity
│   └── csv/
│       ├── employee/       # Employee entity samples
│       ├── candidate/      # Candidate entity samples
│       ├── position/       # Position entity samples
│       ├── user/          # User entity samples
│       └── ...            # Other entities
└── ef_xml_samples/         # Sample XML output files
```

## Sample Files by Entity

### Employee Entity
**Location**: `docs/schemas/ef_csv_samples/csv/employee/`
- `employee_sample_1.csv` - 10 records with diverse field mappings
- `employee_sample_2.csv` - 5 records with alternate field names
- `EMPLOYEE-MAIN_20210820.csv` - Eightfold standard format
- `EMPLOYEE-EXPERIENCE_20210820.csv` - Experience data format
- `EMPLOYEE-EDUCATION_20210820.csv` - Education data format
- And 10+ other employee-related CSV formats

### Candidate Entity
**Location**: `docs/schemas/ef_csv_samples/csv/candidate/`
- `candidate_sample.csv` - Basic candidate data
- `candidate_certification_sample.csv` - Certification data

### Position Entity
**Location**: `docs/schemas/ef_csv_samples/csv/position/`
- `position_sample.csv` - Job position data

### User Entity
**Location**: `docs/schemas/ef_csv_samples/csv/user/`
- `user_sample.csv` - User account data

## Frontend Access
The frontend accesses these files through:
1. **Direct copies**: Key samples copied to `frontend/public/samples/` for UI download
2. **Symlink**: `frontend/public/samples/csv -> docs/schemas/ef_csv_samples/csv`

## Backend Schema Files
Backend JSON schemas remain in `backend/app/schemas/`:
- `employee_schema.json` - Employee field mappings
- `candidate_schema.json` - Candidate field mappings
- `position_schema.json` - Position field mappings
- `user_schema.json` - User field mappings
- `role_schema.json` - Role field mappings
- `course_schema.json` - Course field mappings

## File Naming Conventions

### CSV Samples
- `{entity}_sample.csv` - Simple test samples
- `{entity}_sample_{number}.csv` - Multiple variants
- `{ENTITY}-{TYPE}_{date}.csv` - Eightfold standard format

### XML Samples
- `test_output_{entity}_sample_{number}_{description}.xml` - Generated output examples

### Schema Files
- `ef_{entity}_{operation}_csv_schema.xlsx` - CSV schema definitions
- `ef_{entity}_{type}.xsd` - XML schema definitions

## Sample File Details

### Employee Sample 1 (10 records)
**File**: `employee_sample_1.csv`
**Fields**: Worker_ID, Legal_First_Name, Legal_Last_Name, Email_Address, Hire_Date, Job_Profile, Cost_Center, Work_Phone, Work_Location, Manager_Name, Skill1, Skill2

### Employee Sample 2 (5 records)
**File**: `employee_sample_2.csv`
**Fields**: userId, firstName, lastName, email, hireDate, title, division, businessPhone, location, reportsTo

## Usage in Development

### Adding New Samples
1. Place in appropriate entity folder under `docs/schemas/ef_csv_samples/csv/{entity}/`
2. Copy to `frontend/public/samples/` if needed for UI download
3. Update this README if adding new entity types

### Accessing from Frontend
```javascript
// Static samples for download
'/samples/employee_sample_1.csv'

// All samples via symlink
'/samples/csv/employee/employee_sample_1.csv'
```

### Accessing from Backend
```python
# Schema files
'backend/app/schemas/employee_schema.json'

# Sample files for testing
'docs/schemas/ef_csv_samples/csv/employee/employee_sample_1.csv'
```

## Maintenance Notes
- All documentation samples centralized in `docs/schemas/`
- Frontend samples are copies, not symlinks (for better browser compatibility)
- Backend schemas remain in app structure for runtime access
- XML samples include both input and expected output examples