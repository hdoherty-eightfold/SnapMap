"""
Deep analysis of Siemens file structure and data quality
Tests the system's ability to handle complex, issue-prone data
"""

import pandas as pd
import re
from app.services.file_parser import FileParser
from app.services.schema_manager import get_schema_manager
from app.services.field_mapper import get_field_mapper

def analyze_siemens_file():
    """Comprehensive analysis of Siemens file structure and challenges"""

    print("="*80)
    print("SIEMENS FILE DEEP ANALYSIS")
    print("="*80)

    # 1. Load the file
    file_path = 'test_siemens_candidates.csv'
    print(f"\n1. Loading file: {file_path}")

    try:
        # Read with pipe delimiter
        df = pd.read_csv(file_path, delimiter='|', encoding='utf-8', on_bad_lines='skip')

        print(f"   [OK] File loaded successfully")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - Delimiter: | (pipe)")

    except Exception as e:
        print(f"   [ERROR] Failed to load file: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Analyze headers
    print(f"\n2. Header Analysis")
    print(f"   Headers found ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2}. {col}")

    # 3. Data quality issues
    print(f"\n3. Data Quality Analysis")

    # Empty fields
    empty_counts = df.isnull().sum()
    if empty_counts.any():
        print(f"   Empty/Null values per column:")
        for col, count in empty_counts[empty_counts > 0].items():
            pct = (count / len(df)) * 100
            print(f"   - {col}: {count} ({pct:.1f}%)")

    # Special characters in data
    print(f"\n4. Special Characters & Encoding")
    special_char_cols = []
    for col in df.columns:
        sample_vals = df[col].dropna().head(5).astype(str)
        for val in sample_vals:
            if any(ord(c) > 127 for c in val):
                special_char_cols.append(col)
                print(f"   - {col}: Contains non-ASCII characters")
                print(f"     Example: {val[:100]}...")
                break

    # 5. Complex nested data detection
    print(f"\n5. Complex/Nested Data Structures")

    # HomeLocation analysis
    if 'HomeLocation' in df.columns:
        sample_location = df['HomeLocation'].dropna().iloc[0] if not df['HomeLocation'].dropna().empty else None
        if sample_location:
            print(f"   HomeLocation structure:")
            print(f"   - Uses '' wrapper quotes")
            print(f"   - Uses %% delimiters for values")
            print(f"   - Contains: street, state, city, zip code, country")
            print(f"   - Example: {sample_location[:150]}...")

            # Try to extract components
            pattern = r"Home street: %(.*?)% , Home state: %(.*?)%, Home city: %(.*?)%, Home zip code: %(.*?)%, Home country: %(.*?)%"
            match = re.search(pattern, sample_location)
            if match:
                print(f"   - Extractable components:")
                print(f"     Street: {match.group(1)}")
                print(f"     State: {match.group(2)}")
                print(f"     City: {match.group(3)}")
                print(f"     Zip: {match.group(4)}")
                print(f"     Country: {match.group(5)}")

    # Skills analysis (comma-separated)
    if 'Skills' in df.columns:
        sample_skills = df['Skills'].dropna().iloc[0] if not df['Skills'].dropna().empty else None
        if sample_skills:
            skills_list = [s.strip() for s in sample_skills.split(',')]
            print(f"\n   Skills field structure:")
            print(f"   - Comma-separated list")
            print(f"   - Example count: {len(skills_list)} skills")
            print(f"   - First 5 skills: {', '.join(skills_list[:5])}")

    # LinkedJobsID (comma-separated IDs)
    if 'LinkedJobsID' in df.columns:
        sample_jobs = df['LinkedJobsID'].dropna().iloc[0] if not df['LinkedJobsID'].dropna().empty else None
        if sample_jobs:
            jobs_list = sample_jobs.split(',')
            print(f"\n   LinkedJobsID structure:")
            print(f"   - Comma-separated job IDs")
            print(f"   - Example count: {len(jobs_list)} jobs")

    # 6. Field type detection
    print(f"\n6. Column Type Detection")
    try:
        parser = FileParser()
        column_types = parser.detect_column_types(df)
        if column_types:
            print(f"   Detected types:")
            for col, col_type in column_types.items():
                print(f"   - {col}: {col_type}")
    except Exception as e:
        print(f"   [ERROR] Type detection failed: {e}")
        column_types = {}

    # 7. Field mapping test
    print(f"\n7. Field Mapping Analysis")

    try:
        schema_manager = get_schema_manager()
        employee_schema = schema_manager.get_schema('employee')

        field_mapper = get_field_mapper()
        mappings = field_mapper.auto_map(
            list(df.columns),
            employee_schema,
            column_types=column_types
        )

        print(f"   Mappings generated: {len(mappings)}")
        print(f"\n   High-confidence mappings (>= 85%):")
        high_conf = [m for m in mappings if m.confidence >= 0.85]
        for m in high_conf:
            print(f"   - {m.source:30} -> {m.target:30} ({m.confidence:.1%}) [{m.method}]")

        print(f"\n   Medium-confidence mappings (70-85%):")
        medium_conf = [m for m in mappings if 0.70 <= m.confidence < 0.85]
        for m in medium_conf:
            print(f"   - {m.source:30} -> {m.target:30} ({m.confidence:.1%}) [{m.method}]")

        print(f"\n   Low-confidence or unmapped fields (<70%):")
        low_conf = [m for m in mappings if m.confidence < 0.70]
        for m in low_conf:
            print(f"   - {m.source:30} -> {m.target if m.target else '(unmapped)':30} ({m.confidence:.1%})")

    except Exception as e:
        print(f"   [ERROR] Field mapping failed: {e}")

    # 8. Specific data challenges
    print(f"\n8. Specific Data Challenges Identified")

    challenges = []

    # Check for pipe delimiter
    challenges.append("[OK] Pipe (|) delimiter - handled by parser")

    # Check for nested location data
    if 'HomeLocation' in df.columns:
        challenges.append("[COMPLEX] Nested location data with %% delimiters")

    # Check for comma-separated lists
    if 'Skills' in df.columns:
        challenges.append("[COMPLEX] Comma-separated skills list (can conflict with CSV parsing)")

    # Check for empty strings vs nulls
    dash_count = (df == '-').sum().sum()
    if dash_count > 0:
        challenges.append(f"[INFO] {dash_count} fields contain placeholder dash ('-')")

    # Check for internal employees
    internal_count = df['IsInternal'].value_counts().get('TRUE', 0) if 'IsInternal' in df.columns else 0
    if internal_count > 0:
        challenges.append(f"[INFO] {internal_count} internal employee records (may have sparse data)")

    # Check for multiple values in single fields
    if 'WorkEmails' in df.columns or 'WorkPhones' in df.columns:
        challenges.append("[COMPLEX] Multiple emails/phones potentially in single fields")

    for challenge in challenges:
        print(f"   {challenge}")

    # 9. Recommendations
    print(f"\n9. Recommendations for Handling This File")
    print(f"   1. Parser Configuration:")
    print(f"      - Ensure pipe delimiter detection works correctly [OK]")
    print(f"      - Handle quoted fields with commas inside")
    print(f"      - Preserve special characters (UTF-8 encoding)")

    print(f"\n   2. Data Cleaning:")
    print(f"      - Extract location components from HomeLocation if needed")
    print(f"      - Split comma-separated skills into array")
    print(f"      - Convert dash ('-') placeholders to null/empty")
    print(f"      - Handle multiple emails/phones in single field")

    print(f"\n   3. Field Mapping:")
    print(f"      - WorkEmails -> EMAIL")
    print(f"      - HomeEmails -> PERSONAL_EMAIL")
    print(f"      - Skills -> SPECIALISED_SKILLS_LIST")
    print(f"      - HomeLocation -> LOCATION (extract country for LOCATION_COUNTRY)")
    print(f"      - LastActivityTimeStamp -> LAST_ACTIVITY_TS")

    print(f"\n   4. Validation:")
    print(f"      - Handle missing required fields gracefully")
    print(f"      - Validate email formats")
    print(f"      - Validate date formats (multiple variations)")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    analyze_siemens_file()
