"""
Test Delimiter Auto-Detection

Tests the FileParser's ability to detect different CSV delimiters:
- Comma-delimited CSV (standard)
- Pipe-delimited CSV (Siemens format)
- Tab-delimited TSV
- Semicolon-delimited CSV
- Mixed content with delimiters in quoted strings
"""

import pytest
import pandas as pd
from io import BytesIO
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser


class TestDelimiterDetection:
    """Test delimiter auto-detection functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = FileParser()

    def test_comma_delimited_csv(self):
        """Test detection of comma-delimited CSV"""
        csv_content = b"""FirstName,LastName,Email
John,Doe,john@example.com
Jane,Smith,jane@example.com
Bob,Johnson,bob@example.com"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info["delimiter"] == ",", "Should detect comma delimiter"
        assert format_info["field_count"] == 3, "Should detect 3 fields"
        assert format_info["row_count"] == 3, "Should detect 3 data rows"
        assert "FirstName" in format_info["preview_fields"]

    def test_pipe_delimited_csv_siemens_format(self):
        """Test detection of pipe-delimited CSV (Siemens format)"""
        csv_content = b"""PersonID|FirstName|LastName|WorkEmails|WorkPhones
12345|John|Doe|john@company.com|555-1234
67890|Jane|Smith|jane@company.com||janes@other.com|555-5678||555-9999
11111|Bob|Johnson|bob@company.com|555-0000"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info["delimiter"] == "|", "Should detect pipe delimiter"
        assert format_info["field_count"] == 5, "Should detect 5 fields"
        assert format_info["row_count"] == 3, "Should detect 3 data rows"
        assert "PersonID" in format_info["preview_fields"]

    def test_tab_delimited_tsv(self):
        """Test detection of tab-delimited TSV"""
        tsv_content = b"""FirstName\tLastName\tEmail\tPhone
John\tDoe\tjohn@example.com\t555-1234
Jane\tSmith\tjane@example.com\t555-5678
Bob\tJohnson\tbob@example.com\t555-0000"""

        format_info = self.parser.detect_file_format(tsv_content, "test.csv")

        assert format_info["delimiter"] == "\t", "Should detect tab delimiter"
        assert format_info["field_count"] == 4, "Should detect 4 fields"
        assert format_info["row_count"] == 3, "Should detect 3 data rows"

    def test_semicolon_delimited_csv(self):
        """Test detection of semicolon-delimited CSV"""
        csv_content = b"""FirstName;LastName;Email;Country
John;Doe;john@example.com;USA
Jane;Smith;jane@example.com;UK
Bob;Johnson;bob@example.com;Canada"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info["delimiter"] == ";", "Should detect semicolon delimiter"
        assert format_info["field_count"] == 4, "Should detect 4 fields"
        assert format_info["row_count"] == 3, "Should detect 3 data rows"

    def test_quoted_strings_with_delimiters(self):
        """Test handling of quoted strings containing delimiters"""
        csv_content = b"""Name,Address,Email
"Doe, John","123 Main St, Apt 4","john@example.com"
"Smith, Jane","456 Oak Ave, Suite 100","jane@example.com"
"Johnson, Bob","789 Elm St, Unit 5","bob@example.com" """

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info["delimiter"] == ",", "Should detect comma delimiter"
        assert format_info["field_count"] == 3, "Should detect 3 fields despite quoted commas"
        assert format_info["row_count"] == 3, "Should detect 3 data rows"

    def test_parse_with_auto_detected_delimiter(self):
        """Test parsing file with auto-detected delimiter"""
        # Pipe-delimited content
        csv_content = b"""PersonID|FirstName|LastName|Email
12345|John|Doe|john@example.com
67890|Jane|Smith|jane@example.com"""

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert metadata["detected_delimiter"] == "|", "Should auto-detect pipe delimiter"
        assert len(df) == 2, "Should parse 2 rows"
        assert len(df.columns) == 4, "Should parse 4 columns"
        assert df.iloc[0]["PersonID"] == "12345" or df.iloc[0]["PersonID"] == 12345

    def test_parse_with_manual_delimiter_override(self):
        """Test parsing with manually specified delimiter"""
        csv_content = b"""A|B|C
1|2|3
4|5|6"""

        df, metadata = self.parser.parse_file(csv_content, "test.csv", delimiter="|")

        assert metadata["detected_delimiter"] == "|", "Should use specified delimiter"
        assert len(df) == 2, "Should parse 2 rows"
        assert len(df.columns) == 3, "Should parse 3 columns"

    def test_multi_value_field_detection(self):
        """Test detection of multi-value fields with || separator"""
        csv_content = b"""PersonID|FirstName|WorkEmails
12345|John|john@company.com||john.doe@other.com
67890|Jane|jane@company.com
11111|Bob|bob@company.com||bob.j@other.com||bob.johnson@third.com"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert "WorkEmails" in format_info["multi_value_fields"], \
            "Should detect WorkEmails as multi-value field"

    def test_special_character_detection(self):
        """Test detection of special characters in content"""
        csv_content = """FirstName,LastName,City
José,García,Torreón
Müller,Schmidt,München
İbrahim,Çelik,İstanbul""".encode('utf-8')

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert len(format_info["special_characters_detected"]) > 0, \
            "Should detect special characters"
        # Check for some specific characters
        special_chars_str = ''.join(format_info["special_characters_detected"])
        assert any(c in special_chars_str for c in ['é', 'ü', 'ö', 'İ', 'ç'])

    def test_entity_suggestion_based_on_fields(self):
        """Test entity type suggestion based on field names"""
        # Test candidate detection
        csv_content = b"""CandidateID,FirstName,LastName,ApplicantEmail
12345,John,Doe,john@example.com"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")
        assert format_info["suggested_entity"] == "candidate", \
            "Should suggest 'candidate' entity type"

        # Test employee detection
        csv_content = b"""EmployeeID,FirstName,LastName,WorkEmail
12345,John,Doe,john@company.com"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")
        assert format_info["suggested_entity"] == "employee", \
            "Should suggest 'employee' entity type"

    def test_excel_file_parsing(self):
        """Test Excel file format detection"""
        # Create a simple Excel file in memory
        df = pd.DataFrame({
            'FirstName': ['John', 'Jane'],
            'LastName': ['Doe', 'Smith'],
            'Email': ['john@example.com', 'jane@example.com']
        })

        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        excel_content = buffer.read()

        format_info = self.parser.detect_file_format(excel_content, "test.xlsx")

        assert format_info["delimiter"] is None, "Excel files don't have delimiters"
        assert format_info["field_count"] == 3, "Should detect 3 fields"
        assert format_info["row_count"] == 2, "Should detect 2 rows"

    def test_large_file_delimiter_detection_performance(self):
        """Test delimiter detection on larger files"""
        # Create a larger CSV file
        rows = []
        rows.append("PersonID|FirstName|LastName|Email|Phone")
        for i in range(1000):
            rows.append(f"{i}|Person{i}|Last{i}|person{i}@example.com|555-{i:04d}")

        csv_content = '\n'.join(rows).encode('utf-8')

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info["delimiter"] == "|", "Should detect pipe delimiter"
        assert format_info["row_count"] == 1000, "Should count all 1000 rows"

    def test_empty_file_handling(self):
        """Test handling of empty files"""
        csv_content = b""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info["row_count"] == 0, "Should handle empty file"
        assert format_info["field_count"] == 0, "Should have no fields"

    def test_single_column_file(self):
        """Test handling of single-column files"""
        csv_content = b"""Email
john@example.com
jane@example.com
bob@example.com"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info["field_count"] == 1, "Should detect 1 field"
        assert format_info["row_count"] == 3, "Should detect 3 rows"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
