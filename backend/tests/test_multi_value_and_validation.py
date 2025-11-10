"""
Test Multi-Value Field Support and Data Loss Validation
"""

import pytest
import pandas as pd
from xml.etree.ElementTree import fromstring

from app.services.xml_transformer import get_xml_transformer
from app.services.data_validator import get_data_validator, DataLossError
from app.services.transformer import get_transformation_engine
from app.models.schema import EntitySchema, FieldDefinition
from app.models.mapping import Mapping


class TestMultiValueFields:
    """Test multi-value field support with || separator"""

    def test_multi_value_emails_with_pipe_separator(self):
        """Test that emails separated by || are properly split into XML list"""
        # Setup
        transformer = get_xml_transformer()
        df = pd.DataFrame([
            {
                'EmployeeID': '12345',
                'WorkEmails': 'john@company.com||john.doe@company.com'
            }
        ])

        mappings = [
            {'source': 'EmployeeID', 'target': 'EMPLOYEE_ID'},
            {'source': 'WorkEmails', 'target': 'EMAIL'}
        ]

        # Execute
        xml_content = transformer.transform_csv_to_xml(
            df=df,
            mappings=mappings,
            entity_name='employee'
        )

        # Verify
        root = fromstring(xml_content)
        employee = root.find('EF_Employee')
        assert employee is not None

        email_list = employee.find('email_list')
        assert email_list is not None

        emails = email_list.findall('email')
        assert len(emails) == 2
        assert emails[0].text == 'john@company.com'
        assert emails[1].text == 'john.doe@company.com'

    def test_multi_value_phones_with_pipe_separator(self):
        """Test that phone numbers separated by || are properly split"""
        transformer = get_xml_transformer()
        df = pd.DataFrame([
            {
                'EmployeeID': '12345',
                'WorkPhones': '555-1234||555-5678||555-9999'
            }
        ])

        mappings = [
            {'source': 'EmployeeID', 'target': 'EMPLOYEE_ID'},
            {'source': 'WorkPhones', 'target': 'PHONE'}
        ]

        xml_content = transformer.transform_csv_to_xml(
            df=df,
            mappings=mappings,
            entity_name='employee'
        )

        root = fromstring(xml_content)
        employee = root.find('EF_Employee')
        phone_list = employee.find('phone_list')
        phones = phone_list.findall('phone')

        assert len(phones) == 3
        assert phones[0].text == '555-1234'
        assert phones[1].text == '555-5678'
        assert phones[2].text == '555-9999'

    def test_comma_separated_fallback(self):
        """Test that comma-separated values still work"""
        transformer = get_xml_transformer()
        df = pd.DataFrame([
            {
                'EmployeeID': '12345',
                'WorkEmails': 'john@company.com,jane@company.com'
            }
        ])

        mappings = [
            {'source': 'EmployeeID', 'target': 'EMPLOYEE_ID'},
            {'source': 'WorkEmails', 'target': 'EMAIL'}
        ]

        xml_content = transformer.transform_csv_to_xml(
            df=df,
            mappings=mappings,
            entity_name='employee'
        )

        root = fromstring(xml_content)
        employee = root.find('EF_Employee')
        email_list = employee.find('email_list')
        emails = email_list.findall('email')

        assert len(emails) == 2
        assert emails[0].text == 'john@company.com'
        assert emails[1].text == 'jane@company.com'

    def test_single_value_no_separator(self):
        """Test that single values without separators work"""
        transformer = get_xml_transformer()
        df = pd.DataFrame([
            {
                'EmployeeID': '12345',
                'WorkEmail': 'john@company.com'
            }
        ])

        mappings = [
            {'source': 'EmployeeID', 'target': 'EMPLOYEE_ID'},
            {'source': 'WorkEmail', 'target': 'EMAIL'}
        ]

        xml_content = transformer.transform_csv_to_xml(
            df=df,
            mappings=mappings,
            entity_name='employee'
        )

        root = fromstring(xml_content)
        employee = root.find('EF_Employee')
        email_list = employee.find('email_list')
        emails = email_list.findall('email')

        assert len(emails) == 1
        assert emails[0].text == 'john@company.com'


class TestDataLossValidation:
    """Test data loss validation throughout pipeline"""

    def test_validate_row_count_success(self):
        """Test that equal row counts pass validation"""
        validator = get_data_validator()
        input_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        output_df = pd.DataFrame({'C': [7, 8, 9], 'D': [10, 11, 12]})

        # Should not raise exception
        result = validator.validate_row_count(
            input_df=input_df,
            output_df=output_df,
            operation_name="test operation"
        )
        assert result is True

    def test_validate_row_count_data_loss(self):
        """Test that row loss is detected"""
        validator = get_data_validator()
        input_df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        output_df = pd.DataFrame({'B': [1, 2, 3]})

        with pytest.raises(DataLossError) as exc_info:
            validator.validate_row_count(
                input_df=input_df,
                output_df=output_df,
                operation_name="test operation"
            )

        error = exc_info.value
        assert error.lost_rows == 2
        assert error.total_rows == 5
        assert "test operation" in error.message
        assert "2 rows lost" in error.message

    def test_validate_row_count_more_output_rows(self):
        """Test that more output rows is allowed"""
        validator = get_data_validator()
        input_df = pd.DataFrame({'A': [1, 2, 3]})
        output_df = pd.DataFrame({'B': [1, 2, 3, 4, 5]})

        # Should not raise exception (data expansion is OK)
        result = validator.validate_row_count(
            input_df=input_df,
            output_df=output_df,
            operation_name="test operation"
        )
        assert result is True

    def test_validate_field_completeness_all_present(self):
        """Test field completeness validation with all fields present"""
        validator = get_data_validator()
        df = pd.DataFrame({
            'EMPLOYEE_ID': ['1', '2', '3'],
            'EMAIL': ['a@b.com', 'c@d.com', 'e@f.com'],
            'NAME': ['John', 'Jane', 'Bob']
        })

        is_valid, issues = validator.validate_field_completeness(
            df=df,
            required_fields=['EMPLOYEE_ID', 'EMAIL'],
            operation_name="test"
        )

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_field_completeness_missing_field(self):
        """Test field completeness validation with missing field"""
        validator = get_data_validator()
        df = pd.DataFrame({
            'EMPLOYEE_ID': ['1', '2', '3'],
            'NAME': ['John', 'Jane', 'Bob']
        })

        is_valid, issues = validator.validate_field_completeness(
            df=df,
            required_fields=['EMPLOYEE_ID', 'EMAIL'],
            operation_name="test"
        )

        assert is_valid is False
        assert len(issues) == 1
        assert issues[0]['field'] == 'EMAIL'
        assert issues[0]['severity'] == 'error'
        assert 'missing' in issues[0]['message'].lower()

    def test_validate_field_completeness_null_values(self):
        """Test field completeness validation with null values"""
        validator = get_data_validator()
        df = pd.DataFrame({
            'EMPLOYEE_ID': ['1', '2', None],
            'EMAIL': ['a@b.com', None, 'e@f.com']
        })

        is_valid, issues = validator.validate_field_completeness(
            df=df,
            required_fields=['EMPLOYEE_ID', 'EMAIL'],
            operation_name="test"
        )

        assert is_valid is True  # Null values generate warnings, not errors
        assert len(issues) == 2  # One warning for each field with nulls
        assert all(issue['severity'] == 'warning' for issue in issues)

    def test_validate_multi_value_fields_detection(self):
        """Test multi-value field detection"""
        validator = get_data_validator()
        df = pd.DataFrame({
            'EMAIL': ['a@b.com||c@d.com', 'e@f.com', 'g@h.com||i@j.com'],
            'PHONE': ['555-1234', '555-5678', '555-9999'],
            'NAME': ['John', 'Jane', 'Bob']
        })

        result = validator.validate_multi_value_fields(
            df=df,
            multi_value_fields=['EMAIL', 'PHONE', 'NAME'],
            separator='||'
        )

        assert result['has_multi_value_fields'] is True
        assert len(result['fields_analyzed']) == 1
        assert result['fields_analyzed'][0]['field_name'] == 'EMAIL'
        assert result['fields_analyzed'][0]['cells_with_separator'] == 2
        assert result['total_multi_value_cells'] == 2

    def test_transformation_with_data_loss_validation(self):
        """Test that transformation engine validates row counts"""
        # Create a simple schema
        schema = EntitySchema(
            entity_name="employee",
            display_name="Employee",
            description="Employee schema for testing",
            fields=[
                FieldDefinition(
                    name="EMPLOYEE_ID",
                    display_name="Employee ID",
                    type="string",
                    required=True,
                    example="12345",
                    description="Unique employee identifier"
                ),
                FieldDefinition(
                    name="EMAIL",
                    display_name="Email",
                    type="email",
                    required=False,
                    example="john@company.com",
                    description="Employee email address"
                )
            ]
        )

        # Create test data
        source_data = [
            {'EmpID': '1', 'Email': 'a@b.com'},
            {'EmpID': '2', 'Email': 'c@d.com'},
            {'EmpID': '3', 'Email': 'e@f.com'}
        ]

        mappings = [
            Mapping(source='EmpID', target='EMPLOYEE_ID', confidence=1.0, method='manual'),
            Mapping(source='Email', target='EMAIL', confidence=1.0, method='manual')
        ]

        engine = get_transformation_engine()

        # This should succeed (no data loss)
        transformed_df, transformations = engine.transform_data(
            source_data=source_data,
            mappings=mappings,
            schema=schema
        )

        assert len(transformed_df) == 3
        assert 'EMPLOYEE_ID' in transformed_df.columns
        assert 'EMAIL' in transformed_df.columns


class TestErrorMessages:
    """Test improved error messages"""

    def test_data_loss_error_details(self):
        """Test that DataLossError contains detailed information"""
        error = DataLossError(
            message="Test data loss",
            lost_rows=5,
            total_rows=100,
            details={
                "operation": "test",
                "potential_reasons": ["nulls", "duplicates"]
            }
        )

        assert error.message == "Test data loss"
        assert error.lost_rows == 5
        assert error.total_rows == 100
        assert "operation" in error.details
        assert "potential_reasons" in error.details

    def test_multi_value_detection_in_validator(self):
        """Test that multi-value detection returns proper structure"""
        validator = get_data_validator()
        df = pd.DataFrame({
            'Emails': ['a@b.com||c@d.com||e@f.com', 'g@h.com'],
        })

        result = validator.validate_multi_value_fields(
            df=df,
            multi_value_fields=['Emails'],
            separator='||'
        )

        assert 'has_multi_value_fields' in result
        assert 'fields_analyzed' in result
        assert 'total_multi_value_cells' in result
        assert result['has_multi_value_fields'] is True
        assert len(result['fields_analyzed']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
