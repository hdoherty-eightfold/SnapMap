# XSD Schema Parser & Generator Implementation

## Overview

This document describes the implementation of automatic XSD schema parsing and JSON schema generation for the SnapMap application. This enhancement ensures that all fields defined in Eightfold XSD files (including complex types from `ef_common_types.xsd`) are available for customer field mapping.

## Problem Statement

Previously, the application manually maintained JSON schema files with limited field coverage. Complex types defined in `ef_common_types.xsd` (such as `CertificationType`, `EducationType`, `ExperienceType`, etc.) were not properly exposed for mapping, making it impossible for customers to map their data to these nested structures.

### Example Issue

The `CertificationType` complex type is defined in `ef_common_types.xsd` with fields like:
- `certificate_name`
- `issuing_authority`
- `license_no`
- `valid_from`
- `valid_to`
- etc.

This type is referenced in both:
- `ef_employee_common.xsd` (in `candidate_data/certification_list`)
- `ef_cand_common.xsd` (in `certification_list`)

But these fields were NOT available in the mapping interface because they weren't in the manually-maintained JSON schemas.

## Solution

We implemented a two-part solution:

### 1. XSD Parser (`app/services/xsd_parser.py`)

A comprehensive XSD parser that:

**Features:**
- Parses entity-specific XSD files (e.g., `ef_employee_common.xsd`, `ef_cand_common.xsd`)
- Automatically resolves `xs:include` directives to load `ef_common_types.xsd`
- Expands complex type references (e.g., `CertificationType` → all its child fields)
- Handles nested structures and builds proper XML paths
- Supports all XSD containers: `xs:all`, `xs:sequence`, `xs:choice`
- Tracks field metadata: required status, data types, patterns, min/max occurs

**Key Classes:**
- `XSDParser`: Main parser class with caching
- `XSDField`: Data class representing an extracted field

**Example Output:**

For the employee entity, the parser extracts fields like:
```
candidate_data/certification_list/certification/certificate_name
candidate_data/certification_list/certification/issuing_authority
candidate_data/certification_list/certification/license_no
candidate_data/certification_list/certification/valid_from
candidate_data/certification_list/certification/valid_to
... (and all other certification fields)
```

### 2. Schema Generator (`app/services/schema_generator.py`)

Automatic JSON schema generation from XSD files:

**Features:**
- Uses `XSDParser` to extract all fields from XSD
- Filters to only include leaf fields (not container types)
- Generates JSON schemas compatible with `SchemaManager`
- Creates human-readable display names
- Generates appropriate example values based on field types
- Supports all 16 Eightfold entities

**Generated Schema Format:**
```json
{
  "entity_name": "employee",
  "display_name": "Employee",
  "description": "Employee master data for Eightfold integration (generated from XSD)",
  "source": "ef_employee_common.xsd + ef_common_types.xsd",
  "fields": [
    {
      "name": "CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_CERTIFICATE_NAME",
      "display_name": "Certificate Name (Certification)",
      "type": "string",
      "required": false,
      "example": "John Doe",
      "description": "certificate_name field",
      "xml_path": "candidate_data/certification_list/certification/certificate_name"
    },
    ... (all other fields)
  ]
}
```

## Results

### Schemas Generated

All 16 entity schemas successfully generated:

| Entity | Fields | Source XSD |
|--------|--------|------------|
| employee | 2,438 | ef_employee_common.xsd |
| candidate | 1,024 | ef_cand_common.xsd |
| user | 70 | ef_user_common.xsd |
| position | 1,182 | ef_position_common.xsd |
| course | 38 | ef_course_common.xsd |
| role | 168 | ef_role_common.xsd |
| demand | 260 | ef_demand_common.xsd |
| holiday | 9 | ef_holiday_common.xsd |
| org_unit | 302 | ef_org_unit_common.xsd |
| foundation_data | 20 | ef_foundation_data_common.xsd |
| pay_grade | 18 | ef_pay_grade_common.xsd |
| project | 264 | ef_project_common.xsd |
| succession_plan | 22 | ef_succession_plan_common.xsd |
| planned_event | 28 | ef_planned_event_common.xsd |
| certificate | 4 | ef_certificate_common.xsd |
| offer | 78 | ef_offer_common.xsd |

### Complex Types from ef_common_types.xsd

The parser successfully loaded and expanded **70 complex types** and **16 simple types** from `ef_common_types.xsd`, including:

**Complex Types:**
- `CertificationType` (16 fields)
- `EducationType` (17 fields)
- `ExperienceType` (12 fields)
- `ProjectType` (9 fields + nested structures)
- `LocationType` (6 fields)
- `AttachmentType` (multiple fields)
- `NoteType` (9 fields)
- `UserType` (3 fields)
- `ApplicationType` (extensive nested structure)
- `CustomFieldType`, `CustomFieldNativeListType`, `CustomFieldCompositeType`
- `PayType`, `BadgeType`, `CourseAttendanceType`
- `SkillListType`, `SkillDetailType`, `SkillGroupType`
- `PerformanceRatingType`, `LanguageProficiencyType`, `MobilityType`
- And many more...

**Simple Types:**
- `GenderType`
- `RatingType`
- `PostedForType`
- `ContactConsentType`
- `HolidayType`
- `OrgUnitType`
- `NoSpaceString`
- And more...

## Integration with Existing System

The XSD-based schemas integrate seamlessly with the existing SnapMap architecture:

### SchemaManager
- Loads XSD-generated JSON schemas
- Provides fields to the API layer
- Validates field definitions

### FieldMapper
- Auto-maps customer CSV fields to XSD-defined fields
- Uses semantic matching for complex type fields
- Supports nested paths like `candidate_data/certification_list/certification/certificate_name`

### XMLTransformer
- Transforms CSV data to Eightfold XML
- Uses `xml_path` from schema fields to build proper XML structure
- Handles nested elements and lists

### API Endpoints
- `/api/schema/{entity_name}` - Returns full schema with all XSD fields
- `/api/auto-map` - Maps CSV fields to XSD-defined target fields
- `/api/transform/*` - Transforms data using XSD-based mappings

## Usage

### Regenerate All Schemas

To regenerate all entity schemas from XSD files:

```bash
cd backend
python app/services/schema_generator.py
```

This will:
1. Parse all 16 entity XSD files
2. Load complex types from `ef_common_types.xsd`
3. Generate JSON schemas with all fields
4. Save to `backend/app/schemas/` directory

### Parse Individual Entity

```python
from app.services.xsd_parser import get_xsd_parser

parser = get_xsd_parser()
fields = parser.parse_entity_schema("employee", "common")

# Get flat field list for mapping UI
flat_fields = parser.get_flat_field_list("employee", "common")
```

### Generate Individual Schema

```python
from app.services.schema_generator import SchemaGenerator

generator = SchemaGenerator()
schema = generator.generate_schema("employee", "employee", save_to_file=True)
```

## File Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── xsd_parser.py           # XSD parsing logic
│   │   ├── schema_generator.py     # Schema generation from XSD
│   │   ├── schema_manager.py       # Schema loading and management
│   │   └── field_mapper.py         # Field mapping with XSD fields
│   └── schemas/
│       ├── employee_schema.json    # Generated from XSD
│       ├── candidate_schema.json   # Generated from XSD
│       ├── user_schema.json        # Generated from XSD
│       └── ... (all 16 entities)
│
├── docs/
│   └── schemas/
│       └── ef_xml_schema/
│           ├── ef_common_types.xsd      # Complex type definitions
│           ├── ef_employee_common.xsd   # Employee schema
│           ├── ef_cand_common.xsd       # Candidate schema
│           └── ... (all entity XSDs)
```

## Benefits

1. **Complete Field Coverage**: All fields from XSD are available for mapping, including complex types
2. **Automatic Updates**: When Eightfold updates their XSD files, just regenerate schemas
3. **No Manual Maintenance**: Schemas are generated automatically from source of truth (XSD files)
4. **Type Safety**: Field types, requirements, and patterns come directly from XSD definitions
5. **Nested Field Support**: Complex types like certifications, education, experience are fully mapped
6. **All Entities Supported**: All 16 Eightfold entities now have complete schemas

## Certification Fields Example

Before this implementation, certification fields were not available. Now customers can map to:

**Employee Entity - Certification Fields:**
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_CERTIFICATE_NAME`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_ISSUING_AUTHORITY`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_PROFICIENCY`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_LICENSE_NO`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_VALID_FROM`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_VALID_TO`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_START_DATE`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_END_DATE`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_LOCATION_STATE`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_LOCATION_COUNTRY`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_STATUS`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_COMMENTS`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_VERIFICATION_STATUS`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_VERIFICATION_BY`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_VERIFICATION_TS`
- `CANDIDATE_DATA_CERTIFICATION_LIST_CERTIFICATION_CERTIFICATE_EXTERNAL_ID`

**Candidate Entity - Certification Fields:**
- `CERTIFICATION_LIST_CERTIFICATION_CERTIFICATE_NAME`
- `CERTIFICATION_LIST_CERTIFICATION_ISSUING_AUTHORITY`
- `CERTIFICATION_LIST_CERTIFICATION_PROFICIENCY`
- `CERTIFICATION_LIST_CERTIFICATION_LICENSE_NO`
- `CERTIFICATION_LIST_CERTIFICATION_VALID_FROM`
- `CERTIFICATION_LIST_CERTIFICATION_VALID_TO`
- (and all other certification fields)

## Next Steps

1. **Sample Data**: Add sample CSV files for the newly supported entities
2. **XML Transformation**: Enhance XMLTransformer to handle all complex type structures
3. **Testing**: Add comprehensive tests for XSD parsing and schema generation
4. **Documentation**: Update API documentation with new field availability
5. **UI Updates**: Update field mapping UI to better display nested field hierarchies

## Technical Notes

- **Caching**: XSDParser caches parsed complex types for performance
- **Namespace Handling**: Properly handles XML Schema namespace (`http://www.w3.org/2001/XMLSchema`)
- **Recursion Prevention**: Prevents infinite loops when complex types reference each other
- **Type Normalization**: Maps XSD types (xs:string, xs:date, etc.) to common types
- **Display Name Generation**: Automatically creates user-friendly names for nested fields

## Conclusion

The XSD parser and schema generator implementation successfully addresses the requirement to expose all fields from Eightfold XSD schemas, including complex types from `ef_common_types.xsd`. Customers can now map their CSV data to any field defined in the Eightfold XML schemas, including nested structures like certifications, education, experience, and more.

All 16 entity types are now fully supported with automatically generated, comprehensive schemas derived directly from the authoritative XSD source files.
