# Semantic Matching Setup - Complete Review

## Overview
SnapMap's semantic matching system is fully configured to identify all 45 employee fields using a hybrid approach combining:
1. **Alias/Exact Matching** (85-100% confidence)
2. **Semantic Embedding Matching** (70-85% confidence)
3. **Fuzzy String Matching** (70-84% confidence)

## Employee Schema Coverage

### Total Fields: 45
All fields have comprehensive aliases and semantic embeddings.

### Required Fields (5):
- `EMPLOYEE_ID` - Unique employee identifier
- `FIRST_NAME` - Employee's first name
- `LAST_NAME` - Employee's last name
- `EMAIL` - Work email address
- `LAST_ACTIVITY_TS` - Last activity timestamp

### Optional Fields (40):
Identity & Basic Info, Job/Role Details, Manager Information, Organizational Structure, Compensation Details, Personal Information, Development Plans, Skills & Attributes

## Alias Configuration

### Statistics
- **Total Field Mappings**: 59 target fields
- **Total Unique Aliases**: 916
- **Average Aliases per Field**: 15.5
- **Coverage**: 100% of employee fields

### Common Siemens Field Mappings (Verified)
| Source Field | Target Field | Status |
|-------------|-------------|---------|
| PersonID | EMPLOYEE_ID/CANDIDATE_ID | ✓ |
| FirstName | FIRST_NAME | ✓ |
| LastName | LAST_NAME | ✓ |
| LastActivityTimeStamp | LAST_ACTIVITY_TS | ✓ |
| WorkEmails | EMAIL | ✓ |
| HomeEmails | PERSONAL_EMAIL | ✓ |
| WorkPhones | PHONE | ✓ |
| HomePhones | PHONE | ✓ |
| Summary | SUMMARY | ✓ |
| Website | URL | ✓ |
| Skills | SPECIALISED_SKILLS_LIST | ✓ |
| HomeLocation | LOCATION | ✓ |
| HomeCountry | LOCATION_COUNTRY | ✓ |

## Semantic Matching Features

### Type Detection & Boosting
The system detects field types from actual data content and boosts similarity scores:
- **Email fields**: +30% boost when detected type matches target
- **Phone fields**: +30% boost when detected type matches target
- **Date fields**: +20% boost when detected type matches target

### Enhanced Field Expansions
For better matching, source fields are expanded with contextual terms:
- Email fields → "email address", "electronic mail", "business email"
- Phone fields → "telephone", "phone number", "contact number"
- ID fields with "Person" → "employee id", "candidate id", "employee unique id"

### Multi-Stage Matching Process
1. **Stage 1**: Fuzzy/Alias matching (most accurate for known patterns)
2. **Stage 2**: Semantic embedding matching (handles variations)
3. **Stage 3**: Fuzzy string matching (fallback)

## Embeddings

### Employee Embeddings
- **File**: `backend/app/embeddings/employee_embeddings.pkl`
- **Model**: all-MiniLM-L6-v2 (sentence-transformers)
- **Fields**: All 45 employee fields
- **Status**: ✓ Rebuilt and verified

### Auto-Initialization
Embeddings are automatically initialized on backend startup in a background thread for optimal performance.

## Field Aliases by Category

### Identity Fields
- **EMPLOYEE_ID**: EmpID, EmployeeID, PersonID, UserID, WorkerID + 12 more
- **USER_ID**: UserID, Username, LoginID, AccountID, SystemID + 10 more
- **FIRST_NAME**: FirstName, GivenName, FName, ForeName + 11 more
- **LAST_NAME**: LastName, Surname, FamilyName, LName + 12 more
- **PREFERRED_FIRST_NAME**: PreferredFirstName, NickName, CommonName + 8 more
- **PREFERRED_LAST_NAME**: PreferredLastName, PreferredSurname, UsedLastName + 3 more

### Contact Fields
- **EMAIL**: WorkEmails, EmailAddress, BusinessEmail, Mail + 20 more
- **PERSONAL_EMAIL**: PersonalEmail, PrivateEmail, HomeEmail, AlternateEmail + 8 more
- **PHONE**: WorkPhones, PhoneNumber, Mobile, ContactNumber + 28 more
- **URL**: Website, ProfileURL, LinkedInURL, PersonalURL + 14 more

### Job/Role Fields
- **TITLE**: JobTitle, Position, Designation, Role + 12 more
- **DETAILED_TITLE**: DetailedTitle, ExtendedTitle, FullTitle, CompleteTitle + 6 more
- **ROLE**: Role, JobRole, Function, PositionType + 10 more
- **JOB_CODE**: JobCode, PositionCode, RoleCode, ClassificationCode + 8 more
- **LEVEL**: Level, Grade, Seniority, Rank, Band, PayBand + 10 more
- **EMPLOYEE_TYPE**: EmployeeType, WorkerType, EmploymentType, ContractType + 10 more

### Manager Fields
- **MANAGER_ID**: ManagerID, SupervisorID, ReportsToID, BossID + 8 more
- **MANAGER_EMAIL**: ManagerEmail, SupervisorEmail, ReportsToEmail, BossEmail + 6 more
- **MANAGER_FULLNAME**: ManagerFullName, SupervisorName, DirectManagerName + 9 more

### Organization Fields
- **COMPANY_NAME**: CompanyName, Organization, Employer, BusinessName + 9 more
- **BUSINESS_UNIT**: Department, Division, Unit, Team, BU + 13 more
- **DIVISION**: Division, BusinessDivision, Sector, Branch + 6 more
- **LOCATION**: HomeLocation, WorkLocation, Office, Site, City + 15 more
- **LOCATION_COUNTRY**: LocationCountry, WorkCountry, HomeCountry, Country + 9 more
- **ORG_UNIT_LIST**: OrgUnitList, OrganizationalUnitList, DepartmentList + 10 more

### Date Fields
- **HIRING_DATE**: HireDate, StartDate, JoinDate, EmploymentDate + 13 more
- **ROLE_CHANGE_DATE**: RoleChangeDate, PromotionDate, TransferDate + 10 more
- **TERMINATION_DATE**: TerminationDate, EndDate, ExitDate, SeparationDate + 13 more
- **PLAN_DATE**: PlanDate, ReviewDate, DevelopmentDate + 7 more
- **LAST_ACTIVITY_TS**: LastActivityTimeStamp, UpdatedAt, ModifiedDate + 17 more

### Compensation Fields
- **BASE_PAY_AMOUNT**: BasePayAmount, BaseSalary, Salary, AnnualSalary + 10 more
- **BASE_PAY_CURRENCY**: BasePayCurrency, SalaryCurrency, PayCurrency, CurrencyCode + 6 more
- **BASE_PAY_FREQUENCY**: BasePayFrequency, PayFrequency, PayPeriod + 6 more
- **BONUS_AMOUNT**: BonusAmount, Bonus, IncentiveAmount, AnnualBonus + 7 more
- **BONUS_CURRENCY**: BonusCurrency, BonusCurrencyCode, IncentiveCurrency + 3 more
- **BONUS_FREQUENCY**: BonusFrequency, BonusPeriod, IncentiveFrequency + 4 more

### Development & Skills Fields
- **PLAN_NAME**: PlanName, DevelopmentPlan, CareerPlan, SuccessionPlan + 7 more
- **PLAN_COMMENTS**: PlanComments, Comments, Notes, Remarks + 6 more
- **SUMMARY**: Summary, Bio, Profile, Overview, Description + 8 more
- **SPECIALISED_SKILLS_LIST**: Skills, SkillsList, TechnicalSkills, KeySkills + 10 more
- **POSITION_CRITICALITY_LIST**: PositionCriticality, Criticality, Importance + 7 more

### Personal/Demographic Fields
- **GENDER**: Gender, Sex, GenderIdentity + 3 more
- **RACE**: Race, Ethnicity, EthnicGroup, RacialGroup + 5 more
- **EXTERNAL_JOB_ID**: ExternalJobID, RequisitionID, JobPostingID, VacancyID + 9 more
- **RM_USER_GROUP_LIST**: UserGroupList, Groups, MemberGroups, AccessGroups + 8 more

## Validation & Testing

### Test Results
✓ All 45 employee fields have aliases
✓ All Siemens test fields mapping correctly
✓ JSON schema validated
✓ Embeddings rebuilt successfully
✓ Backend actively using updated schema

### Test Command
```bash
cd backend && python test_aliases.py
```

## Integration Points

### Backend Components
1. **schema_manager.py** - Loads employee_schema.json with LRU caching
2. **field_mapper.py** - Uses aliases for exact/fuzzy matching (Stage 1)
3. **semantic_matcher.py** - Uses embeddings for semantic matching (Stage 2)
4. **automapping.py** - Coordinates hybrid matching approach
5. **validator.py** - Validates against schema and detects issues

### Frontend Components
1. **FileUpload.tsx** - Initiates entity detection
2. **IssueReview.tsx** - Shows field mapping issues
3. **FieldMapper (component)** - Allows manual mapping adjustments
4. **PreviewCSV.tsx** - Shows transformed data with dynamic column widths

## Performance Optimizations

### Column Type Detection
- Analyzes actual data content to detect email, phone, and date fields
- Boosts semantic similarity when detected types match target schema types
- Implemented in [file_parser.py:detect_column_types()](backend/app/services/file_parser.py#L350-L390)

### Dynamic Column Widths
- Calculates optimal column widths based on content (min 100px, max 400px)
- Samples first 50 rows for performance
- Implemented in [PreviewCSV.tsx:calculateColumnWidths()](frontend/src/components/export/PreviewCSV.tsx#L32-L55)

### Caching Strategy
- Schema manager uses LRU cache (max 10 schemas)
- Embeddings loaded once on startup
- File storage metadata cached in memory

## Recommendations

### Current State
The semantic matching system is fully operational and production-ready with:
- Comprehensive alias coverage (916 unique aliases)
- All 45 employee fields properly configured
- Enhanced type detection and similarity boosting
- Multi-stage matching for maximum accuracy

### Future Enhancements
1. **Add more entity types**: Candidate, Position, User schemas need similar alias expansion
2. **Field-specific boosting**: Add domain-specific term boosting for specialized fields
3. **Learning from corrections**: Track user manual corrections to improve future mappings
4. **Confidence thresholds**: Allow users to configure minimum confidence levels
5. **Mapping analytics**: Track which aliases/patterns are most commonly matched

## File Locations

### Configuration
- Schema: [backend/app/schemas/employee_schema.json](backend/app/schemas/employee_schema.json)
- Aliases: [backend/app/schemas/field_aliases.json](backend/app/schemas/field_aliases.json)
- Registry: [backend/app/schemas/entity_registry.json](backend/app/schemas/entity_registry.json)

### Embeddings
- Employee: [backend/app/embeddings/employee_embeddings.pkl](backend/app/embeddings/employee_embeddings.pkl)
- Other entities: [backend/app/embeddings/](backend/app/embeddings/)

### Services
- Schema Manager: [backend/app/services/schema_manager.py](backend/app/services/schema_manager.py)
- Field Mapper: [backend/app/services/field_mapper.py](backend/app/services/field_mapper.py)
- Semantic Matcher: [backend/app/services/semantic_matcher.py](backend/app/services/semantic_matcher.py)

---

**Last Updated**: 2025-11-09
**Status**: ✓ Fully Operational
**Coverage**: 100% (45/45 employee fields)
**Total Aliases**: 916
