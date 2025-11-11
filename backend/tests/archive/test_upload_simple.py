"""
Test script to upload a sample file and test the review endpoint
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api"

def test_upload():
    """Test file upload"""
    print("=" * 60)
    print("Testing File Upload")
    print("=" * 60)

    # Path to sample file
    sample_file = Path(__file__).parent / "frontend" / "public" / "samples" / "employee_sample_1.csv"

    if not sample_file.exists():
        print(f"[ERROR] Sample file not found: {sample_file}")
        return None

    print(f"[OK] Found sample file: {sample_file.name}")

    # Upload file
    with open(sample_file, 'rb') as f:
        files = {'file': (sample_file.name, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] Upload successful!")
        print(f"   File ID: {data['file_id']}")
        print(f"   Rows: {data['row_count']}")
        print(f"   Columns: {data['column_count']}")
        print(f"   Fields: {', '.join(data['columns'][:5])}...")
        return data
    else:
        print(f"[ERROR] Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_review(file_id, entity_name="employee"):
    """Test file review endpoint"""
    print("\n" + "=" * 60)
    print("Testing File Review (AI Analysis)")
    print("=" * 60)

    payload = {
        "file_id": file_id,
        "entity_name": entity_name,
        "include_suggestions": True
    }

    print(f"Analyzing file with AI (this may take 5-10 seconds)...")

    try:
        response = requests.post(
            f"{BASE_URL}/review/file",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Review completed!")
            print(f"\nSummary:")
            print(f"   Total Issues: {data['total_issues']}")
            print(f"   Critical: {data['critical_issues']}")
            print(f"   Warnings: {data['warnings']}")
            print(f"   Can Auto-Fix: {'Yes' if data['can_auto_fix'] else 'No'}")
            print(f"\nAI Summary:")
            print(f"   {data['summary']}")

            if data['issues_found']:
                print(f"\nIssues Found:")
                for i, issue in enumerate(data['issues_found'][:5], 1):
                    print(f"   {i}. [{issue['severity'].upper()}] {issue['type']} - {issue['field']}")
                    print(f"      {issue['description']}")

            if data['suggestions']:
                print(f"\nSuggestions:")
                for i, suggestion in enumerate(data['suggestions'][:5], 1):
                    confidence_pct = int(suggestion['confidence'] * 100)
                    fixable = "Auto-fixable" if suggestion['auto_fixable'] else "Manual"
                    print(f"   {i}. {suggestion['field']} -> {suggestion['target_field']}")
                    print(f"      Confidence: {confidence_pct}% | {fixable}")

            return data
        else:
            print(f"[ERROR] Review failed: {response.status_code}")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"   Error: {error_data['error'].get('message', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] Request timed out (AI analysis taking too long)")
        print(f"   This may happen if:")
        print(f"   - Gemini API key is not configured")
        print(f"   - Network issues")
        print(f"   - Large file processing")
        return None
    except Exception as e:
        print(f"[ERROR] Error during review: {str(e)}")
        return None

def test_config():
    """Test configuration endpoint"""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Configuration loaded")
            print(f"   Vector DB: {data['vector_db']['type']}")
            print(f"   AI Provider: {data['ai_inference']['provider']}")
            print(f"   AI Enabled: {data['ai_inference']['enabled']}")
            print(f"\nAPI Keys Configured:")
            print(f"   Gemini: {'Yes' if data['api_keys']['gemini_configured'] else 'No'}")
            print(f"   OpenAI: {'Yes' if data['api_keys']['openai_configured'] else 'No'}")

            if not data['api_keys']['gemini_configured']:
                print(f"\n[WARNING] Gemini API key not configured")
                print(f"   AI-powered review features may not work")
                print(f"   Configure in Settings or backend/.env file")

            return data
        else:
            print(f"[ERROR] Configuration check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Error checking config: {str(e)}")
        return None

def main():
    print("\n" + "=" * 60)
    print("SnapMap - End-to-End Test")
    print("=" * 60 + "\n")

    # Test configuration
    config = test_config()

    # Test upload
    upload_result = test_upload()

    if not upload_result:
        print("\n[FAILED] Upload test failed. Stopping tests.")
        return

    # Test review
    review_result = test_review(upload_result['file_id'])

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Upload: {'Success' if upload_result else 'Failed'}")
    print(f"Config: {'Success' if config else 'Failed'}")
    print(f"Review: {'Success' if review_result else 'Failed'}")

    if not review_result and config and not config['api_keys']['gemini_configured']:
        print(f"\n[NOTE] Review failed because Gemini API key is not configured")
        print(f"   To fix: Add GEMINI_API_KEY to backend/.env")

    print("\nTest completed!\n")

if __name__ == "__main__":
    main()
