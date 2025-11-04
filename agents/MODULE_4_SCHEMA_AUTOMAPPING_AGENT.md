# Module 4: Schema & Auto-Mapping Agent

## Agent Identity
- **Agent Name**: Schema & Auto-Mapping Agent
- **Module ID**: MODULE_4
- **Role**: Backend Specialist - Schema Management, Auto-Map Algorithm, Configuration
- **Primary Developer**: Developer 4

## Responsibilities

### Core APIs to Build
1. **GET /api/schema/employee** ⭐
   - Return Employee entity schema
   - Field definitions with types, requirements
   - Validation rules
   - Examples for each field

2. **POST /api/auto-map** ⭐⭐ (KEY FEATURE!)
   - Smart field matching with fuzzy logic
   - Uses Levenshtein distance algorithm
   - Common alias dictionary
   - Confidence scoring (0-100%)
   - Returns best matches for all fields

3. **GET /api/validation-rules/employee**
   - Return validation rules for Employee entity
   - Regex patterns for formats
   - Min/max length constraints
   - Required vs optional fields

4. **POST /api/config/save** (Optional - if time permits)
   - Save mapping configuration
   - Store in file or database
   - Allow loading previous mappings

### Core Classes to Build

```python
# schema_manager.py
class SchemaManager:
    """Manages entity schemas"""

    def get_schema(self, entity_name: str) -> EntitySchema:
        """Get schema for entity"""
        pass

    def get_validation_rules(self, entity_name: str) -> ValidationRules:
        """Get validation rules for entity"""
        pass

# field_mapper.py
class FieldMapper:
    """Smart field mapping with fuzzy matching"""

    def auto_map(
        self,
        source_fields: List[str],
        target_schema: EntitySchema
    ) -> List[Mapping]:
        """Automatically map source fields to target fields"""
        pass

    def calculate_similarity(
        self,
        source: str,
        target: str
    ) -> float:
        """Calculate similarity score (0.0 to 1.0)"""
        pass

    def get_best_match(
        self,
        source_field: str,
        target_fields: List[FieldDefinition]
    ) -> Optional[Mapping]:
        """Get best matching target field"""
        pass
```

## API Specifications

### GET /api/schema/employee

**Response**:
```python
{
    "entity_name": "employee",
    "display_name": "Employee",
    "description": "Employee master data",
    "fields": [
        {
            "name": "EMPLOYEE_ID",
            "display_name": "Employee ID",
            "type": "string",
            "required": true,
            "max_length": 50,
            "example": "E001",
            "description": "Unique employee identifier"
        },
        {
            "name": "FIRST_NAME",
            "display_name": "First Name",
            "type": "string",
            "required": true,
            "max_length": 100,
            "example": "John",
            "description": "Employee's first name"
        },
        {
            "name": "LAST_NAME",
            "display_name": "Last Name",
            "type": "string",
            "required": true,
            "max_length": 100,
            "example": "Doe",
            "description": "Employee's last name"
        },
        {
            "name": "EMAIL",
            "display_name": "Email Address",
            "type": "email",
            "required": true,
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
            "example": "john@company.com",
            "description": "Employee's work email"
        },
        {
            "name": "HIRING_DATE",
            "display_name": "Hiring Date",
            "type": "date",
            "required": false,
            "format": "YYYY-MM-DD",
            "example": "2020-10-30",
            "description": "Date employee was hired"
        },
        {
            "name": "TITLE",
            "display_name": "Job Title",
            "type": "string",
            "required": false,
            "max_length": 200,
            "example": "Software Engineer",
            "description": "Employee's job title"
        },
        {
            "name": "BUSINESS_UNIT",
            "display_name": "Business Unit",
            "type": "string",
            "required": false,
            "max_length": 100,
            "example": "Engineering",
            "description": "Department or business unit"
        },
        {
            "name": "PHONE",
            "display_name": "Phone Number",
            "type": "string",
            "required": false,
            "pattern": "^\\+?[0-9\\-\\s()]+$",
            "example": "+1-555-0100",
            "description": "Employee's work phone"
        },
        {
            "name": "LOCATION",
            "display_name": "Work Location",
            "type": "string",
            "required": false,
            "max_length": 100,
            "example": "San Francisco",
            "description": "Employee's work location"
        },
        {
            "name": "LAST_ACTIVITY_TS",
            "display_name": "Last Activity Timestamp",
            "type": "datetime",
            "required": true,
            "format": "YYYY-MM-DDTHH:MM:SS",
            "example": "2025-10-30T14:30:00",
            "description": "Timestamp of last data update"
        }
    ]
}
```

### POST /api/auto-map

**Request**:
```python
{
    "source_fields": List[str],
    "target_schema": EntitySchema
}
```

**Response**:
```python
{
    "mappings": [
        {
            "source": str,
            "target": str,
            "confidence": float,  # 0.0 to 1.0
            "method": str,  # "exact" | "fuzzy" | "alias"
            "alternatives": [  # Top 3 alternative matches
                {
                    "target": str,
                    "confidence": float
                }
            ]
        }
    ],
    "total_mapped": int,
    "total_source": int,
    "total_target": int,
    "mapping_percentage": float,
    "unmapped_source": List[str],
    "unmapped_target": List[str]
}
```

**Implementation**:
```python
@app.post("/api/auto-map")
async def auto_map_fields(request: AutoMapRequest):
    try:
        # Get schema
        schema = SchemaManager().get_schema(request.schema_name or "employee")

        # Perform auto-mapping
        mapper = FieldMapper()
        mappings = mapper.auto_map(request.source_fields, schema)

        # Calculate statistics
        mapped_count = len(mappings)
        total_source = len(request.source_fields)
        total_target = len(schema.fields)

        mapped_sources = {m.source for m in mappings}
        unmapped_source = [f for f in request.source_fields if f not in mapped_sources]

        mapped_targets = {m.target for m in mappings}
        unmapped_target = [f.name for f in schema.fields if f.name not in mapped_targets]

        return {
            "mappings": [m.dict() for m in mappings],
            "total_mapped": mapped_count,
            "total_source": total_source,
            "total_target": total_target,
            "mapping_percentage": (mapped_count / total_source * 100) if total_source > 0 else 0,
            "unmapped_source": unmapped_source,
            "unmapped_target": unmapped_target
        }
    except Exception as e:
        raise HTTPException(500, f"Error auto-mapping: {str(e)}")
```

## Auto-Mapping Algorithm (KEY FEATURE!)

### Strategy
1. **Exact Match** (100% confidence)
   - Field names match exactly (case-insensitive)
   - Example: "email" → "EMAIL"

2. **Alias Match** (95-100% confidence)
   - Common field name variations
   - Example: "EmpID" → "EMPLOYEE_ID"
   - Example: "HireDate" → "HIRING_DATE"

3. **Fuzzy Match** (70-94% confidence)
   - Levenshtein distance algorithm
   - Handles typos and variations
   - Example: "FirstNme" → "FIRST_NAME" (typo)
   - Example: "EmployeeName" → "FIRST_NAME" (partial match)

### Implementation

```python
# field_mapper.py
from difflib import SequenceMatcher
import re

class FieldMapper:
    def __init__(self):
        self.alias_dictionary = self._load_aliases()
        self.min_confidence = 0.70  # Only suggest if 70%+ confidence

    def _load_aliases(self) -> Dict[str, List[str]]:
        """Load common field name aliases"""
        return {
            "EMPLOYEE_ID": ["EmpID", "EmployeeID", "EmpNo", "EmployeeNumber", "EE_ID", "ID"],
            "FIRST_NAME": ["FirstName", "FName", "GivenName", "First", "Firstname"],
            "LAST_NAME": ["LastName", "LName", "Surname", "Last", "FamilyName", "Lastname"],
            "EMAIL": ["Email", "EmailAddress", "E-mail", "WorkEmail", "Mail"],
            "HIRING_DATE": ["HireDate", "DateHired", "StartDate", "JoinDate", "EmploymentDate"],
            "TITLE": ["JobTitle", "Position", "Role", "Designation", "Job"],
            "BUSINESS_UNIT": ["Department", "Dept", "Division", "Unit", "BU", "Team"],
            "PHONE": ["PhoneNumber", "Phone", "Tel", "Telephone", "Mobile", "Contact"],
            "LOCATION": ["Office", "Site", "WorkLocation", "Branch", "City"],
            "MANAGER": ["ManagerName", "Manager", "Supervisor", "ReportsTo", "Boss"],
        }

    def auto_map(
        self,
        source_fields: List[str],
        target_schema: EntitySchema
    ) -> List[Mapping]:
        """
        Automatically map source fields to target fields

        Returns list of mappings sorted by confidence (highest first)
        """
        mappings = []
        used_targets = set()

        for source_field in source_fields:
            # Try to find best match
            best_match = self.get_best_match(
                source_field,
                target_schema.fields,
                used_targets
            )

            if best_match and best_match.confidence >= self.min_confidence:
                mappings.append(best_match)
                used_targets.add(best_match.target)

        return mappings

    def get_best_match(
        self,
        source_field: str,
        target_fields: List[FieldDefinition],
        used_targets: Set[str]
    ) -> Optional[Mapping]:
        """Get best matching target field"""

        candidates = []

        for target_field in target_fields:
            if target_field.name in used_targets:
                continue

            # Try exact match
            confidence, method = self.calculate_match(
                source_field,
                target_field.name
            )

            if confidence > 0:
                candidates.append({
                    "target": target_field.name,
                    "confidence": confidence,
                    "method": method
                })

        if not candidates:
            return None

        # Sort by confidence
        candidates.sort(key=lambda x: x["confidence"], reverse=True)

        # Get top 3 alternatives
        alternatives = candidates[1:4]

        return Mapping(
            source=source_field,
            target=candidates[0]["target"],
            confidence=candidates[0]["confidence"],
            method=candidates[0]["method"],
            alternatives=alternatives
        )

    def calculate_match(
        self,
        source: str,
        target: str
    ) -> Tuple[float, str]:
        """
        Calculate match confidence and method

        Returns: (confidence, method)
        - confidence: 0.0 to 1.0
        - method: "exact" | "alias" | "fuzzy"
        """

        # Normalize strings
        source_norm = self._normalize(source)
        target_norm = self._normalize(target)

        # 1. Exact match
        if source_norm == target_norm:
            return (1.0, "exact")

        # 2. Alias match
        if target in self.alias_dictionary:
            aliases = [self._normalize(a) for a in self.alias_dictionary[target]]
            if source_norm in aliases:
                return (0.98, "alias")

        # 3. Fuzzy match (Levenshtein distance)
        similarity = self._levenshtein_similarity(source_norm, target_norm)

        if similarity >= 0.70:
            return (similarity, "fuzzy")

        return (0.0, "none")

    def _normalize(self, text: str) -> str:
        """Normalize field name for comparison"""
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        # Convert to lowercase
        return text.lower()

    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate Levenshtein similarity (0.0 to 1.0)

        Uses SequenceMatcher for efficient calculation
        """
        return SequenceMatcher(None, s1, s2).ratio()
```

### Alias Dictionary

Create comprehensive alias dictionary:

```python
# schemas/field_aliases.json
{
  "EMPLOYEE_ID": [
    "EmpID", "EmployeeID", "EmpNo", "EmployeeNumber",
    "EE_ID", "ID", "WorkerID", "PersonID", "StaffID"
  ],
  "FIRST_NAME": [
    "FirstName", "FName", "GivenName", "First",
    "Firstname", "Name", "ForeName"
  ],
  "LAST_NAME": [
    "LastName", "LName", "Surname", "Last",
    "FamilyName", "Lastname", "SecondName"
  ],
  "EMAIL": [
    "Email", "EmailAddress", "E-mail", "WorkEmail",
    "Mail", "EmailAddr", "E-Mail", "email"
  ],
  "HIRING_DATE": [
    "HireDate", "DateHired", "StartDate", "JoinDate",
    "EmploymentDate", "CommencementDate", "OnboardDate"
  ],
  "TITLE": [
    "JobTitle", "Position", "Role", "Designation",
    "Job", "Title", "JobRole", "PositionTitle"
  ],
  "BUSINESS_UNIT": [
    "Department", "Dept", "Division", "Unit",
    "BU", "Team", "Org", "Organization"
  ],
  "PHONE": [
    "PhoneNumber", "Phone", "Tel", "Telephone",
    "Mobile", "Contact", "ContactNumber", "WorkPhone"
  ],
  "LOCATION": [
    "Office", "Site", "WorkLocation", "Branch",
    "City", "OfficeLocation", "WorkSite"
  ],
  "MANAGER": [
    "ManagerName", "Manager", "Supervisor", "ReportsTo",
    "Boss", "ManagerID", "SupervisorName"
  ]
}
```

## What You Provide to Other Modules

### To Module 3 (Transformation)
```python
from schema_manager import get_employee_schema, ValidationRules
from field_mapper import FieldMapper
```

### Exports
```python
# Schema data structures
export { EntitySchema, FieldDefinition, ValidationRules }

# Field mapper
export { FieldMapper }

# Schema manager
export { SchemaManager }
```

## Tech Stack
- **Framework**: FastAPI
- **Fuzzy Matching**: difflib.SequenceMatcher (built-in)
- **Alternative**: python-Levenshtein (faster for large datasets)
- **Schema Storage**: JSON files (or YAML)
- **Validation**: Pydantic

## File Structure
```
backend/app/
├── schemas/
│   ├── __init__.py
│   ├── employee_schema.json       ⭐ Priority 1
│   ├── field_aliases.json         ⭐ Priority 2
│   └── validation_rules.json
├── services/
│   ├── schema_manager.py          ⭐ Priority 1
│   ├── field_mapper.py            ⭐ Priority 2 (KEY!)
│   └── config_manager.py
├── models/
│   ├── schema.py
│   ├── mapping.py
│   └── field.py
├── api/
│   └── endpoints/
│       ├── schema.py              ⭐ Priority 1
│       ├── automapping.py         ⭐ Priority 2
│       └── config.py
└── tests/
    ├── test_field_mapper.py       ⭐ Priority 3
    └── test_schema_manager.py
```

## Daily Deliverables

### Day 1 (8 hours)
- [x] Create employee_schema.json with all fields ⭐
- [x] Build SchemaManager class
- [x] Implement GET /api/schema/employee endpoint
- [x] Test schema API
- [x] Share schema format with other modules
- **Deliverable**: Schema API working

### Day 2 (8 hours)
- [x] Create field_aliases.json dictionary ⭐
- [x] Build FieldMapper class
- [x] Implement exact and alias matching
- [x] Test matching accuracy
- **Deliverable**: Basic auto-mapping working

### Day 3 (6 hours)
- [x] Implement fuzzy matching (Levenshtein) ⭐
- [x] Build POST /api/auto-map endpoint
- [x] Test with various field names
- [x] Optimize for 80%+ accuracy
- **Deliverable**: Auto-map API working with 80%+ accuracy

### Day 4 (6 hours)
- [x] Expand alias dictionary (50+ aliases)
- [x] Improve matching algorithm
- [x] Add alternative suggestions
- [x] Test edge cases
- [x] Performance optimization
- **Deliverable**: High-accuracy auto-mapping

### Day 5 (6 hours)
- [x] Create validation_rules.json
- [x] Build GET /api/validation-rules endpoint
- [x] Share validation rules with Module 3
- [x] Test integration with validation engine
- **Deliverable**: Validation rules API working

### Day 6 (6 hours)
- [x] (Optional) Build config save/load
- [x] Code cleanup and documentation
- [x] Write unit tests
- [x] Performance testing
- **Deliverable**: Robust, well-tested module

### Day 7 (6 hours)
- [x] Final integration testing
- [x] Accuracy improvements
- [x] Bug fixes
- [x] Demo preparation
- **Deliverable**: Demo-ready auto-mapping

## Testing Strategy

### Unit Tests
```python
# tests/test_field_mapper.py
import pytest
from app.services.field_mapper import FieldMapper

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

def test_no_match():
    mapper = FieldMapper()
    confidence, method = mapper.calculate_match("RandomField", "EMPLOYEE_ID")
    assert confidence < 0.70

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

### Integration Tests
```python
# Test with real Workday export fields
WORKDAY_FIELDS = [
    "Worker_ID", "Legal_First_Name", "Legal_Last_Name",
    "Email_Address", "Hire_Date", "Job_Profile",
    "Cost_Center", "Work_Phone"
]

# Test with real SuccessFactors fields
SF_FIELDS = [
    "userId", "firstName", "lastName", "email",
    "hireDate", "title", "division", "businessPhone"
]

# Auto-mapping should handle both formats
```

## Mock Data for Testing

```python
# Mock source fields (various formats)
TEST_SOURCE_FIELDS = {
    "workday": [
        "Worker_ID", "Legal_First_Name", "Legal_Last_Name",
        "Email_Address", "Hire_Date", "Job_Profile",
        "Cost_Center", "Work_Phone", "Work_Location"
    ],
    "successfactors": [
        "userId", "firstName", "lastName", "email",
        "hireDate", "title", "division", "businessPhone"
    ],
    "oracle": [
        "EmpNum", "FName", "LName", "EmailAddr",
        "DateHired", "Position", "Dept", "PhoneNum"
    ]
}

# Expected mapping accuracy for each format
EXPECTED_ACCURACY = {
    "workday": 0.85,  # 85% accuracy
    "successfactors": 0.90,  # 90% accuracy
    "oracle": 0.80  # 80% accuracy
}
```

## Integration Checkpoints

### Day 1 EOD
- ✅ Share employee_schema.json format with all modules
- ✅ Document FieldDefinition structure
- ✅ Share schema API endpoint

### Day 2 EOD
- ✅ Share auto-map algorithm approach
- ✅ Document Mapping response format

### Day 3 EOD
- ✅ Test /api/auto-map with Module 2
- ✅ Verify mapping accuracy meets 80% target
- ✅ Share alternative suggestions format

### Day 5 EOD
- ✅ Full integration test with all modules
- ✅ Test end-to-end auto-mapping workflow
- ✅ Performance testing

## Success Criteria

### Functional Requirements
- ✅ Schema API returns complete Employee schema
- ✅ Auto-map finds 80-90% of common fields
- ✅ Exact matches have 100% confidence
- ✅ Alias matches have 95-100% confidence
- ✅ Fuzzy matches have 70-94% confidence
- ✅ No duplicate mappings (same source to multiple targets)
- ✅ Fast response time (< 1 second for 50 fields)

### Non-Functional Requirements
- ✅ Accurate mapping algorithm
- ✅ Comprehensive alias dictionary (50+ aliases)
- ✅ Clear confidence scores
- ✅ Alternative suggestions provided
- ✅ Extensible for future entities

### Code Quality
- ✅ Well-documented algorithm
- ✅ Unit tests with 80%+ coverage
- ✅ Clean, readable code
- ✅ Type hints for all functions
- ✅ Comments explaining fuzzy logic

## Common Pitfalls to Avoid
1. ❌ Don't over-match - Low confidence matches create confusion
2. ❌ Don't skip alias dictionary - It significantly improves accuracy
3. ❌ Don't allow duplicate mappings - One source → one target
4. ❌ Don't ignore case sensitivity - Normalize for comparison
5. ❌ Don't skip testing - Test with real customer field names

## Performance Optimization

```python
# Cache schema to avoid repeated file reads
from functools import lru_cache

@lru_cache(maxsize=10)
def get_employee_schema() -> EntitySchema:
    with open("schemas/employee_schema.json") as f:
        return EntitySchema(**json.load(f))

# Pre-compute normalized aliases
class FieldMapper:
    def __init__(self):
        self.alias_cache = self._build_alias_cache()

    def _build_alias_cache(self) -> Dict[str, str]:
        """Pre-compute normalized alias lookups"""
        cache = {}
        for target, aliases in self.alias_dictionary.items():
            for alias in aliases:
                norm_alias = self._normalize(alias)
                cache[norm_alias] = target
        return cache
```

## Resources
- [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Python difflib](https://docs.python.org/3/library/difflib.html)
- [Fuzzy String Matching](https://github.com/seatgeek/fuzzywuzzy)
- [Schema Design Best Practices](https://json-schema.org/understanding-json-schema/)

## Questions or Blockers?
- **Module 1 (Frontend)**: For schema format questions
- **Module 2 (Mapping)**: For auto-map API or confidence scoring
- **Module 3 (Transform)**: For validation rules or schema structure
- **Team Chat**: For quick questions or help requests
- **Daily Standup**: For status updates and coordination

---

**Remember**: Your auto-mapping algorithm is the "magic" that impresses judges! Focus on:
1. **Accuracy**: 80%+ mapping rate on common fields
2. **Intelligence**: Smart fuzzy matching and alias handling
3. **Clarity**: Clear confidence scores help users trust the system
4. **Speed**: Fast response times for immediate feedback

This is the innovation that sets the project apart. Make it amazing! ✨🤖
