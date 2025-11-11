#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Enhanced Field Mapping Accuracy
Validates improvement from 13.64% to 70%+ accuracy for Siemens fields
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for stdout to handle Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.field_mapper import get_field_mapper
from app.services.schema_manager import get_schema_manager

def test_siemens_field_mapping():
    """Test mapping accuracy with real Siemens candidate fields"""

    print("=" * 80)
    print("ENHANCED FIELD MAPPING ACCURACY TEST")
    print("=" * 80)
    print()

    # Real Siemens candidate fields from test file
    siemens_fields = [
        "PersonID",
        "FirstName",
        "LastName",
        "LastActivityTimeStamp",
        "WorkEmails",
        "HomeEmails",
        "WorkPhones",
        "HomePhones",
        "Salutation",
        "HomeLocation",
        "IsInternal",
        "Summary",
        "Website",
        "Skills",
        "LinkedJobsID",
        "AcceptedDPCS",
        "VisibilityAsCandidate",
        "CountryRegionOfCitizenship",
        "NoticePeriodDateOfAvailability",
        "AnonymizationNEW",
        "DefaultAccountForReceivingEmails",
        "HomeCountry"
    ]

    # Expected mappings (ground truth)
    expected_mappings = {
        "PersonID": "CANDIDATE_ID",
        "FirstName": "FIRST_NAME",
        "LastName": "LAST_NAME",
        "LastActivityTimeStamp": "LAST_ACTIVITY_TS",
        "WorkEmails": "EMAIL",
        "HomeEmails": "EMAIL",
        "WorkPhones": "PHONE",
        "HomePhones": "PHONE",
        "Salutation": None,  # No exact match in candidate schema
        "HomeLocation": None,  # Could map to LOCATION if added
        "IsInternal": None,  # Siemens-specific
        "Summary": None,  # Could map to notes/description if added
        "Website": None,  # Not in candidate schema
        "Skills": None,  # Not in candidate schema
        "LinkedJobsID": None,  # Siemens-specific
        "AcceptedDPCS": None,  # Siemens-specific
        "VisibilityAsCandidate": None,  # Could map to STATUS
        "CountryRegionOfCitizenship": None,  # Not in candidate schema
        "NoticePeriodDateOfAvailability": None,  # Could map to APPLICATION_DATE
        "AnonymizationNEW": None,  # Siemens-specific
        "DefaultAccountForReceivingEmails": None,  # Siemens-specific
        "HomeCountry": None  # Not in candidate schema
    }

    # Get services
    mapper = get_field_mapper()
    schema_manager = get_schema_manager()

    # Load candidate schema
    candidate_schema = schema_manager.get_schema("candidate")

    print(f"Source Schema: Siemens Candidates")
    print(f"Target Schema: {candidate_schema.entity_name}")
    print(f"Total Source Fields: {len(siemens_fields)}")
    print(f"Total Target Fields: {len(candidate_schema.fields)}")
    print()

    # Perform auto-mapping
    mappings = mapper.auto_map(siemens_fields, candidate_schema, min_confidence=0.70)

    print("-" * 80)
    print("MAPPING RESULTS")
    print("-" * 80)
    print()

    # Track results
    correct_mappings = 0
    total_expected_mappings = sum(1 for v in expected_mappings.values() if v is not None)
    mapped_fields = set()

    # Display all mappings
    for mapping in mappings:
        expected = expected_mappings.get(mapping.source)
        is_correct = (expected == mapping.target)
        status = "✓" if is_correct else "✗"

        if is_correct:
            correct_mappings += 1

        mapped_fields.add(mapping.source)

        print(f"{status} {mapping.source:30} → {mapping.target:20} "
              f"(confidence: {mapping.confidence:.2f}, method: {mapping.method})")

        if expected and expected != mapping.target:
            print(f"  ⚠ Expected: {expected}")

        # Show alternatives if available
        if mapping.alternatives:
            print(f"  Alternatives: ", end="")
            for alt in mapping.alternatives[:3]:
                print(f"{alt.target} ({alt.confidence:.2f}), ", end="")
            print()

    print()

    # Show unmapped fields
    unmapped_fields = [f for f in siemens_fields if f not in mapped_fields]
    if unmapped_fields:
        print("-" * 80)
        print("UNMAPPED FIELDS")
        print("-" * 80)
        for field in unmapped_fields:
            expected = expected_mappings.get(field)
            if expected:
                print(f"✗ {field:30} → (NOT MAPPED) - Expected: {expected}")
            else:
                print(f"○ {field:30} → (NOT MAPPED) - No equivalent in target schema")
        print()

    # Calculate metrics
    print("=" * 80)
    print("ACCURACY METRICS")
    print("=" * 80)
    print()

    total_fields = len(siemens_fields)
    mapped_count = len(mappings)
    mapping_rate = (mapped_count / total_fields) * 100

    accuracy = (correct_mappings / total_expected_mappings) * 100 if total_expected_mappings > 0 else 0

    print(f"Total Source Fields:        {total_fields}")
    print(f"Fields Mapped:              {mapped_count} ({mapping_rate:.2f}%)")
    print(f"Expected Mappable Fields:   {total_expected_mappings}")
    print(f"Correct Mappings:           {correct_mappings}")
    print(f"Mapping Accuracy:           {accuracy:.2f}%")
    print()

    # Calculate improvement
    original_accuracy = 13.64
    improvement = accuracy - original_accuracy
    improvement_pct = (improvement / original_accuracy) * 100 if original_accuracy > 0 else 0

    print(f"Original Accuracy:          {original_accuracy:.2f}%")
    print(f"New Accuracy:               {accuracy:.2f}%")
    print(f"Improvement:                +{improvement:.2f} percentage points ({improvement_pct:.1f}% increase)")
    print()

    # Success criteria
    target_accuracy = 70.0
    success = accuracy >= target_accuracy

    print("=" * 80)
    print("SUCCESS CRITERIA")
    print("=" * 80)
    print(f"Target Accuracy:            {target_accuracy}%")
    print(f"Achieved Accuracy:          {accuracy:.2f}%")
    print(f"Status:                     {'✓ PASSED' if success else '✗ FAILED'}")
    print()

    # Detailed breakdown by matching method
    method_counts = {}
    for mapping in mappings:
        method_counts[mapping.method] = method_counts.get(mapping.method, 0) + 1

    if method_counts:
        print("-" * 80)
        print("MATCHING METHOD BREAKDOWN")
        print("-" * 80)
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / mapped_count) * 100
            print(f"{method:15} {count:3} ({pct:5.1f}%)")
        print()

    return success


def test_individual_field_matches():
    """Test specific critical field mappings in detail"""

    print("=" * 80)
    print("CRITICAL FIELD MAPPING TESTS")
    print("=" * 80)
    print()

    mapper = get_field_mapper()

    # Critical test cases
    test_cases = [
        ("PersonID", "CANDIDATE_ID", "ID field mapping"),
        ("WorkEmails", "EMAIL", "Work email mapping"),
        ("WorkPhones", "PHONE", "Work phone mapping"),
        ("HomeEmails", "EMAIL", "Home email mapping"),
        ("HomePhones", "PHONE", "Home phone mapping"),
        ("LastActivityTimeStamp", "LAST_ACTIVITY_TS", "Timestamp mapping"),
        ("FirstName", "FIRST_NAME", "First name mapping"),
        ("LastName", "LAST_NAME", "Last name mapping"),
    ]

    passed = 0
    failed = 0

    for source, expected_target, description in test_cases:
        confidence, method = mapper.calculate_match(source, expected_target)

        # Test passes if confidence >= 0.80
        success = confidence >= 0.80
        status = "✓ PASS" if success else "✗ FAIL"

        if success:
            passed += 1
        else:
            failed += 1

        print(f"{status} {description:30}")
        print(f"   {source:25} → {expected_target:20}")
        print(f"   Confidence: {confidence:.2f}, Method: {method}")
        print()

    print("-" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print()

    return failed == 0


if __name__ == "__main__":
    print()

    # Run individual field tests
    individual_success = test_individual_field_matches()

    print()

    # Run full mapping test
    mapping_success = test_siemens_field_mapping()

    # Exit with appropriate code
    if individual_success and mapping_success:
        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
        sys.exit(0)
    else:
        print("=" * 80)
        print("SOME TESTS FAILED ✗")
        print("=" * 80)
        sys.exit(1)
