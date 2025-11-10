"""
Complete Workflow Testing
Tests the entire SnapMap workflow with both employee sample files
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.schema_manager import get_schema_manager
from app.services.field_mapper import FieldMapper
from app.services.xml_transformer import XMLTransformer


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def test_sample_file(sample_name, csv_path, entity_name="employee"):
    """Test complete workflow for a sample file"""
    print_header(f"Testing {sample_name}")

    # Step 1: Load schema
    print(f"\n[1/4] Loading {entity_name} schema...")
    schema_manager = get_schema_manager()
    schema = schema_manager.get_schema(entity_name)
    print(f"  [OK] Schema loaded: {len(schema.fields)} fields")

    # Step 2: Load CSV
    print(f"\n[2/4] Loading CSV: {csv_path.name}")
    if not csv_path.exists():
        print(f"  [ERROR] File not found: {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    print(f"  [OK] Loaded {len(df)} records")
    print(f"  [OK] CSV has {len(df.columns)} columns")
    print(f"  Columns: {', '.join(df.columns)}")

    # Show first record
    print(f"\n  First Record:")
    for col in df.columns:
        print(f"    {col}: {df[col].iloc[0]}")

    # Step 3: Auto-mapping
    print(f"\n[3/4] Auto-mapping fields...")
    field_mapper = FieldMapper()

    mappings = field_mapper.auto_map(
        source_fields=list(df.columns),
        target_schema=schema,
        min_confidence=0.60
    )

    mapping_rate = (len(mappings) / len(df.columns) * 100) if len(df.columns) > 0 else 0
    print(f"  [OK] Mapped {len(mappings)}/{len(df.columns)} fields ({mapping_rate:.1f}%)")

    print(f"\n  Mappings:")
    for i, mapping in enumerate(mappings, 1):
        print(f"    {i}. '{mapping.source}' -> '{mapping.target}' (confidence: {mapping.confidence:.2f})")

    # Check unmapped
    unmapped = [f for f in df.columns if f not in [m.source for m in mappings]]
    if unmapped:
        print(f"\n  Unmapped fields: {', '.join(unmapped)}")

    # Step 4: XML Transformation
    print(f"\n[4/4] Transforming to XML...")
    transformer = XMLTransformer()

    mapping_dict = [{"source": m.source, "target": m.target} for m in mappings]

    try:
        xml_output = transformer.transform_csv_to_xml(
            df=df,
            mappings=mapping_dict,
            entity_name=entity_name
        )

        xml_lines = xml_output.split('\n')
        element_count = len([l for l in xml_lines if '<' in l and '>' in l])

        print(f"  [OK] XML generated")
        print(f"  - Total lines: {len(xml_lines)}")
        print(f"  - Total elements: {element_count}")
        print(f"  - Records transformed: {len(df)}")

        # Verify XML structure
        checks = [
            ("XML declaration", "<?xml version"),
            ("Root element", f"<EF_{entity_name.title()}_List>"),
            ("Entity element", f"<EF_{entity_name.title()}>"),
        ]

        print(f"\n  XML Structure:")
        for check_name, check_string in checks:
            status = "[OK]" if check_string.lower() in xml_output.lower() else "[ERROR]"
            print(f"    {status} {check_name}")

        # Show sample XML
        print(f"\n  Sample XML (first 20 lines):")
        for i, line in enumerate(xml_lines[:20], 1):
            print(f"    {i:3d}: {line}")

        # Save output
        output_file = backend_dir / f"test_output_{sample_name.lower().replace(' ', '_')}.xml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_output)
        print(f"\n  [OK] XML saved to: {output_file.name}")

        # Verify data integrity - check if first record data appears in XML
        first_id = str(df.iloc[0][df.columns[0]])  # First column value of first record
        if first_id in xml_output:
            print(f"  [OK] Data integrity verified (found: {first_id})")
        else:
            print(f"  [WARNING] Could not verify data integrity")

        return True

    except Exception as e:
        print(f"  [ERROR] XML transformation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all workflow tests"""
    print("=" * 80)
    print("  SNAPMAP COMPLETE WORKFLOW TEST")
    print("  Testing with multiple sample files")
    print("=" * 80)

    results = {}

    # Test files
    test_files = [
        ("Employee Sample 1 (10 records)",
         Path(__file__).parent.parent / "frontend/public/samples/employee_sample_1.csv"),
        ("Employee Sample 2 (5 records)",
         Path(__file__).parent.parent / "frontend/public/samples/employee_sample_2.csv"),
    ]

    for sample_name, csv_path in test_files:
        success = test_sample_file(sample_name, csv_path, "employee")
        results[sample_name] = success

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTests Run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    print("\nResults:")
    for name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {name}")

    if passed == total:
        print("\n" + "=" * 80)
        print("  ALL TESTS PASSED!")
        print("  SnapMap workflow is working correctly")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("  SOME TESTS FAILED")
        print("  Please review errors above")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
