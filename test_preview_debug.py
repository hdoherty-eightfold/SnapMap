"""
Test script to debug the preview transformation issue
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_preview_with_file_id():
    """Test the preview endpoint with file_id parameter"""

    # Mock request data as the frontend would send it
    request_data = {
        "mappings": [
            {
                "source": "name",
                "target": "NAME",
                "confidence": 0.95,
                "method": "exact"
            },
            {
                "source": "email",
                "target": "EMAIL",
                "confidence": 0.95,
                "method": "exact"
            }
        ],
        "file_id": "test-file-id",  # This would be a real file_id from upload
        "entity_name": "employee",
        "sample_size": 50
    }

    print("=" * 80)
    print("TESTING /transform/preview ENDPOINT")
    print("=" * 80)
    print("\nRequest payload:")
    print(json.dumps(request_data, indent=2))

    # Send request
    response = requests.post(
        f"{BASE_URL}/transform/preview",
        json=request_data,
        timeout=30
    )

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")

    try:
        response_data = response.json()
        print("\nResponse Body:")
        print(json.dumps(response_data, indent=2))
    except Exception as e:
        print(f"\nCouldn't parse response as JSON: {e}")
        print(f"Raw response: {response.text}")

    return response


def test_preview_without_source_data():
    """Test what happens when source_data is None"""

    request_data = {
        "mappings": [
            {
                "source": "name",
                "target": "NAME",
                "confidence": 0.95,
                "method": "exact"
            }
        ],
        "file_id": "some-file-id",
        "entity_name": "employee",
        "sample_size": 5
        # Note: source_data is intentionally omitted
    }

    print("\n" + "=" * 80)
    print("TESTING WITH file_id BUT NO source_data")
    print("=" * 80)
    print("\nRequest payload:")
    print(json.dumps(request_data, indent=2))

    response = requests.post(
        f"{BASE_URL}/transform/preview",
        json=request_data,
        timeout=30
    )

    print(f"\nResponse Status: {response.status_code}")

    try:
        response_data = response.json()
        print("\nResponse Body:")
        print(json.dumps(response_data, indent=2))
    except Exception as e:
        print(f"\nCouldn't parse response as JSON: {e}")
        print(f"Raw response: {response.text}")

    return response


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("PREVIEW TRANSFORMATION DEBUG TEST")
    print("=" * 80)

    # Test 1: With file_id (simulating real frontend behavior)
    try:
        response1 = test_preview_without_source_data()
    except Exception as e:
        print(f"\n[ERROR] Test 1 failed with exception: {e}")

    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print("""
The issue is that the /transform/preview endpoint does NOT handle file_id properly.

Looking at the code:
1. Frontend sends: file_id + mappings + entity_name (NO source_data)
2. Backend /transform/preview (line 42): Calls engine.transform_data(request.source_data, ...)
3. Since source_data is None, transform_data receives None
4. TransformationEngine.transform_data creates DataFrame from None
5. pd.DataFrame(None) creates an EMPTY DataFrame with 0 rows
6. Result: 0 output rows

Compare to /transform/export endpoint (lines 107-125):
- It CHECKS if source_data is None
- If None, it retrieves data from file_id using storage.retrieve_dataframe()
- Then transforms the actual data

ROOT CAUSE:
The /transform/preview endpoint is missing the file_id retrieval logic that exists
in the /transform/export endpoint.
""")
