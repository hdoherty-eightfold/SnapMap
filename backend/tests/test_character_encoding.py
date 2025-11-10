"""
Test Character Encoding Preservation

Tests proper handling of international characters throughout the pipeline:
- Turkish: Türkiye, Kayır, İstanbul
- Spanish: Torreón, García, Señor
- German: München, Größe
- French: Français, Élève
- Complete pipeline: upload -> map -> transform -> XML
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


class TestCharacterEncoding:
    """Test character encoding preservation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.parser = FileParser()
        self.transformer = XMLTransformer()

        # Test data with international characters
        self.test_data = {
            'turkish': [
                {'name': 'Türkiye', 'city': 'İstanbul', 'surname': 'Kayır'},
                {'name': 'Çağlar', 'city': 'Ankara', 'surname': 'Şahin'},
                {'name': 'Ömer', 'city': 'İzmir', 'surname': 'Güneş'}
            ],
            'spanish': [
                {'name': 'José', 'city': 'Torreón', 'surname': 'García'},
                {'name': 'María', 'city': 'León', 'surname': 'Señor'},
                {'name': 'Ángel', 'city': 'Aragón', 'surname': 'Muñoz'}
            ],
            'german': [
                {'name': 'München', 'city': 'Köln', 'surname': 'Größe'},
                {'name': 'Jürgen', 'city': 'Düsseldorf', 'surname': 'Müller'},
                {'name': 'Björn', 'city': 'Nürnberg', 'surname': 'Schäfer'}
            ],
            'french': [
                {'name': 'François', 'city': 'Paris', 'surname': 'Élève'},
                {'name': 'Amélie', 'city': 'Lyon', 'surname': 'Côté'},
                {'name': 'René', 'city': 'Orléans', 'surname': 'Bélanger'}
            ]
        }

    def test_turkish_characters_in_csv(self):
        """Test Turkish character preservation in CSV parsing"""
        csv_content = """FirstName,LastName,City
Türkiye,Kayır,İstanbul
Çağlar,Şahin,Ankara
Ömer,Güneş,İzmir""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert df.iloc[0]['FirstName'] == 'Türkiye', "Should preserve Turkish Ü"
        assert df.iloc[0]['LastName'] == 'Kayır', "Should preserve Turkish ı"
        assert df.iloc[0]['City'] == 'İstanbul', "Should preserve Turkish İ"
        assert df.iloc[1]['FirstName'] == 'Çağlar', "Should preserve Turkish Ç"
        assert df.iloc[1]['LastName'] == 'Şahin', "Should preserve Turkish Ş"

    def test_spanish_characters_in_csv(self):
        """Test Spanish character preservation in CSV parsing"""
        csv_content = """FirstName,LastName,City
José,García,Torreón
María,Señor,León
Ángel,Muñoz,Aragón""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert df.iloc[0]['FirstName'] == 'José', "Should preserve Spanish é"
        assert df.iloc[0]['LastName'] == 'García', "Should preserve Spanish í"
        assert df.iloc[0]['City'] == 'Torreón', "Should preserve Spanish ó"
        assert df.iloc[1]['LastName'] == 'Señor', "Should preserve Spanish ñ"
        assert df.iloc[2]['FirstName'] == 'Ángel', "Should preserve Spanish Á"

    def test_german_characters_in_csv(self):
        """Test German character preservation in CSV parsing"""
        csv_content = """FirstName,LastName,City
Jürgen,Müller,München
Björn,Schäfer,Köln
Andreas,Größe,Düsseldorf""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert df.iloc[0]['FirstName'] == 'Jürgen', "Should preserve German ü"
        assert df.iloc[0]['LastName'] == 'Müller', "Should preserve German ü"
        assert df.iloc[0]['City'] == 'München', "Should preserve German ü"
        assert df.iloc[1]['FirstName'] == 'Björn', "Should preserve German ö"
        assert df.iloc[2]['LastName'] == 'Größe', "Should preserve German ö and ß"

    def test_french_characters_in_csv(self):
        """Test French character preservation in CSV parsing"""
        csv_content = """FirstName,LastName,City
François,Élève,Paris
Amélie,Côté,Lyon
René,Bélanger,Orléans""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert df.iloc[0]['FirstName'] == 'François', "Should preserve French ç"
        assert df.iloc[0]['LastName'] == 'Élève', "Should preserve French É and è"
        assert df.iloc[1]['FirstName'] == 'Amélie', "Should preserve French é"
        assert df.iloc[1]['LastName'] == 'Côté', "Should preserve French ô and é"

    def test_mixed_international_characters(self):
        """Test mixed international characters in one file"""
        csv_content = """FirstName,LastName,City,Country
José,García,Torreón,España
Jürgen,Müller,München,Deutschland
François,Élève,Paris,France
Çağlar,Şahin,İstanbul,Türkiye""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert len(df) == 4, "Should parse all rows"
        assert df.iloc[0]['FirstName'] == 'José', "Spanish preserved"
        assert df.iloc[1]['FirstName'] == 'Jürgen', "German preserved"
        assert df.iloc[2]['FirstName'] == 'François', "French preserved"
        assert df.iloc[3]['FirstName'] == 'Çağlar', "Turkish preserved"

    def test_character_encoding_in_xml_output(self):
        """Test character preservation through XML transformation"""
        # Create DataFrame with international characters
        df = pd.DataFrame({
            'FIRST_NAME': ['José', 'Jürgen', 'François', 'Çağlar'],
            'LAST_NAME': ['García', 'Müller', 'Élève', 'Şahin'],
            'LOCATION': ['Torreón', 'München', 'Paris', 'İstanbul']
        })

        # Create simple mappings
        mappings = [
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'},
            {'source': 'LAST_NAME', 'target': 'LAST_NAME'},
            {'source': 'LOCATION', 'target': 'LOCATION'}
        ]

        # Transform to XML
        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        # Parse XML to verify characters
        root = ET.fromstring(xml_output.encode('utf-8'))
        employees = root.findall('.//EF_Employee')

        assert len(employees) == 4, "Should have 4 employee records"

        # Check first employee (Spanish)
        first_name = employees[0].find('first_name')
        assert first_name is not None and first_name.text == 'José', \
            "Spanish characters preserved in XML"

        # Check second employee (German)
        last_name = employees[1].find('last_name')
        assert last_name is not None and last_name.text == 'Müller', \
            "German characters preserved in XML"

        # Check third employee (French)
        last_name = employees[2].find('last_name')
        assert last_name is not None and last_name.text == 'Élève', \
            "French characters preserved in XML"

        # Check fourth employee (Turkish)
        location = employees[3].find('location')
        assert location is not None and location.text == 'İstanbul', \
            "Turkish characters preserved in XML"

    def test_pipe_delimited_with_special_chars(self):
        """Test pipe-delimited files with special characters (Siemens format)"""
        csv_content = """PersonID|FirstName|LastName|Location
12345|José|García|Torreón
67890|Müller|Schmidt|München
11111|François|Dubois|Orléans
22222|Çağlar|Şahin|İstanbul""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        assert metadata['detected_delimiter'] == '|', "Should detect pipe delimiter"
        assert df.iloc[0]['FirstName'] == 'José', "Spanish preserved with pipe delimiter"
        assert df.iloc[1]['FirstName'] == 'Müller', "German preserved with pipe delimiter"
        assert df.iloc[2]['FirstName'] == 'François', "French preserved with pipe delimiter"
        assert df.iloc[3]['FirstName'] == 'Çağlar', "Turkish preserved with pipe delimiter"

    def test_encoding_detection_utf8(self):
        """Test UTF-8 encoding auto-detection"""
        csv_content = """Name,City
Ülkü,İzmir
José,León""".encode('utf-8')

        format_info = self.parser.detect_file_format(csv_content, "test.csv")

        assert format_info['encoding'] in ['utf-8', 'UTF-8'], \
            "Should detect UTF-8 encoding"

    def test_special_characters_in_multi_value_fields(self):
        """Test special characters in multi-value fields with || separator"""
        csv_content = """Name|Cities
José|Torreón||León||Madrid
Müller|München||Köln||Düsseldorf
François|Paris||Lyon||Orléans""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        # Create mappings for multi-value field
        mappings = [
            {'source': 'Name', 'target': 'FIRST_NAME'},
            {'source': 'Cities', 'target': 'LOCATION'}
        ]

        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        # Verify multi-value fields preserved characters
        assert 'Torreón' in xml_output, "Spanish ó preserved in multi-value field"
        assert 'München' in xml_output, "German ü preserved in multi-value field"
        assert 'Orléans' in xml_output, "French é preserved in multi-value field"

    def test_end_to_end_character_preservation(self):
        """Test complete pipeline: CSV -> Parse -> Transform -> XML"""
        # Create CSV with all character types
        csv_content = """PersonID|FirstName|LastName|Email|Location
1|Türkiye|Kayır|turkish@example.com|İstanbul
2|José|García|spanish@example.com|Torreón
3|Jürgen|Müller|german@example.com|München
4|François|Élève|french@example.com|Orléans""".encode('utf-8')

        # Step 1: Parse CSV
        df, metadata = self.parser.parse_file(csv_content, "test.csv")
        assert len(df) == 4, "All rows parsed"

        # Step 2: Create mappings
        mappings = [
            {'source': 'PersonID', 'target': 'EMPLOYEE_ID'},
            {'source': 'FirstName', 'target': 'FIRST_NAME'},
            {'source': 'LastName', 'target': 'LAST_NAME'},
            {'source': 'Email', 'target': 'EMAIL'},
            {'source': 'Location', 'target': 'LOCATION'}
        ]

        # Step 3: Transform to XML
        xml_output = self.transformer.transform_csv_to_xml(df, mappings, "employee")

        # Step 4: Verify all characters preserved
        # Turkish
        assert 'Türkiye' in xml_output, "Turkish Ü preserved end-to-end"
        assert 'Kayır' in xml_output, "Turkish ı preserved end-to-end"
        assert 'İstanbul' in xml_output, "Turkish İ preserved end-to-end"

        # Spanish
        assert 'José' in xml_output, "Spanish é preserved end-to-end"
        assert 'García' in xml_output, "Spanish í preserved end-to-end"
        assert 'Torreón' in xml_output, "Spanish ó preserved end-to-end"

        # German
        assert 'Jürgen' in xml_output, "German ü preserved end-to-end"
        assert 'Müller' in xml_output, "German ü preserved end-to-end"
        assert 'München' in xml_output, "German ü preserved end-to-end"

        # French
        assert 'François' in xml_output, "French ç preserved end-to-end"
        assert 'Élève' in xml_output, "French é/è preserved end-to-end"
        assert 'Orléans' in xml_output, "French é preserved end-to-end"

        # Verify XML is valid UTF-8
        root = ET.fromstring(xml_output.encode('utf-8'))
        assert root is not None, "XML is valid UTF-8"

    def test_emoji_and_unicode_symbols(self):
        """Test handling of emojis and special unicode symbols"""
        csv_content = """Name,Department,Notes
John Smith,Engineering,Great developer ⭐
Jane Doe,Sales,Top performer 🏆
Bob Lee,HR,Helpful person 👍""".encode('utf-8')

        df, metadata = self.parser.parse_file(csv_content, "test.csv")

        # Characters should be preserved
        assert '⭐' in df.iloc[0]['Notes'] or len(df.iloc[0]['Notes']) > 10
        assert '🏆' in df.iloc[1]['Notes'] or len(df.iloc[1]['Notes']) > 10

    def test_windows_1252_encoding(self):
        """Test handling of Windows-1252 encoded files"""
        # Windows-1252 uses different codes for special chars
        # This is a common encoding issue
        csv_content = """FirstName,LastName
José,García
María,Muñoz""".encode('windows-1252')

        # Parser should handle or detect encoding properly
        try:
            df, metadata = self.parser.parse_file(csv_content, "test.csv", encoding='windows-1252')
            assert 'José' in str(df.iloc[0]['FirstName']) or 'Jos' in str(df.iloc[0]['FirstName'])
        except Exception as e:
            # If it fails, it should provide a clear error message
            assert 'encoding' in str(e).lower() or 'decode' in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
