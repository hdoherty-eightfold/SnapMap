"""Quick test to verify semantic mapping fix"""
import requests
import json

url = "http://localhost:8000/api/auto-map"
data = {
    "source_fields": ["Worker_ID", "Legal_First_Name", "Legal_Last_Name", "Email_Address"],
    "target_schema": "employee",
    "min_confidence": 0.7
}

print("Testing auto-map API endpoint...")
response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\nSuccess! Mapped {result['total_mapped']} fields")
    print("\nMappings:")
    for mapping in result['mappings']:
        print(f"  {mapping['source']} -> {mapping['target']} (confidence: {mapping['confidence']:.2f}, method: {mapping['method']})")

    # Check if semantic method is present
    semantic_count = sum(1 for m in result['mappings'] if m['method'] == 'semantic')
    print(f"\nSemantic mappings: {semantic_count}/{result['total_mapped']}")

    if semantic_count > 0:
        print("\n✓ VALIDATION ERROR FIXED! Semantic method is now accepted.")
    else:
        print("\n⚠ Semantic method not used (fallback to fuzzy)")
else:
    print(f"Error: {response.text}")
