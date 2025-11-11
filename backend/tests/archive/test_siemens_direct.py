"""
Direct test of Siemens file processing without API
"""

import pandas as pd
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

TEST_FILE = r"c:\Code\SnapMap\backend\test_siemens_candidates.csv"

print("="*80)
print("DIRECT SIEMENS FILE PROCESSING TEST")
print("="*80)

# Test 1: Load with pandas using engine='python'
print("\n[TEST 1] Loading with pandas (engine='python', on_bad_lines='skip')...")
try:
    df = pd.read_csv(
        TEST_FILE,
        delimiter='|',
        encoding='utf-8',
        on_bad_lines='skip',
        engine='python'
    )
    print(f"[OK] Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"[OK] Columns: {df.columns.tolist()[:5]}...")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 2: Load without skip to see the error
print("\n[TEST 2] Loading with pandas (engine='python', on_bad_lines='warn')...")
try:
    df2 = pd.read_csv(
        TEST_FILE,
        delimiter='|',
        encoding='utf-8',
        on_bad_lines='warn',
        engine='python'
    )
    print(f"[OK] Loaded {len(df2)} rows, {len(df2.columns)} columns")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 3: Load with default C engine
print("\n[TEST 3] Loading with pandas (default C engine)...")
try:
    df3 = pd.read_csv(
        TEST_FILE,
        delimiter='|',
        encoding='utf-8'
    )
    print(f"[OK] Loaded {len(df3)} rows, {len(df3.columns)} columns")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {str(e)[:200]}")

# Test 4: Load with quoting
print("\n[TEST 4] Loading with pandas (with quoting and escaping)...")
try:
    df4 = pd.read_csv(
        TEST_FILE,
        delimiter='|',
        encoding='utf-8',
        quoting=3,  # QUOTE_NONE
        engine='python'
    )
    print(f"[OK] Loaded {len(df4)} rows, {len(df4.columns)} columns")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {str(e)[:200]}")

# Test 5: Check if specific test cases are preserved
print("\n[TEST 5] Checking special characters...")
if 'df' in locals():
    # Check Turkish characters
    turkey_found = df[df['HomeCountry'].str.contains('Türkiye', na=False)] if 'HomeCountry' in df.columns else pd.DataFrame()
    print(f"[INFO] Rows with 'Türkiye': {len(turkey_found)}")

    # Check Spanish characters
    if 'HomeLocation' in df.columns:
        torreon_found = df[df['HomeLocation'].str.contains('Torreón', na=False, regex=False)]
        print(f"[INFO] Rows with 'Torreón': {len(torreon_found)}")

    # Check specific candidates
    if 'FirstName' in df.columns and 'LastName' in df.columns:
        tarik = df[(df['FirstName'] == 'Tarik Uveys') & (df['LastName'] == 'Sen')]
        print(f"[INFO] Tarik Uveys Sen found: {len(tarik) > 0}")

        esra = df[(df['FirstName'] == 'Esra') & (df['LastName'] == 'Kayır')]
        print(f"[INFO] Esra Kayır found: {len(esra) > 0}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
