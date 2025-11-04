"""
Test the bad file validation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import pandas as pd
from app.services.csv_validator import get_csv_validator

# Read the bad file
bad_file_path = "docs/badfiles/EMPLOYEE-MAIN_bad.csv"
print(f"=== Testing Validation on Bad File: {bad_file_path} ===\n")

# Load the file
df = pd.read_csv(bad_file_path)

print("File Headers:")
print(df.columns.tolist())
print()

print("First few rows:")
print(df.head())
print()

# Run validation
validator = get_csv_validator()
is_valid, issues = validator.validate_file(
    df=df,
    entity_name="employee",
    filename=bad_file_path
)

print(f"\n=== Validation Result ===")
print(f"Valid: {is_valid}")
print(f"Total Issues: {len(issues)}\n")

if issues:
    print("Issues Found:")
    for i, issue in enumerate(issues, 1):
        issue_dict = issue.to_dict()
        print(f"\n{i}. [{issue_dict['severity'].upper()}] {issue_dict['type']}")
        print(f"   Field: {issue_dict['field']}")
        print(f"   Description: {issue_dict['description']}")
        if issue_dict.get('suggestion'):
            print(f"   Suggestion: {issue_dict['suggestion']}")
        if issue_dict.get('affected_rows') != 'all':
            print(f"   Affected Rows: {issue_dict['affected_rows']}")
else:
    print("No issues found!")

print("\n=== Test Complete ===")
