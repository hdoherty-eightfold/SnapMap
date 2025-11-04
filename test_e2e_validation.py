"""
End-to-end test for CSV validation
Tests the full upload -> review flow with bad file
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json

# Backend URL
BASE_URL = "http://localhost:8000"

def test_bad_file_upload_and_review():
    """Test uploading and reviewing a file with validation issues"""

    print("=== End-to-End Validation Test ===\n")

    # Step 1: Upload the bad file
    print("Step 1: Uploading bad file...")
    bad_file_path = "docs/badfiles/EMPLOYEE-MAIN_bad.csv"

    with open(bad_file_path, 'rb') as f:
        files = {'file': (os.path.basename(bad_file_path), f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)

    if response.status_code != 200:
        print(f"[FAIL] Upload failed: {response.status_code}")
        print(response.text)
        return False

    upload_result = response.json()
    file_id = upload_result['file_id']
    entity_name = "employee"  # We know this is an employee file

    print(f"[OK] File uploaded successfully")
    print(f"  File ID: {file_id}")
    print(f"  Entity: {entity_name} (hardcoded for test)")
    print(f"  Rows: {upload_result['row_count']}")
    print(f"  Columns: {upload_result['column_count']}\n")

    # Step 2: Review the file (triggers validation)
    print("Step 2: Reviewing file (running validation)...")
    review_payload = {
        "file_id": file_id,
        "entity_name": entity_name,
        "include_suggestions": True
    }

    response = requests.post(
        f"{BASE_URL}/api/review/file",
        json=review_payload,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        print(f"[FAIL] Review failed: {response.status_code}")
        print(response.text)
        return False

    review_result = response.json()

    print(f"[OK] Review completed successfully")
    print(f"\n=== Full Response ===")
    print(json.dumps(review_result, indent=2))
    print(f"\n=== Summary ===")
    print(f"  Summary: {review_result['summary']}")
    print(f"  Total Issues: {review_result['total_issues']}")
    print(f"  Critical Issues: {review_result['critical_issues']}")
    print(f"  Warnings: {review_result['warnings']}")
    print(f"  Can Auto-fix: {review_result['can_auto_fix']}\n")

    # Step 3: Display issues found
    if review_result['issues_found']:
        print("Issues Found:")
        for i, issue in enumerate(review_result['issues_found'], 1):
            print(f"\n{i}. [{issue['severity'].upper()}] {issue['type']}")
            print(f"   Field: {issue.get('field', 'N/A')}")
            print(f"   Description: {issue.get('description', 'N/A')}")
            if issue.get('suggestion'):
                print(f"   Suggestion: {issue['suggestion']}")

    # Step 4: Display suggestions
    if review_result['suggestions']:
        print("\n\nSuggestions:")
        for i, suggestion in enumerate(review_result['suggestions'], 1):
            print(f"\n{i}. Type: {suggestion.get('issue_type', 'N/A')}")
            print(f"   Field: {suggestion.get('field', 'N/A')}")
            print(f"   Suggestion: {suggestion.get('suggestion', 'N/A')}")
            print(f"   Auto-fixable: {suggestion.get('auto_fixable', False)}")

    # Step 5: Validate we caught the header typos
    print("\n\n=== Validation Check ===")

    expected_issues = ['EMPLOYEE_IDD', 'PHONEE']
    issues_fields = [issue.get('field', '') for issue in review_result['issues_found']]

    for expected in expected_issues:
        if expected in issues_fields:
            print(f"[OK] Detected typo in header: {expected}")
        else:
            print(f"[FAIL] Failed to detect typo in header: {expected}")
            return False

    print("\n=== Test Complete ===")
    print("[OK] All validation checks passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_bad_file_upload_and_review()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
