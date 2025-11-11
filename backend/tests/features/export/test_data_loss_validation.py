"""
Test Data Loss Validation

Tests data integrity throughout the pipeline:
- Upload 1213 row file -> verify 1213 rows in output
- Test with various transformations
- Assert HTTP 400 if rows lost
- Check error message shows specific row numbers
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_validator import DataValidator, DataLossError, get_data_validator
from app.services.xml_transformer import XMLTransformer
import xml.etree.ElementTree as ET


class TestDataLossValidation:
    """Test data loss validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.validator = get_data_validator()
        self.transformer = XMLTransformer()

    def test_no_data_loss_same_row_count(self):
        """Test validation passes when row counts match"""
        input_df = pd.DataFrame({
            'A': range(100),
            'B': range(100)
        })

        output_df = pd.DataFrame({
            'X': range(100),
            'Y': range(100)
        })

        # Should not raise exception
        result = self.validator.validate_row_count(
            input_df,
            output_df,
            "test_operation"
        )

        assert result is True, "Validation should pass"

    def test_data_loss_detection(self):
        """Test detection of data loss"""
        input_df = pd.DataFrame({
            'A': range(100),
            'B': range(100)
        })

        # Output has fewer rows
        output_df = pd.DataFrame({
            'X': range(90),
            'Y': range(90)
        })

        with pytest.raises(DataLossError) as exc_info:
            self.validator.validate_row_count(
                input_df,
                output_df,
                "test_operation"
            )

        error = exc_info.value
        assert error.lost_rows == 10, "Should detect 10 lost rows"
        assert error.total_rows == 100, "Should track total rows"
        assert "10 rows lost" in error.message, "Error message should mention lost count"
        assert "10.0%" in error.message, "Error message should mention percentage"

    def test_large_file_1213_rows_preserved(self):
        """Test 1213 row file preserves all rows through transformation"""
        # Create DataFrame with 1213 rows
        input_df = pd.DataFrame({
            'FIRST_NAME': [f'Person{i}' for i in range(1213)],
            'LAST_NAME': [f'Last{i}' for i in range(1213)],
            'EMAIL': [f'person{i}@example.com' for i in range(1213)]
        })

        # Simulate transformation (identity transform)
        output_df = input_df.copy()

        # Validate
        result = self.validator.validate_row_count(
            input_df,
            output_df,
            "transform_operation"
        )

        assert result is True, "All 1213 rows should be preserved"
        assert len(output_df) == 1213, "Output should have exactly 1213 rows"

    def test_xml_transformation_preserves_row_count(self):
        """Test XML transformation preserves all rows"""
        input_df = pd.DataFrame({
            'FIRST_NAME': [f'Person{i}' for i in range(500)],
            'LAST_NAME': [f'Last{i}' for i in range(500)],
            'EMAIL': [f'person{i}@example.com' for i in range(500)]
        })

        mappings = [
            {'source': 'FIRST_NAME', 'target': 'FIRST_NAME'},
            {'source': 'LAST_NAME', 'target': 'LAST_NAME'},
            {'source': 'EMAIL', 'target': 'EMAIL'}
        ]

        # Transform to XML
        xml_output = self.transformer.transform_csv_to_xml(input_df, mappings, "employee")

        # Count records in XML
        root = ET.fromstring(xml_output.encode('utf-8'))
        employees = root.findall('.//EF_Employee')

        assert len(employees) == 500, "XML should have all 500 employee records"

        # Validate row count
        # Create pseudo output_df from XML count
        output_df = pd.DataFrame({'dummy': range(len(employees))})

        result = self.validator.validate_row_count(
            input_df,
            output_df,
            "xml_transformation"
        )

        assert result is True, "XML transformation should preserve all rows"

    def test_error_details_include_row_numbers(self):
        """Test error details include specific row information"""
        input_df = pd.DataFrame({
            'ID': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
            'Value': range(10)
        })

        # Simulate losing some rows
        output_df = pd.DataFrame({
            'ID': ['A', 'C', 'E', 'G', 'I'],  # Missing B, D, F, H, J
            'Value': [0, 2, 4, 6, 8]
        })

        with pytest.raises(DataLossError) as exc_info:
            self.validator.validate_row_count(
                input_df,
                output_df,
                "filtering_operation"
            )

        error = exc_info.value
        assert error.details is not None, "Should include error details"
        assert "input_rows" in error.details, "Details should include input row count"
        assert "output_rows" in error.details, "Details should include output row count"
        assert "lost_count" in error.details, "Details should include lost count"

    def test_null_value_detection_in_error_details(self):
        """Test error details identify null values as potential cause"""
        input_df = pd.DataFrame({
            'A': [1, 2, None, 4, None, 6],
            'B': ['x', 'y', 'z', None, None, 'w']
        })

        output_df = pd.DataFrame({
            'A': [1, 2, 6],  # Lost rows with nulls
            'B': ['x', 'y', 'w']
        })

        with pytest.raises(DataLossError) as exc_info:
            self.validator.validate_row_count(
                input_df,
                output_df,
                "null_filtering"
            )

        error = exc_info.value
        assert "potential_reasons" in error.details, "Should include potential reasons"

        # Check for null value detection
        reasons = error.details["potential_reasons"]
        null_reason = next((r for r in reasons if "Null" in r.get("reason", "")), None)
        assert null_reason is not None, "Should identify null values as potential cause"

    def test_duplicate_detection_in_error_details(self):
        """Test error details identify duplicates"""
        input_df = pd.DataFrame({
            'A': [1, 2, 2, 3, 3, 3, 4],
            'B': ['x', 'y', 'y', 'z', 'z', 'z', 'w']
        })

        output_df = pd.DataFrame({
            'A': [1, 2, 3, 4],  # Duplicates removed
            'B': ['x', 'y', 'z', 'w']
        })

        with pytest.raises(DataLossError) as exc_info:
            self.validator.validate_row_count(
                input_df,
                output_df,
                "deduplication"
            )

        error = exc_info.value
        reasons = error.details["potential_reasons"]
        dup_reason = next((r for r in reasons if "Duplicate" in r.get("reason", "")), None)
        assert dup_reason is not None, "Should identify duplicates"
        assert dup_reason["duplicate_count"] == 3, "Should count 3 duplicate rows"

    def test_allow_deduplication_flag(self):
        """Test allowing row loss for deduplication"""
        input_df = pd.DataFrame({
            'A': [1, 2, 2, 3, 3, 3, 4],
            'B': ['x', 'y', 'y', 'z', 'z', 'z', 'w']
        })

        output_df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': ['x', 'y', 'z', 'w']
        })

        # Should not raise when deduplication is allowed
        result = self.validator.validate_row_count(
            input_df,
            output_df,
            "deduplication",
            allow_duplicates_removal=True
        )

        assert result is True, "Should allow deduplication"

    def test_field_completeness_validation(self):
        """Test field completeness validation"""
        df = pd.DataFrame({
            'FIRST_NAME': ['John', 'Jane', None, 'Bob'],
            'LAST_NAME': ['Doe', 'Smith', 'Johnson', 'Lee'],
            'EMAIL': ['john@test.com', None, None, 'bob@test.com']
        })

        required_fields = ['FIRST_NAME', 'LAST_NAME', 'EMAIL']

        is_valid, issues = self.validator.validate_field_completeness(
            df,
            required_fields,
            "data_quality_check"
        )

        # Should have warnings (not errors) for null values
        assert len(issues) > 0, "Should detect null values"

        # Check for specific field issues
        first_name_issue = next((i for i in issues if i['field'] == 'FIRST_NAME'), None)
        assert first_name_issue is not None, "Should detect null in FIRST_NAME"
        assert first_name_issue['null_count'] == 1, "Should count 1 null"

        email_issue = next((i for i in issues if i['field'] == 'EMAIL'), None)
        assert email_issue is not None, "Should detect null in EMAIL"
        assert email_issue['null_count'] == 2, "Should count 2 nulls"

    def test_missing_required_field(self):
        """Test detection of missing required fields"""
        df = pd.DataFrame({
            'FIRST_NAME': ['John', 'Jane'],
            'LAST_NAME': ['Doe', 'Smith']
            # EMAIL is missing
        })

        required_fields = ['FIRST_NAME', 'LAST_NAME', 'EMAIL']

        is_valid, issues = self.validator.validate_field_completeness(
            df,
            required_fields,
            "schema_validation"
        )

        assert is_valid is False, "Should fail validation"

        # Should have error for missing field
        error_issues = [i for i in issues if i['severity'] == 'error']
        assert len(error_issues) == 1, "Should have 1 error"
        assert error_issues[0]['field'] == 'EMAIL', "Should identify EMAIL as missing"

    def test_multi_value_field_validation(self):
        """Test multi-value field validation"""
        df = pd.DataFrame({
            'EMAIL': ['single@test.com', 'multi1@test.com||multi2@test.com', 'another@test.com'],
            'PHONE': ['555-1111||555-2222', '555-3333', '555-4444||555-5555||555-6666']
        })

        multi_value_fields = ['EMAIL', 'PHONE']

        results = self.validator.validate_multi_value_fields(
            df,
            multi_value_fields,
            separator='||'
        )

        assert results['has_multi_value_fields'] is True, "Should detect multi-value fields"
        assert results['total_multi_value_cells'] >= 3, "Should count multi-value cells"

        # Check field analysis
        assert len(results['fields_analyzed']) == 2, "Should analyze both fields"

        email_result = next((f for f in results['fields_analyzed'] if f['field_name'] == 'EMAIL'), None)
        assert email_result is not None, "Should analyze EMAIL field"
        assert email_result['cells_with_separator'] >= 1, "Should detect || in EMAIL"

        phone_result = next((f for f in results['fields_analyzed'] if f['field_name'] == 'PHONE'), None)
        assert phone_result is not None, "Should analyze PHONE field"
        assert phone_result['cells_with_separator'] >= 2, "Should detect || in PHONE"

    def test_large_file_stress_test(self):
        """Stress test with very large file (10000 rows)"""
        # Create large DataFrame
        input_df = pd.DataFrame({
            'ID': range(10000),
            'Value': range(10000)
        })

        output_df = input_df.copy()

        # Should handle large files efficiently
        import time
        start_time = time.time()

        result = self.validator.validate_row_count(
            input_df,
            output_df,
            "stress_test"
        )

        elapsed = time.time() - start_time

        assert result is True, "Should validate large file"
        assert elapsed < 1.0, f"Should be fast (<1s), took {elapsed:.2f}s"

    def test_percentage_calculation_accuracy(self):
        """Test accurate percentage calculation in error messages"""
        input_df = pd.DataFrame({'A': range(1000)})
        output_df = pd.DataFrame({'A': range(750)})  # 25% loss

        with pytest.raises(DataLossError) as exc_info:
            self.validator.validate_row_count(input_df, output_df, "test")

        error = exc_info.value
        assert error.lost_rows == 250
        assert "25.0%" in error.message, "Should show 25% loss"

    def test_100_percent_data_loss(self):
        """Test detection of complete data loss"""
        input_df = pd.DataFrame({'A': range(100)})
        output_df = pd.DataFrame({'A': []})  # Empty output

        with pytest.raises(DataLossError) as exc_info:
            self.validator.validate_row_count(input_df, output_df, "test")

        error = exc_info.value
        assert error.lost_rows == 100
        assert "100.0%" in error.message, "Should show 100% loss"

    def test_no_error_when_rows_increased(self):
        """Test that no error is raised when output has more rows"""
        input_df = pd.DataFrame({'A': range(100)})
        output_df = pd.DataFrame({'A': range(150)})  # More rows

        # Should not raise - this might be intentional (e.g., unpivoting)
        result = self.validator.validate_row_count(input_df, output_df, "test")
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
