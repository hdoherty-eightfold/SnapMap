"""
Test Multi-Value Field Handling

Tests handling of fields with multiple values:
- Parse "email1@test.com||email2@test.com" format
- Generate XML with <email_list><email>...</email></email_list>
- Test with 2, 3, 5+ values
- Test empty values
- Test special characters in values
"""

import pytest
import pandas as pd
from io import BytesIO
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.file_parser import FileParser
from app.services.xml_transformer import XMLTransformer


class TestMultiValueFields:
    """Test multi-value field handling"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = FileParser()
        self.transformer = XMLTransformer()

    def test_parse_double_pipe_separator(self):
        """Test parsing fields with || separator"""
        csv_content = b"""PersonID|WorkEmails
12345|john@company.com||john.doe@other.com
67890|jane@company.com
11111|bob@company.com||bob.j@other.com||bob.johnson@third.com"""

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert len(df) == 3, "Should parse all rows"
        assert '||' in df.iloc[0]['WorkEmails'], "Should preserve || separator"
        assert '||' in df.iloc[2]['WorkEmails'], "Should preserve || separator"

    def test_detect_multi_value_fields(self):
        """Test detection of multi-value fields"""
        csv_content = b"""PersonID|WorkEmails|WorkPhones
12345|john@company.com||john.doe@other.com|555-1234||555-5678
67890|jane@company.com|555-9999"""

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert "WorkEmails" in format_info["multi_value_fields"], \
            "Should detect WorkEmails as multi-value field"
        assert "WorkPhones" in format_info["multi_value_fields"], \
            "Should detect WorkPhones as multi-value field"

    def test_xml_generation_with_two_values(self):
        """Test XML generation with 2 values in multi-value field"""
        df = pd.DataFrame({
            'EMAIL': ['email1@test.com||email2@test.com'],
            'FIRST_NAME': ['John']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        # Parse XML
        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list = root.find('.//email_list')

        assert email_list is not None, "Should have email_list element"

        emails = email_list.findall('email')
        assert len(emails) == 2, "Should have 2 email elements"
        assert emails[0].text == 'email1@test.com', "First email correct"
        assert emails[1].text == 'email2@test.com', "Second email correct"

    def test_xml_generation_with_three_values(self):
        """Test XML generation with 3 values in multi-value field"""
        df = pd.DataFrame({
            'PHONE': ['555-1111||555-2222||555-3333'],
            'FIRST_NAME': ['Jane']
        })

        mappings = [
            {'source': 'PHONE', 'target': 'PHONE'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        phone_list = root.find('.//phone_list')

        assert phone_list is not None, "Should have phone_list element"

        phones = phone_list.findall('phone')
        assert len(phones) == 3, "Should have 3 phone elements"
        assert phones[0].text == '555-1111', "First phone correct"
        assert phones[1].text == '555-2222', "Second phone correct"
        assert phones[2].text == '555-3333', "Third phone correct"

    def test_xml_generation_with_five_plus_values(self):
        """Test XML generation with 5+ values in multi-value field"""
        df = pd.DataFrame({
            'EMAIL': ['e1@test.com||e2@test.com||e3@test.com||e4@test.com||e5@test.com||e6@test.com'],
            'FIRST_NAME': ['Bob']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list = root.find('.//email_list')

        assert email_list is not None, "Should have email_list element"

        emails = email_list.findall('email')
        assert len(emails) == 6, "Should have 6 email elements"
        assert emails[0].text == 'e1@test.com'
        assert emails[5].text == 'e6@test.com'

    def test_empty_values_in_multi_value_field(self):
        """Test handling of empty values in multi-value fields"""
        df = pd.DataFrame({
            'EMAIL': ['email1@test.com||||email3@test.com'],  # Empty middle value
            'FIRST_NAME': ['Alice']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list = root.find('.//email_list')

        emails = email_list.findall('email')
        # Should skip empty values
        assert len(emails) == 2, "Should skip empty values"
        assert emails[0].text == 'email1@test.com'
        assert emails[1].text == 'email3@test.com'

    def test_special_characters_in_multi_value_fields(self):
        """Test special characters within multi-value fields"""
        df = pd.DataFrame({
            'EMAIL': ['josé@company.com||müller@example.de||françois@test.fr'],
            'FIRST_NAME': ['Test']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        # Verify special characters preserved
        assert 'josé@company.com' in xml_output, "Spanish character preserved"
        assert 'müller@example.de' in xml_output, "German character preserved"
        assert 'françois@test.fr' in xml_output, "French character preserved"

        # Parse and verify structure
        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list = root.find('.//email_list')
        emails = email_list.findall('email')

        assert len(emails) == 3, "Should have 3 email elements"
        assert emails[0].text == 'josé@company.com'

    def test_whitespace_trimming_in_multi_value_fields(self):
        """Test that whitespace is trimmed from multi-value items"""
        df = pd.DataFrame({
            'EMAIL': ['  email1@test.com  ||  email2@test.com  ||  email3@test.com  '],
            'FIRST_NAME': ['Test']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list = root.find('.//email_list')
        emails = email_list.findall('email')

        # Values should be trimmed
        assert emails[0].text == 'email1@test.com', "Whitespace trimmed"
        assert emails[1].text == 'email2@test.com', "Whitespace trimmed"
        assert emails[2].text == 'email3@test.com', "Whitespace trimmed"

    def test_single_value_not_split(self):
        """Test that single values without separator are not split"""
        df = pd.DataFrame({
            'EMAIL': ['single@test.com'],
            'FIRST_NAME': ['Test']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list = root.find('.//email_list')
        emails = email_list.findall('email')

        assert len(emails) == 1, "Single value should remain single"
        assert emails[0].text == 'single@test.com'

    def test_multiple_multi_value_fields(self):
        """Test multiple multi-value fields in same record"""
        df = pd.DataFrame({
            'EMAIL': ['email1@test.com||email2@test.com'],
            'PHONE': ['555-1111||555-2222||555-3333'],
            'FIRST_NAME': ['John']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'PHONE', 'target': 'PHONE'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))

        # Check email_list
        email_list = root.find('.//email_list')
        assert email_list is not None
        assert len(email_list.findall('email')) == 2

        # Check phone_list
        phone_list = root.find('.//phone_list')
        assert phone_list is not None
        assert len(phone_list.findall('phone')) == 3

    def test_comma_separated_values_fallback(self):
        """Test fallback to comma separation when || not present"""
        df = pd.DataFrame({
            'EMAIL': ['email1@test.com,email2@test.com,email3@test.com'],
            'FIRST_NAME': ['Jane']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list = root.find('.//email_list')

        emails = email_list.findall('email')
        # Transformer should handle comma-separated values
        assert len(emails) == 3, "Should split on comma when || not present"

    def test_mixed_single_and_multi_value_rows(self):
        """Test file with mix of single and multi-value rows"""
        df = pd.DataFrame({
            'EMAIL': [
                'single@test.com',
                'multi1@test.com||multi2@test.com',
                'another@test.com',
                'triple1@test.com||triple2@test.com||triple3@test.com'
            ],
            'FIRST_NAME': ['Alice', 'Bob', 'Charlie', 'Diana']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        employees = root.findall('.//EF_Employee')

        assert len(employees) == 4, "Should have 4 employee records"

        # First employee - single value
        emails_1 = employees[0].find('.//email_list').findall('email')
        assert len(emails_1) == 1

        # Second employee - two values
        emails_2 = employees[1].find('.//email_list').findall('email')
        assert len(emails_2) == 2

        # Third employee - single value
        emails_3 = employees[2].find('.//email_list').findall('email')
        assert len(emails_3) == 1

        # Fourth employee - three values
        emails_4 = employees[3].find('.//email_list').findall('email')
        assert len(emails_4) == 3

    def test_url_multi_value_field(self):
        """Test URL multi-value fields"""
        df = pd.DataFrame({
            'URL': ['https://linkedin.com/in/john||https://github.com/johndoe'],
            'FIRST_NAME': ['John']
        })

        mappings = [
            {'source': 'URL', 'target': 'URL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        url_list = root.find('.//url_list')

        assert url_list is not None, "Should have url_list element"

        urls = url_list.findall('url')
        assert len(urls) == 2, "Should have 2 URL elements"
        assert urls[0].text == 'https://linkedin.com/in/john'
        assert urls[1].text == 'https://github.com/johndoe'

    def test_nan_in_multi_value_field(self):
        """Test handling of NaN/null values in multi-value fields"""
        df = pd.DataFrame({
            'EMAIL': ['email1@test.com||email2@test.com', pd.NA, ''],
            'FIRST_NAME': ['Alice', 'Bob', 'Charlie']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        employees = root.findall('.//EF_Employee')

        assert len(employees) == 3, "Should have all 3 employees"

        # First has emails
        email_list_1 = employees[0].find('.//email_list')
        assert email_list_1 is not None

        # Second and third might not have email_list (null/empty)
        # This depends on implementation - XML transformer skips NaN

    def test_long_multi_value_list(self):
        """Test very long multi-value list (stress test)"""
        # Create a list with 20 email addresses
        email_list = '||'.join([f'email{i}@test.com' for i in range(20)])

        df = pd.DataFrame({
            'EMAIL': [email_list],
            'FIRST_NAME': ['Test']
        })

        mappings = [
            {'source': 'EMAIL', 'target': 'EMAIL'},
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        root = ET.fromstring(xml_output.encode('utf-8'))
        email_list_elem = root.find('.//email_list')
        emails = email_list_elem.findall('email')

        assert len(emails) == 20, "Should handle 20 email values"
        assert emails[0].text == 'email0@test.com'
        assert emails[19].text == 'email19@test.com'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
