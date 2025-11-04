# Test Data Files

This folder contains sample data files for testing the SnapMap application.

## Employee Sample Files

### employee_sample_1.csv
Sample employee data with varied field naming conventions (e.g., Worker_ID, Legal_First_Name, etc.)
- 10 sample employee records
- Tests field mapping with underscore-separated names
- Includes additional fields like skills

### employee_sample_2.csv
Alternative employee data format with different naming conventions (e.g., userId, firstName, etc.)
- 5 sample employee records
- Tests field mapping with camelCase names
- More compact field set

## Other Entity Types

You can create additional sample files for other entity types:
- `user_sample.csv` - User account data
- `position_sample.csv` - Job position/requisition data
- `candidate_sample.csv` - Candidate application data
- `course_sample.csv` - Training course data
- `role_sample.csv` - Role/permission data

## Usage

These files are used for:
1. **Testing the auto-mapping algorithm** - Verify that the AI can correctly map source fields to Eightfold schema fields
2. **Manual testing** - Upload these files through the UI to test the complete workflow
3. **Integration testing** - Use in automated tests to verify end-to-end functionality
4. **Schema inference testing** - Test AI entity type detection from field names

## Adding New Test Files

When creating new test files:
1. Use generic field names (not specific to any HR system)
2. Include variety in naming conventions (snake_case, camelCase, etc.)
3. Keep files small (5-20 records) for quick testing
4. Document the purpose in this README
