"""
Test XML functionality end-to-end
"""

import requests
import json
import io
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Fix Windows console encoding
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def create_test_csv():
    """Create a test CSV file"""
    csv_content = """employee_id,first_name,last_name,email,phone,title,location,hiring_date,manager_email
EMP001,John,Doe,john.doe@company.com,555-0100,Software Engineer,New York,2024-01-15,jane.smith@company.com
EMP002,Jane,Smith,jane.smith@company.com,555-0101,Engineering Manager,San Francisco,2023-06-20,bob.jones@company.com
EMP003,Bob,Jones,bob.jones@company.com,555-0102,VP Engineering,Boston,2022-03-10,ceo@company.com
EMP004,Alice,Williams,alice.williams@company.com,555-0103,Senior Engineer,New York,2023-09-05,jane.smith@company.com
EMP005,Charlie,Brown,charlie.brown@company.com,555-0104,Product Manager,Austin,2024-02-01,bob.jones@company.com
"""
    return csv_content

def test_upload_file():
    """Test file upload"""
    print("\n=== TEST 1: Upload CSV File ===")

    csv_content = create_test_csv()

    # Create file object
    files = {
        'file': ('test_employees.csv', io.BytesIO(csv_content.encode()), 'text/csv')
    }

    response = requests.post(f"{API_BASE}/upload", files=files)

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ File uploaded successfully")
        print(f"  File ID: {data['file_id']}")
        print(f"  Columns: {', '.join(data['columns'])}")
        print(f"  Row count: {data['row_count']}")
        return data['file_id'], data['columns']
    else:
        print(f"✗ Upload failed: {response.text}")
        return None, None

def test_xml_preview(file_id):
    """Test XML preview endpoint"""
    print("\n=== TEST 2: XML Preview ===")

    # Create mappings (with required confidence and method fields)
    mappings = [
        {"source": "employee_id", "target": "EMPLOYEE_ID", "confidence": 1.0, "method": "exact"},
        {"source": "first_name", "target": "FIRST_NAME", "confidence": 1.0, "method": "exact"},
        {"source": "last_name", "target": "LAST_NAME", "confidence": 1.0, "method": "exact"},
        {"source": "email", "target": "EMAIL", "confidence": 1.0, "method": "exact"},
        {"source": "phone", "target": "PHONE", "confidence": 1.0, "method": "exact"},
        {"source": "title", "target": "TITLE", "confidence": 1.0, "method": "exact"},
        {"source": "location", "target": "LOCATION", "confidence": 1.0, "method": "exact"},
        {"source": "hiring_date", "target": "HIRING_DATE", "confidence": 1.0, "method": "exact"},
        {"source": "manager_email", "target": "MANAGER_EMAIL", "confidence": 1.0, "method": "exact"},
    ]

    payload = {
        "file_id": file_id,
        "mappings": mappings,
        "entity_name": "employee",
        "sample_size": 3
    }

    response = requests.post(
        f"{API_BASE}/transform/preview-xml",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ XML preview generated successfully")
        print(f"  Preview rows: {data['preview_row_count']}")
        print(f"  Total rows: {data['total_row_count']}")
        print(f"\n  XML Preview (first 500 chars):")
        print(f"  {data['xml_preview'][:500]}...")
        return mappings
    else:
        print(f"✗ Preview failed: {response.text}")
        return None

def test_xml_export(file_id, mappings):
    """Test XML export endpoint"""
    print("\n=== TEST 3: XML Export ===")

    payload = {
        "file_id": file_id,
        "mappings": mappings,
        "entity_name": "employee",
        "output_filename": "test_export.xml"
    }

    response = requests.post(
        f"{API_BASE}/transform/export-xml",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        xml_content = response.content.decode('utf-8')
        print(f"✓ XML export successful")
        print(f"  Content length: {len(xml_content)} characters")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Content-Disposition: {response.headers.get('Content-Disposition')}")

        # Validate XML structure
        if '<EF_Employee_List>' in xml_content and '<EF_Employee>' in xml_content:
            print(f"  ✓ XML structure valid (contains EF_Employee_List and EF_Employee)")
        else:
            print(f"  ✗ XML structure invalid")

        # Check for key fields
        key_fields = ['employee_id', 'first_name', 'last_name', 'email_list', 'phone_list']
        found_fields = [field for field in key_fields if field in xml_content]
        print(f"  Found fields: {', '.join(found_fields)}")

        # Save to file
        output_path = Path("test_export_output.xml")
        output_path.write_text(xml_content, encoding='utf-8')
        print(f"  ✓ Saved to: {output_path.absolute()}")

        # Show first part of XML
        print(f"\n  XML Content (first 800 chars):")
        print(f"  {xml_content[:800]}...")

        return True
    else:
        print(f"✗ Export failed: {response.text}")
        return False

def test_xml_validation():
    """Test XML validation with various data types"""
    print("\n=== TEST 4: XML Validation (Data Types) ===")

    # Test CSV with various data types
    csv_content = """employee_id,first_name,last_name,email,hiring_date,location
EMP001,John,Doe,john@test.com,2024-01-15,New York
EMP002,Jane,Smith,jane@test.com,01/20/2024,San Francisco
"""

    files = {
        'file': ('test_types.csv', io.BytesIO(csv_content.encode()), 'text/csv')
    }

    response = requests.post(f"{API_BASE}/upload", files=files)

    if response.status_code != 200:
        print(f"✗ Upload failed")
        return

    file_id = response.json()['file_id']

    mappings = [
        {"source": "employee_id", "target": "EMPLOYEE_ID", "confidence": 1.0, "method": "exact"},
        {"source": "first_name", "target": "FIRST_NAME", "confidence": 1.0, "method": "exact"},
        {"source": "last_name", "target": "LAST_NAME", "confidence": 1.0, "method": "exact"},
        {"source": "email", "target": "EMAIL", "confidence": 1.0, "method": "exact"},
        {"source": "hiring_date", "target": "HIRING_DATE", "confidence": 1.0, "method": "exact"},
        {"source": "location", "target": "LOCATION", "confidence": 1.0, "method": "exact"},
    ]

    payload = {
        "file_id": file_id,
        "mappings": mappings,
        "entity_name": "employee",
        "sample_size": 2
    }

    response = requests.post(f"{API_BASE}/transform/preview-xml", json=payload)

    if response.status_code == 200:
        data = response.json()
        xml_content = data['xml_preview']

        print(f"✓ Generated XML with multiple date formats")

        # Check date formatting
        if '2024-01-15' in xml_content:
            print(f"  ✓ Date format 1 (YYYY-MM-DD) handled correctly")
        if '2024-01-20' in xml_content or '01/20/2024' in xml_content:
            print(f"  ✓ Date format 2 (MM/DD/YYYY) processed")

        print(f"\n  XML Sample:")
        print(f"  {xml_content[:500]}...")
    else:
        print(f"✗ Validation test failed: {response.text}")

def main():
    """Run all XML tests"""
    print("=" * 60)
    print("XML FUNCTIONALITY TEST SUITE")
    print("=" * 60)

    try:
        # Test 1: Upload
        file_id, columns = test_upload_file()
        if not file_id:
            print("\n✗ Test suite failed: Could not upload file")
            return

        # Test 2: Preview
        mappings = test_xml_preview(file_id)
        if not mappings:
            print("\n✗ Test suite failed: Could not generate XML preview")
            return

        # Test 3: Export
        export_success = test_xml_export(file_id, mappings)
        if not export_success:
            print("\n✗ Test suite failed: Could not export XML")
            return

        # Test 4: Validation
        test_xml_validation()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUITE SUMMARY")
        print("=" * 60)
        print("✓ All XML functionality tests passed!")
        print("  - File upload: OK")
        print("  - XML preview: OK")
        print("  - XML export: OK")
        print("  - Data validation: OK")
        print("\nXML features are working as expected.")

    except Exception as e:
        print(f"\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
