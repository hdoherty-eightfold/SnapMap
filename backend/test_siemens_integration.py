"""
Comprehensive End-to-End Integration Test for Siemens Candidate File
Tests the complete workflow from upload to XML generation
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
import chardet

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_FILE = r"c:\Code\SnapMap\backend\test_siemens_candidates.csv"
RESULTS_FILE = r"c:\Code\SnapMap\SIEMENS_INTEGRATION_TEST_RESULTS.md"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARNING] {text}{Colors.ENDC}")

class SiemensIntegrationTest:
    def __init__(self):
        self.results = {
            'upload_success': False,
            'delimiter_detected': None,
            'encoding_detected': None,
            'total_fields': 0,
            'fields_mapped': 0,
            'mapping_accuracy': 0.0,
            'characters_preserved': {},
            'row_count_validation': False,
            'source_rows': 0,
            'output_rows': 0,
            'xml_generated': False,
            'xml_size_kb': 0,
            'issues': [],
            'specific_scenarios': {}
        }
        self.job_id = None
        self.mapping_data = None

    def check_server(self):
        """Check if FastAPI server is running"""
        print_header("STEP 1: Server Health Check")
        try:
            # Check root endpoint
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print_success(f"Server is running at http://localhost:8000")
                return True
        except Exception as e:
            print_error(f"Server is not responding: {str(e)}")
            self.results['issues'].append(f"Server not running: {str(e)}")
            return False

    def analyze_file(self):
        """Analyze the source file"""
        print_header("STEP 2: Source File Analysis")

        if not os.path.exists(TEST_FILE):
            print_error(f"Test file not found: {TEST_FILE}")
            self.results['issues'].append(f"Test file not found")
            return False

        # File size
        file_size = os.path.getsize(TEST_FILE) / 1024
        print_info(f"File size: {file_size:.2f} KB")

        # Detect encoding
        with open(TEST_FILE, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            self.results['encoding_detected'] = result['encoding']
            print_info(f"Encoding detected: {result['encoding']} (confidence: {result['confidence']*100:.1f}%)")

        # Count rows and detect delimiter
        with open(TEST_FILE, 'r', encoding='utf-8') as f:
            first_line = f.readline()

            # Detect delimiter
            if '|' in first_line:
                self.results['delimiter_detected'] = '|'
                print_info(f"Delimiter detected: | (pipe)")
            elif ',' in first_line:
                self.results['delimiter_detected'] = ','
                print_info(f"Delimiter detected: , (comma)")
            else:
                self.results['delimiter_detected'] = 'unknown'
                print_warning(f"Delimiter: unknown")

            # Count fields
            self.results['total_fields'] = len(first_line.split(self.results['delimiter_detected']))
            print_info(f"Total fields: {self.results['total_fields']}")

            # Count rows
            f.seek(0)
            self.results['source_rows'] = sum(1 for _ in f) - 1  # Exclude header
            print_info(f"Total data rows: {self.results['source_rows']}")

        # Check for special characters
        special_test_cases = {
            'Turkish_ü': 'Türkiye',
            'Spanish_ó': 'Torreón',
            'Turkish_ı': 'Kayır'
        }

        with open(TEST_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            for key, char_pattern in special_test_cases.items():
                if char_pattern in content:
                    print_success(f"Found special character test case: {char_pattern}")
                    self.results['characters_preserved'][key] = 'FOUND_IN_SOURCE'

        print_success("File analysis complete")
        return True

    def upload_file(self):
        """Upload file via API"""
        print_header("STEP 3: File Upload via API")

        try:
            with open(TEST_FILE, 'rb') as f:
                files = {'file': ('test_siemens_candidates.csv', f, 'text/csv')}
                data = {'schema_name': 'candidate'}

                print_info("Uploading file to /upload endpoint...")
                response = requests.post(f"{BASE_URL}/upload", files=files, data=data, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    self.job_id = result.get('file_id')  # Use file_id from upload response
                    self.results['upload_success'] = True
                    print_success(f"Upload successful! File ID: {self.job_id}")
                    print_info(f"Rows uploaded: {result.get('row_count', 0)}")
                    print_info(f"Columns: {result.get('column_count', 0)}")
                    return True
                else:
                    print_error(f"Upload failed with status {response.status_code}")
                    print_error(f"Response: {response.text}")
                    self.results['issues'].append(f"Upload failed: {response.status_code}")
                    return False
        except Exception as e:
            print_error(f"Upload error: {str(e)}")
            self.results['issues'].append(f"Upload exception: {str(e)}")
            return False

    def get_mapping(self):
        """Get auto-generated mapping"""
        print_header("STEP 4: Auto-Mapping Retrieval")

        if not self.job_id:
            print_error("No job ID available")
            return False

        try:
            print_info(f"Retrieving mapping for job {self.job_id}...")
            response = requests.get(f"{BASE_URL}/mapping/{self.job_id}", timeout=30)

            if response.status_code == 200:
                self.mapping_data = response.json()

                # Analyze mapping
                mapping = self.mapping_data.get('mapping', {})
                source_fields = self.mapping_data.get('source_fields', [])

                print_info(f"Source fields detected: {len(source_fields)}")
                print_info(f"Target schema: {self.mapping_data.get('target_schema')}")

                # Count mapped fields
                mapped_count = sum(1 for field, target in mapping.items() if target)
                self.results['fields_mapped'] = mapped_count
                self.results['mapping_accuracy'] = (mapped_count / len(source_fields) * 100) if source_fields else 0

                print_success(f"Mapped fields: {mapped_count}/{len(source_fields)} ({self.results['mapping_accuracy']:.1f}%)")

                # Show sample mappings
                print_info("\nSample mappings:")
                count = 0
                for source, target in mapping.items():
                    if target and count < 10:
                        print(f"  {source} → {target}")
                        count += 1

                return True
            else:
                print_error(f"Failed to get mapping: {response.status_code}")
                self.results['issues'].append(f"Mapping retrieval failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Mapping error: {str(e)}")
            self.results['issues'].append(f"Mapping exception: {str(e)}")
            return False

    def validate_and_export(self):
        """Validate data and export to XML"""
        print_header("STEP 5: Data Validation & XML Export")

        if not self.job_id or not self.mapping_data:
            print_error("Missing job ID or mapping data")
            return False

        try:
            # Prepare export request
            export_data = {
                'job_id': self.job_id,
                'mapping': self.mapping_data.get('mapping', {}),
                'target_schema': 'candidate'
            }

            print_info("Sending export request...")
            response = requests.post(f"{BASE_URL}/export", json=export_data, timeout=120)

            if response.status_code == 200:
                result = response.json()

                # Check if XML was generated
                xml_path = result.get('xml_path')
                if xml_path and os.path.exists(xml_path):
                    self.results['xml_generated'] = True
                    self.results['xml_size_kb'] = os.path.getsize(xml_path) / 1024

                    print_success(f"XML generated: {xml_path}")
                    print_info(f"XML size: {self.results['xml_size_kb']:.2f} KB")

                    # Count records in XML
                    with open(xml_path, 'r', encoding='utf-8') as f:
                        xml_content = f.read()
                        self.results['output_rows'] = xml_content.count('<Candidate>')
                        print_info(f"Records in XML: {self.results['output_rows']}")

                    # Validate row count
                    if self.results['output_rows'] == self.results['source_rows']:
                        self.results['row_count_validation'] = True
                        print_success(f"Row count validation: PASS ({self.results['source_rows']} in = {self.results['output_rows']} out)")
                    else:
                        self.results['row_count_validation'] = False
                        print_error(f"Row count validation: FAIL ({self.results['source_rows']} in ≠ {self.results['output_rows']} out)")
                        self.results['issues'].append(f"Row count mismatch: {self.results['source_rows']} vs {self.results['output_rows']}")

                    # Check character preservation
                    self.check_character_preservation(xml_content)

                    return True
                else:
                    print_error("XML file not generated")
                    self.results['issues'].append("XML file not found")
                    return False
            else:
                print_error(f"Export failed: {response.status_code}")
                error_msg = response.json().get('error', 'Unknown error')
                print_error(f"Error: {error_msg}")
                self.results['issues'].append(f"Export failed: {error_msg}")
                return False
        except Exception as e:
            print_error(f"Export error: {str(e)}")
            self.results['issues'].append(f"Export exception: {str(e)}")
            return False

    def check_character_preservation(self, xml_content):
        """Check if special characters are preserved in XML"""
        print_info("\nChecking character preservation...")

        test_cases = {
            'Turkish_ü': 'Türkiye',
            'Spanish_ó': 'Torreón',
            'Turkish_ı': 'Kayır'
        }

        for key, expected in test_cases.items():
            if expected in xml_content:
                self.results['characters_preserved'][key] = 'PRESERVED'
                print_success(f"{expected} - PRESERVED ✓")
            else:
                self.results['characters_preserved'][key] = 'LOST'
                print_error(f"{expected} - LOST ✗")
                self.results['issues'].append(f"Character lost: {expected}")

    def test_specific_scenarios(self):
        """Test specific data scenarios"""
        print_header("STEP 6: Specific Scenario Testing")

        # For now, we'll check if these are in the source file
        scenarios = {
            'Row_3_Turkish': 'Tarik Uveys Sen from Türkiye',
            'Row_8_Spanish': 'Hector from Torreón',
            'Row_10_Long_Skills': 'Esra Kayır with 100+ skills',
            'Row_15_Internal': 'Internal Siemens employee'
        }

        with open(TEST_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

            if 'Tarik Uveys' in content and 'Sen' in content:
                self.results['specific_scenarios']['Turkish_candidate'] = 'FOUND'
                print_success("Turkish candidate (Tarik Uveys Sen) - FOUND")

            if 'Hector' in content and 'Torreón' in content:
                self.results['specific_scenarios']['Spanish_candidate'] = 'FOUND'
                print_success("Spanish candidate (Hector from Torreón) - FOUND")

            if 'Esra' in content and 'Kayır' in content:
                self.results['specific_scenarios']['Long_skills'] = 'FOUND'
                print_success("Long skills field (Esra Kayır) - FOUND")

            if 'SIEMENS.COM' in content or 'SIEMENS-HEALTHINEERS.COM' in content:
                self.results['specific_scenarios']['Internal_employee'] = 'FOUND'
                print_success("Internal Siemens employee - FOUND")

    def generate_report(self):
        """Generate detailed test results report"""
        print_header("STEP 7: Generating Report")

        report = f"""# SIEMENS INTEGRATION TEST RESULTS

**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test File:** {TEST_FILE}

---

## Executive Summary

| Metric | Result |
|--------|--------|
| Upload Success | {'[PASS] YES' if self.results['upload_success'] else '[FAIL] NO'} |
| Delimiter Detected | {self.results['delimiter_detected']} |
| Encoding Detected | {self.results['encoding_detected']} |
| Fields Mapped | {self.results['fields_mapped']}/{self.results['total_fields']} ({self.results['mapping_accuracy']:.1f}%) |
| Row Count Validation | {'[PASS]' if self.results['row_count_validation'] else '[FAIL]'} |
| XML Generated | {'[YES]' if self.results['xml_generated'] else '[NO]'} |

---

## Detailed Results

### 1. File Analysis
- **Source Rows:** {self.results['source_rows']}
- **Output Rows:** {self.results['output_rows']}
- **Delimiter:** `{self.results['delimiter_detected']}`
- **Encoding:** {self.results['encoding_detected']}
- **Total Fields:** {self.results['total_fields']}

### 2. Mapping Performance
- **Fields Successfully Mapped:** {self.results['fields_mapped']}
- **Mapping Accuracy:** {self.results['mapping_accuracy']:.1f}%
- **Target Schema:** candidate
- **Validation:** {'✓ PASS (≥70%)' if self.results['mapping_accuracy'] >= 70 else '✗ FAIL (<70%)'}

### 3. Character Encoding Preservation
"""

        if self.results['characters_preserved']:
            report += "\n| Character Test | Status |\n|----------------|--------|\n"
            for key, status in self.results['characters_preserved'].items():
                marker = '[PASS]' if status == 'PRESERVED' else '[FAIL]'
                report += f"| {key.replace('_', ' ')} | {marker} {status} |\n"
        else:
            report += "\n*No character tests performed*\n"

        report += f"""

### 4. Row Count Validation
- **Input Rows:** {self.results['source_rows']}
- **Output Rows:** {self.results['output_rows']}
- **Match:** {'[YES]' if self.results['row_count_validation'] else '[NO]'}

### 5. XML Output
- **Generated:** {'[YES]' if self.results['xml_generated'] else '[NO]'}
- **Size:** {self.results['xml_size_kb']:.2f} KB

### 6. Specific Scenarios Tested
"""

        if self.results['specific_scenarios']:
            report += "\n| Scenario | Status |\n|----------|--------|\n"
            for key, status in self.results['specific_scenarios'].items():
                report += f"| {key.replace('_', ' ')} | {status} |\n"
        else:
            report += "\n*No specific scenarios tested*\n"

        report += "\n\n### 7. Issues Found\n\n"

        if self.results['issues']:
            for i, issue in enumerate(self.results['issues'], 1):
                report += f"{i}. {issue}\n"
        else:
            report += "**No issues found!**\n"

        report += f"""

---

## Test Verdict

"""

        # Calculate overall pass/fail
        critical_checks = [
            self.results['upload_success'],
            self.results['xml_generated'],
            self.results['row_count_validation'],
            self.results['mapping_accuracy'] >= 70
        ]

        if all(critical_checks):
            report += "### **PASS**\n\nAll critical checks passed successfully.\n"
        else:
            report += "### **FAIL**\n\nOne or more critical checks failed.\n"

        report += f"\n**Total Issues:** {len(self.results['issues'])}\n"

        # Save report
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            f.write(report)

        print_success(f"Report saved to: {RESULTS_FILE}")
        print_info(f"Report size: {len(report)} characters")

        return report

    def run(self):
        """Run all tests"""
        print_header("SIEMENS CANDIDATE FILE - COMPREHENSIVE INTEGRATION TEST")
        print_info(f"Test file: {TEST_FILE}")
        print_info(f"Results will be saved to: {RESULTS_FILE}")

        start_time = time.time()

        # Run test steps
        steps = [
            self.check_server,
            self.analyze_file,
            self.upload_file,
            self.get_mapping,
            self.validate_and_export,
            self.test_specific_scenarios,
            self.generate_report
        ]

        for step in steps:
            if not step():
                print_error(f"Test failed at step: {step.__name__}")
                # Continue to generate report even if a step fails
                if step != self.generate_report:
                    continue

        elapsed_time = time.time() - start_time

        print_header("TEST COMPLETE")
        print_info(f"Total execution time: {elapsed_time:.2f} seconds")
        print_info(f"Results saved to: {RESULTS_FILE}")

        # Print summary
        print("\n" + "="*80)
        print(f"{Colors.BOLD}SUMMARY{Colors.ENDC}".center(80))
        print("="*80)
        print(f"Upload Success: {Colors.GREEN if self.results['upload_success'] else Colors.RED}{'YES' if self.results['upload_success'] else 'NO'}{Colors.ENDC}")
        print(f"Mapping Accuracy: {self.results['mapping_accuracy']:.1f}%")
        print(f"Row Count Match: {Colors.GREEN if self.results['row_count_validation'] else Colors.RED}{'YES' if self.results['row_count_validation'] else 'NO'}{Colors.ENDC}")
        print(f"XML Generated: {Colors.GREEN if self.results['xml_generated'] else Colors.RED}{'YES' if self.results['xml_generated'] else 'NO'}{Colors.ENDC}")
        print(f"Issues Found: {len(self.results['issues'])}")
        print("="*80 + "\n")

if __name__ == "__main__":
    test = SiemensIntegrationTest()
    test.run()
