"""
Comprehensive QA Test Script for Siemens Candidates File
Tests: Upload, Mapping, Validation, Character Encoding, XML Transformation
"""

import requests
import json
import csv
import time
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
CSV_FILE = "test_siemens_candidates.csv"
RESULTS_FILE = "siemens_qa_results.json"

class SiemensQATest:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "issues": [],
            "summary": {}
        }
        self.issues = []
        self.uploaded_file_id = None
        self.mapping_id = None

    def log_issue(self, category, severity, description, details=None):
        """Log an issue found during testing"""
        issue = {
            "category": category,
            "severity": severity,
            "description": description,
            "details": details or {}
        }
        self.issues.append(issue)
        print(f"[{severity}] {category}: {description}")

    def test_1_file_analysis(self):
        """Test 1: Analyze file structure and encoding"""
        print("\n=== TEST 1: FILE ANALYSIS ===")
        test_results = {
            "status": "running",
            "findings": []
        }

        try:
            # Check file exists
            if not Path(CSV_FILE).exists():
                self.log_issue("File Analysis", "CRITICAL",
                             "Siemens CSV file not found", {"path": CSV_FILE})
                test_results["status"] = "failed"
                return test_results

            # Try different encodings
            encodings_tested = {}
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'utf-8-sig']:
                try:
                    with open(CSV_FILE, 'r', encoding=encoding) as f:
                        content = f.read()
                        encodings_tested[encoding] = "SUCCESS"

                    # Check for special characters
                    special_chars = ['ü', 'ö', 'é', 'ñ', 'á', 'ı', 'İ']
                    found_chars = {char: char in content for char in special_chars}
                    test_results["findings"].append({
                        "encoding": encoding,
                        "special_chars": found_chars
                    })

                except Exception as e:
                    encodings_tested[encoding] = f"FAILED: {str(e)}"

            test_results["encodings"] = encodings_tested

            # Analyze structure
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                headers = first_line.strip().split('|')
                total_lines = sum(1 for _ in f) + 1  # +1 for first line already read

            test_results["structure"] = {
                "delimiter": "|",
                "header_count": len(headers),
                "headers": headers[:5],  # First 5 headers
                "total_lines": total_lines,
                "total_records": total_lines - 1
            }

            # Check for malformed rows
            malformed_rows = []
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='|')
                header = next(reader)
                expected_cols = len(header)

                for i, row in enumerate(reader, 2):  # Start at 2 (line after header)
                    if len(row) != expected_cols:
                        malformed_rows.append({
                            "line": i,
                            "expected": expected_cols,
                            "actual": len(row)
                        })
                        if len(malformed_rows) <= 5:  # Log first 5
                            self.log_issue("File Analysis", "HIGH",
                                         f"Malformed row at line {i}",
                                         {"expected_cols": expected_cols, "actual_cols": len(row)})

            test_results["malformed_rows"] = {
                "count": len(malformed_rows),
                "examples": malformed_rows[:10]
            }

            test_results["status"] = "passed"
            print(f"[OK] File analysis complete: {total_lines-1} records, {len(malformed_rows)} malformed rows")

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("File Analysis", "CRITICAL", "Test failed with exception", {"error": str(e)})

        self.results["tests"]["file_analysis"] = test_results
        return test_results

    def test_2_upload_api(self):
        """Test 2: Upload file via API with different encodings"""
        print("\n=== TEST 2: UPLOAD API ===")
        test_results = {
            "status": "running",
            "upload_attempts": []
        }

        try:
            # Test with different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                print(f"  Testing upload with {encoding} encoding...")
                attempt = {
                    "encoding": encoding,
                    "timestamp": datetime.now().isoformat()
                }

                try:
                    # Read file with specific encoding
                    with open(CSV_FILE, 'rb') as f:
                        files = {'file': (CSV_FILE, f, 'text/csv')}
                        data = {'encoding': encoding}

                        response = requests.post(
                            f"{BASE_URL}/api/upload",
                            files=files,
                            data=data,
                            timeout=30
                        )

                    attempt["status_code"] = response.status_code
                    attempt["response"] = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

                    if response.status_code == 200:
                        print(f"    [OK] Upload successful with {encoding}")
                        result = response.json()
                        attempt["file_id"] = result.get("file_id")
                        if encoding == 'utf-8' and not self.uploaded_file_id:
                            self.uploaded_file_id = result.get("file_id")
                    else:
                        print(f"    [FAIL] Upload failed with {encoding}: {response.status_code}")
                        self.log_issue("Upload API", "HIGH",
                                     f"Upload failed with {encoding} encoding",
                                     {"status_code": response.status_code, "response": attempt["response"]})

                except Exception as e:
                    attempt["error"] = str(e)
                    self.log_issue("Upload API", "HIGH",
                                 f"Upload exception with {encoding}",
                                 {"error": str(e)})

                test_results["upload_attempts"].append(attempt)
                time.sleep(1)  # Rate limiting

            test_results["status"] = "passed" if self.uploaded_file_id else "failed"

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("Upload API", "CRITICAL", "Test failed with exception", {"error": str(e)})

        self.results["tests"]["upload_api"] = test_results
        return test_results

    def test_3_schema_retrieval(self):
        """Test 3: Get candidate schema"""
        print("\n=== TEST 3: SCHEMA RETRIEVAL ===")
        test_results = {
            "status": "running"
        }

        try:
            response = requests.get(f"{BASE_URL}/api/schema/candidate", timeout=10)
            test_results["status_code"] = response.status_code

            if response.status_code == 200:
                schema = response.json()
                test_results["schema"] = schema
                test_results["field_count"] = len(schema.get("fields", []))
                print(f"  [OK] Schema retrieved: {test_results['field_count']} fields")
                test_results["status"] = "passed"
            else:
                self.log_issue("Schema Retrieval", "HIGH",
                             "Failed to retrieve schema",
                             {"status_code": response.status_code})
                test_results["status"] = "failed"

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("Schema Retrieval", "CRITICAL", "Test failed", {"error": str(e)})

        self.results["tests"]["schema_retrieval"] = test_results
        return test_results

    def test_4_auto_mapping(self):
        """Test 4: Auto-map fields"""
        print("\n=== TEST 4: AUTO-MAPPING ===")
        test_results = {
            "status": "running"
        }

        if not self.uploaded_file_id:
            print("  [SKIP] Skipping: No uploaded file ID")
            test_results["status"] = "skipped"
            self.results["tests"]["auto_mapping"] = test_results
            return test_results

        try:
            # Get source fields first
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                headers = f.readline().strip().split('|')

            test_results["source_fields"] = headers
            test_results["source_field_count"] = len(headers)

            # Call auto-map API
            response = requests.post(
                f"{BASE_URL}/api/auto-map",
                json={"file_id": self.uploaded_file_id},
                timeout=30
            )

            test_results["status_code"] = response.status_code

            if response.status_code == 200:
                mapping_result = response.json()
                test_results["mapping"] = mapping_result

                # Analyze mapping quality
                mappings = mapping_result.get("mappings", [])
                mapped_count = sum(1 for m in mappings if m.get("target_field"))
                confidence_scores = [m.get("confidence", 0) for m in mappings if m.get("target_field")]

                test_results["mapping_stats"] = {
                    "total_source_fields": len(mappings),
                    "mapped_fields": mapped_count,
                    "unmapped_fields": len(mappings) - mapped_count,
                    "mapping_percentage": round(mapped_count / len(mappings) * 100, 2) if mappings else 0,
                    "avg_confidence": round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0,
                    "min_confidence": min(confidence_scores) if confidence_scores else 0,
                    "max_confidence": max(confidence_scores) if confidence_scores else 0
                }

                # Identify unmapped fields
                unmapped = [m["source_field"] for m in mappings if not m.get("target_field")]
                test_results["unmapped_fields"] = unmapped

                if unmapped:
                    self.log_issue("Auto-Mapping", "MEDIUM",
                                 f"{len(unmapped)} fields not mapped",
                                 {"unmapped_fields": unmapped[:10]})

                # Check for low confidence mappings
                low_conf = [m for m in mappings if m.get("target_field") and m.get("confidence", 0) < 0.7]
                if low_conf:
                    self.log_issue("Auto-Mapping", "MEDIUM",
                                 f"{len(low_conf)} fields with low confidence",
                                 {"low_confidence_mappings": low_conf[:5]})

                print(f"  [OK] Mapped {mapped_count}/{len(mappings)} fields ({test_results['mapping_stats']['mapping_percentage']}%)")
                test_results["status"] = "passed"
                self.mapping_id = mapping_result.get("mapping_id")

            else:
                self.log_issue("Auto-Mapping", "HIGH",
                             "Auto-mapping failed",
                             {"status_code": response.status_code})
                test_results["status"] = "failed"

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("Auto-Mapping", "CRITICAL", "Test failed", {"error": str(e)})

        self.results["tests"]["auto_mapping"] = test_results
        return test_results

    def test_5_character_validation(self):
        """Test 5: Validate special character preservation"""
        print("\n=== TEST 5: CHARACTER VALIDATION ===")
        test_results = {
            "status": "running",
            "character_tests": []
        }

        # Test specific lines with special characters
        test_cases = [
            {"line": 3, "field": "HomeCountry", "expected": "Türkiye", "description": "Turkish ü"},
            {"line": 8, "field": "HomeLocation", "contains": "Torreón", "description": "Spanish ó"},
            {"line": 10, "field": "LastName", "expected": "Kayır", "description": "Turkish dotless i"},
            {"line": 28, "field": "FirstName", "expected": "Omar", "description": "Arabic/Italian name"}
        ]

        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='|')
                rows = list(reader)

            for test_case in test_cases:
                line_num = test_case["line"]
                field = test_case["field"]

                if line_num - 2 < len(rows):  # -2 because line 1 is header, line 2 is index 0
                    row = rows[line_num - 2]
                    actual_value = row.get(field, "")

                    test_result = {
                        "line": line_num,
                        "field": field,
                        "description": test_case["description"],
                        "actual_value": actual_value
                    }

                    if "expected" in test_case:
                        test_result["expected"] = test_case["expected"]
                        test_result["passed"] = actual_value == test_case["expected"]

                        if not test_result["passed"]:
                            self.log_issue("Character Validation", "HIGH",
                                         f"Special character mismatch at line {line_num}",
                                         {"field": field, "expected": test_case["expected"],
                                          "actual": actual_value, "hex_expected": test_case["expected"].encode('utf-8').hex(),
                                          "hex_actual": actual_value.encode('utf-8').hex()})
                    elif "contains" in test_case:
                        test_result["contains"] = test_case["contains"]
                        test_result["passed"] = test_case["contains"] in actual_value

                        if not test_result["passed"]:
                            self.log_issue("Character Validation", "HIGH",
                                         f"Special character not found at line {line_num}",
                                         {"field": field, "expected_contains": test_case["contains"],
                                          "actual": actual_value})

                    test_results["character_tests"].append(test_result)
                    status_symbol = "[OK]" if test_result.get("passed") else "[FAIL]"
                    print(f"  {status_symbol} Line {line_num}: {test_case['description']}")

            passed_tests = sum(1 for t in test_results["character_tests"] if t.get("passed"))
            test_results["status"] = "passed" if passed_tests == len(test_cases) else "failed"

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("Character Validation", "CRITICAL", "Test failed", {"error": str(e)})

        self.results["tests"]["character_validation"] = test_results
        return test_results

    def test_6_data_validation(self):
        """Test 6: Validate data via API"""
        print("\n=== TEST 6: DATA VALIDATION ===")
        test_results = {
            "status": "running"
        }

        if not self.uploaded_file_id or not self.mapping_id:
            print("  [SKIP] Skipping: Missing file_id or mapping_id")
            test_results["status"] = "skipped"
            self.results["tests"]["data_validation"] = test_results
            return test_results

        try:
            response = requests.post(
                f"{BASE_URL}/api/validate",
                json={
                    "file_id": self.uploaded_file_id,
                    "mapping_id": self.mapping_id
                },
                timeout=60
            )

            test_results["status_code"] = response.status_code

            if response.status_code == 200:
                validation_result = response.json()
                test_results["validation"] = validation_result

                errors = validation_result.get("errors", [])
                test_results["error_count"] = len(errors)

                # Categorize errors
                error_categories = {}
                for error in errors:
                    category = error.get("type", "unknown")
                    if category not in error_categories:
                        error_categories[category] = []
                    error_categories[category].append(error)

                test_results["error_categories"] = {
                    cat: len(errs) for cat, errs in error_categories.items()
                }

                # Log sample errors
                for category, errors_list in error_categories.items():
                    sample_errors = errors_list[:3]
                    self.log_issue("Data Validation", "MEDIUM",
                                 f"{len(errors_list)} {category} errors found",
                                 {"sample_errors": sample_errors})

                print(f"  [OK] Validation complete: {len(errors)} errors found")
                test_results["status"] = "passed"

            else:
                self.log_issue("Data Validation", "HIGH",
                             "Validation API failed",
                             {"status_code": response.status_code})
                test_results["status"] = "failed"

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("Data Validation", "CRITICAL", "Test failed", {"error": str(e)})

        self.results["tests"]["data_validation"] = test_results
        return test_results

    def test_7_xml_transformation(self):
        """Test 7: Transform to XML"""
        print("\n=== TEST 7: XML TRANSFORMATION ===")
        test_results = {
            "status": "running"
        }

        if not self.uploaded_file_id or not self.mapping_id:
            print("  [SKIP] Skipping: Missing file_id or mapping_id")
            test_results["status"] = "skipped"
            self.results["tests"]["xml_transformation"] = test_results
            return test_results

        try:
            response = requests.post(
                f"{BASE_URL}/api/transform/export-xml",
                json={
                    "file_id": self.uploaded_file_id,
                    "mapping_id": self.mapping_id
                },
                timeout=120
            )

            test_results["status_code"] = response.status_code

            if response.status_code == 200:
                xml_content = response.text
                test_results["xml_size"] = len(xml_content)

                # Validate XML structure
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(xml_content)
                    test_results["xml_valid"] = True
                    test_results["root_tag"] = root.tag
                    test_results["record_count"] = len(list(root))

                    # Check special characters in XML
                    special_char_found = {
                        "Türkiye": "Türkiye" in xml_content,
                        "Torreón": "Torreón" in xml_content,
                        "Kayır": "Kayır" in xml_content
                    }
                    test_results["special_chars_in_xml"] = special_char_found

                    missing_chars = [char for char, found in special_char_found.items() if not found]
                    if missing_chars:
                        self.log_issue("XML Transformation", "HIGH",
                                     "Special characters not preserved in XML",
                                     {"missing": missing_chars})

                    print(f"  [OK] XML valid: {test_results['record_count']} records")
                    test_results["status"] = "passed"

                    # Save sample
                    with open("siemens_output_sample.xml", "w", encoding="utf-8") as f:
                        f.write(xml_content[:5000])  # First 5000 chars

                except ET.ParseError as e:
                    test_results["xml_valid"] = False
                    test_results["xml_error"] = str(e)
                    self.log_issue("XML Transformation", "CRITICAL",
                                 "XML is malformed",
                                 {"error": str(e)})
                    test_results["status"] = "failed"

            else:
                self.log_issue("XML Transformation", "HIGH",
                             "XML transformation failed",
                             {"status_code": response.status_code})
                test_results["status"] = "failed"

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("XML Transformation", "CRITICAL", "Test failed", {"error": str(e)})

        self.results["tests"]["xml_transformation"] = test_results
        return test_results

    def test_8_edge_cases(self):
        """Test 8: Edge cases"""
        print("\n=== TEST 8: EDGE CASES ===")
        test_results = {
            "status": "running",
            "edge_cases": []
        }

        try:
            # Test empty/null fields
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='|')
                rows = list(reader)

            # Check specific lines mentioned
            test_lines = [15, 41, 45, 47, 48]
            for line_num in test_lines:
                if line_num - 2 < len(rows):
                    row = rows[line_num - 2]
                    empty_fields = [k for k, v in row.items() if not v or v.strip() == '']

                    edge_case = {
                        "line": line_num,
                        "type": "empty_fields",
                        "empty_field_count": len(empty_fields),
                        "empty_fields": empty_fields[:5]
                    }
                    test_results["edge_cases"].append(edge_case)

                    if len(empty_fields) > 5:
                        self.log_issue("Edge Cases", "MEDIUM",
                                     f"Line {line_num} has {len(empty_fields)} empty fields",
                                     {"sample_fields": empty_fields[:5]})

            # Check for very long fields (line 4 mentioned)
            if len(rows) >= 2:
                row = rows[2]  # Line 4 (0-indexed, so index 2)
                skills = row.get('Skills', '')
                if len(skills) > 1000:
                    edge_case = {
                        "line": 4,
                        "type": "long_field",
                        "field": "Skills",
                        "length": len(skills),
                        "preview": skills[:100] + "..."
                    }
                    test_results["edge_cases"].append(edge_case)
                    print(f"  [OK] Found long field: Skills ({len(skills)} chars)")

            # Check for pipe delimiters in data
            pipe_count = 0
            for i, row in enumerate(rows[:50], 2):  # Check first 50 rows
                for field, value in row.items():
                    if '|' in value:
                        pipe_count += 1
                        if pipe_count <= 3:
                            edge_case = {
                                "line": i,
                                "type": "pipe_in_data",
                                "field": field,
                                "value_preview": value[:50]
                            }
                            test_results["edge_cases"].append(edge_case)

            if pipe_count > 0:
                self.log_issue("Edge Cases", "HIGH",
                             f"Found {pipe_count} fields with pipe delimiter in data",
                             {"risk": "May cause parsing issues"})

            # Check for || (double pipe) in data
            double_pipe_count = 0
            for i, row in enumerate(rows[:50], 2):
                for field, value in row.items():
                    if '||' in value:
                        double_pipe_count += 1
                        if double_pipe_count <= 3:
                            edge_case = {
                                "line": i,
                                "type": "double_pipe_in_data",
                                "field": field,
                                "value_preview": value[:50]
                            }
                            test_results["edge_cases"].append(edge_case)

            if double_pipe_count > 0:
                self.log_issue("Edge Cases", "MEDIUM",
                             f"Found {double_pipe_count} fields with || in data",
                             {"note": "Check if this is intentional separator"})

            print(f"  [OK] Edge case analysis complete: {len(test_results['edge_cases'])} cases found")
            test_results["status"] = "passed"

        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            self.log_issue("Edge Cases", "CRITICAL", "Test failed", {"error": str(e)})

        self.results["tests"]["edge_cases"] = test_results
        return test_results

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("="*60)
        print("SIEMENS CANDIDATES QA TEST SUITE")
        print("="*60)

        # Run tests in order
        self.test_1_file_analysis()
        self.test_2_upload_api()
        self.test_3_schema_retrieval()
        self.test_4_auto_mapping()
        self.test_5_character_validation()
        self.test_6_data_validation()
        self.test_7_xml_transformation()
        self.test_8_edge_cases()

        # Generate summary
        self.generate_summary()

        # Save results
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print("\n" + "="*60)
        print("QA TEST SUITE COMPLETE")
        print("="*60)
        print(f"Results saved to: {RESULTS_FILE}")

        return self.results

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        passed = sum(1 for t in self.results["tests"].values() if t.get("status") == "passed")
        failed = sum(1 for t in self.results["tests"].values() if t.get("status") == "failed")
        errors = sum(1 for t in self.results["tests"].values() if t.get("status") == "error")
        skipped = sum(1 for t in self.results["tests"].values() if t.get("status") == "skipped")

        # Categorize issues by severity
        critical = sum(1 for i in self.issues if i["severity"] == "CRITICAL")
        high = sum(1 for i in self.issues if i["severity"] == "HIGH")
        medium = sum(1 for i in self.issues if i["severity"] == "MEDIUM")

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "total_issues": len(self.issues),
            "critical_issues": critical,
            "high_issues": high,
            "medium_issues": medium,
            "production_ready": critical == 0 and high < 3
        }

        print(f"\n=== TEST SUMMARY ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Skipped: {skipped}")
        print(f"\nIssues Found:")
        print(f"  CRITICAL: {critical}")
        print(f"  HIGH: {high}")
        print(f"  MEDIUM: {medium}")
        print(f"\nProduction Ready: {'YES' if self.results['summary']['production_ready'] else 'NO'}")

if __name__ == "__main__":
    tester = SiemensQATest()
    results = tester.run_all_tests()
