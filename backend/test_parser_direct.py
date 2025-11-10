"""
Direct test of file parser
"""

import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

from app.services.file_parser import FileParser

TEST_FILE = r"c:\Code\SnapMap\backend\test_siemens_candidates.csv"

print("="*80)
print("DIRECT FILE PARSER TEST")
print("="*80)

# Read file
with open(TEST_FILE, 'rb') as f:
    file_content = f.read()

print(f"\n[INFO] File size: {len(file_content)} bytes")

# Create parser
parser = FileParser()

# Try to parse
try:
    print("\n[TEST] Parsing file...")
    df, metadata = parser.parse_file(file_content, "test_siemens_candidates.csv")

    print(f"[OK] Parsed successfully!")
    print(f"[INFO] Rows: {len(df)}")
    print(f"[INFO] Columns: {len(df.columns)}")
    print(f"[INFO] Detected delimiter: {metadata.get('detected_delimiter')}")
    print(f"[INFO] Detected encoding: {metadata.get('detected_encoding')}")
    print(f"[INFO] Column names: {df.columns.tolist()[:5]}...")

    # Check for special characters
    if 'HomeCountry' in df.columns:
        turkey_count = len(df[df['HomeCountry'].str.contains('Türkiye', na=False, regex=False)])
        print(f"[INFO] Rows with 'Türkiye': {turkey_count}")

except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
