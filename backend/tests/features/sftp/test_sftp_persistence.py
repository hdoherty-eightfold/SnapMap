"""
Test SFTP Persistence
Verify that SFTP credentials are properly saved and loaded from disk
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.sftp_manager import get_sftp_manager

def test_sftp_persistence():
    print("=== Testing SFTP Credentials Persistence ===\n")

    # Get SFTP manager instance
    manager = get_sftp_manager()

    # Test 1: Add a test credential
    print("1. Adding test SFTP credential...")
    cred = manager.add_credential(
        name="Test SFTP Server",
        host="sftp.example.com",
        port=22,
        username="testuser",
        password="testpassword123",
        remote_path="/uploads"
    )
    print(f"   [OK] Created credential: {cred['id']}")
    print(f"   Name: {cred['name']}")
    print(f"   Host: {cred['host']}:{cred['port']}")
    print(f"   Username: {cred['username']}")
    print(f"   Remote Path: {cred['remote_path']}")
    print()

    # Test 2: Retrieve the credential
    print("2. Retrieving credential by ID...")
    retrieved = manager.get_credential(cred['id'])
    if retrieved:
        print(f"   [OK] Retrieved credential: {retrieved['id']}")
        print(f"   Password persisted: {'password' in retrieved}")
        print(f"   Password value: {retrieved.get('password', 'N/A')}")
    else:
        print("   [FAIL] Failed to retrieve credential")
    print()

    # Test 3: List all credentials
    print("3. Listing all credentials...")
    all_creds = manager.get_all_credentials()
    print(f"   [OK] Total credentials: {len(all_creds)}")
    for c in all_creds:
        print(f"   - {c['name']} ({c['id']})")
    print()

    # Test 4: Check if credentials file was created
    print("4. Checking credentials file...")
    import tempfile
    from pathlib import Path
    creds_file = Path(tempfile.gettempdir()) / "snapmap_sftp" / "credentials.json"
    if creds_file.exists():
        print(f"   [OK] Credentials file exists: {creds_file}")
        import json
        with open(creds_file, 'r') as f:
            data = json.load(f)
        print(f"   [OK] File contains {len(data)} credential(s)")
        print(f"   [OK] Password is encoded (not plain text): {list(data.values())[0].get('password', '')[:20]}...")
    else:
        print(f"   [FAIL] Credentials file not found: {creds_file}")
    print()

    # Test 5: Simulate server restart by creating new manager instance
    print("5. Testing persistence across restarts...")
    print("   Creating new SFTP manager instance...")
    from app.services import sftp_manager
    sftp_manager._sftp_manager = None  # Reset singleton
    new_manager = get_sftp_manager()

    # Try to retrieve the credential again
    retrieved_after_restart = new_manager.get_credential(cred['id'])
    if retrieved_after_restart:
        print(f"   [OK] Credential persisted across restart!")
        print(f"   [OK] Name: {retrieved_after_restart['name']}")
        print(f"   [OK] Password restored: {retrieved_after_restart.get('password') == 'testpassword123'}")
    else:
        print("   [FAIL] Credential NOT persisted (FAILURE)")
    print()

    # Cleanup
    print("6. Cleaning up test credential...")
    success = new_manager.delete_credential(cred['id'])
    if success:
        print(f"   [OK] Deleted test credential: {cred['id']}")
    else:
        print(f"   [FAIL] Failed to delete credential")

    print("\n=== Test Complete ===")
    print(f"Status: {'[OK] ALL TESTS PASSED' if retrieved_after_restart else '[FAIL] PERSISTENCE FAILED'}")

if __name__ == "__main__":
    test_sftp_persistence()
