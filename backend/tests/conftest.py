"""
Pytest Configuration and Fixtures

Provides shared fixtures and configuration for all tests.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_csv_comma_delimited():
    """Sample comma-delimited CSV content"""
    return b"""FirstName,LastName,Email,Phone
John,Doe,john@example.com,555-1234
Jane,Smith,jane@example.com,555-5678
Bob,Johnson,bob@example.com,555-0000"""


@pytest.fixture
def sample_csv_pipe_delimited():
    """Sample pipe-delimited CSV content (Siemens format)"""
    return b"""PersonID|FirstName|LastName|WorkEmails|WorkPhones
12345|John|Doe|john@company.com|555-1234
67890|Jane|Smith|jane@company.com||janes@other.com|555-5678||555-9999
11111|Bob|Johnson|bob@company.com|555-0000"""


@pytest.fixture
def sample_csv_with_special_chars():
    """Sample CSV with international characters"""
    return """FirstName,LastName,City,Country
José,García,Torreón,España
Jürgen,Müller,München,Deutschland
François,Élève,Paris,France
Çağlar,Şahin,İstanbul,Türkiye
Esra,Kayır,İstanbul,Türkiye""".encode('utf-8')


@pytest.fixture
def sample_dataframe_simple():
    """Simple pandas DataFrame for testing"""
    return pd.DataFrame({
        'FIRST_NAME': ['John', 'Jane', 'Bob'],
        'LAST_NAME': ['Doe', 'Smith', 'Johnson'],
        'EMAIL': ['john@test.com', 'jane@test.com', 'bob@test.com']
    })


@pytest.fixture
def sample_dataframe_multi_value():
    """DataFrame with multi-value fields"""
    return pd.DataFrame({
        'FIRST_NAME': ['John', 'Jane', 'Bob'],
        'EMAIL': [
            'john@company.com||john@personal.com',
            'jane@company.com',
            'bob@company.com||bob@other.com||bob@third.com'
        ],
        'PHONE': [
            '555-1111||555-2222',
            '555-3333',
            '555-4444||555-5555'
        ]
    })


@pytest.fixture
def sample_dataframe_special_chars():
    """DataFrame with international characters"""
    return pd.DataFrame({
        'FIRST_NAME': ['José', 'Jürgen', 'François', 'Çağlar'],
        'LAST_NAME': ['García', 'Müller', 'Élève', 'Şahin'],
        'CITY': ['Torreón', 'München', 'Paris', 'İstanbul']
    })


@pytest.fixture
def sample_field_mappings():
    """Sample field mappings for transformation"""
    return [
        {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'},
        {'source': 'LAST_NAME', 'target': 'LAST_NAME'},
        {'source': 'EMAIL', 'target': 'EMAIL'},
        {'source': 'PHONE', 'target': 'PHONE'}
    ]


@pytest.fixture
def siemens_field_names():
    """Common Siemens field names"""
    return [
        "PersonID",
        "FirstName",
        "LastName",
        "PreferredName",
        "WorkEmails",
        "HomeEmails",
        "WorkPhones",
        "HomePhones",
        "JobTitle",
        "Department",
        "Location",
        "HireDate",
        "ManagerID",
        "EmployeeStatus"
    ]


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_siemens_file: requires actual Siemens test file"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Mark end-to-end tests
        if "end_to_end" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)

        # Mark tests that require Siemens file
        if "siemens" in item.nodeid.lower():
            item.add_marker(pytest.mark.requires_siemens_file)


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def backend_dir():
    """Path to backend directory"""
    return Path(__file__).parent.parent
