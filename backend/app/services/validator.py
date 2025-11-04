"""
Validation Engine
Validates data against schema requirements
"""

import re
from typing import List
import pandas as pd

from app.models.mapping import Mapping
from app.models.schema import EntitySchema
from app.models.validation import ValidationMessage, ValidationSummary, ValidationResult


class ValidationEngine:
    """Handles data validation"""

    def validate_mappings(
        self,
        mappings: List[Mapping],
        schema: EntitySchema
    ) -> ValidationResult:
        """
        Validate that mappings meet schema requirements

        Args:
            mappings: List of field mappings
            schema: Target schema

        Returns:
            ValidationResult with errors, warnings, and summary
        """
        errors = []
        warnings = []
        info = []

        # Get mapped target fields
        mapped_targets = {m.target for m in mappings}

        # Check required fields
        required_fields = schema.get_required_fields()
        required_mapped = 0

        for field in required_fields:
            if field.name in mapped_targets:
                required_mapped += 1
            else:
                if field.name == "LAST_ACTIVITY_TS":
                    # This field is auto-generated
                    info.append(ValidationMessage(
                        field=field.name,
                        message=f"Required field will be auto-generated with current timestamp",
                        severity="info"
                    ))
                    required_mapped += 1
                else:
                    errors.append(ValidationMessage(
                        field=field.name,
                        message=f"Required field '{field.display_name}' is not mapped",
                        severity="error",
                        suggestion=f"Map a source field to {field.name}"
                    ))

        # Check optional fields not mapped
        optional_fields = schema.get_optional_fields()
        for field in optional_fields:
            if field.name not in mapped_targets:
                warnings.append(ValidationMessage(
                    field=field.name,
                    message=f"Optional field '{field.display_name}' is not mapped",
                    severity="warning",
                    suggestion=f"Consider mapping a source field to {field.name} if available"
                ))

        # Calculate mapping completeness
        total_required = len(required_fields)
        mapping_completeness = (required_mapped / total_required * 100) if total_required > 0 else 100

        # Create summary
        summary = ValidationSummary(
            total_errors=len(errors),
            total_warnings=len(warnings),
            required_fields_mapped=required_mapped,
            required_fields_total=total_required,
            mapping_completeness=round(mapping_completeness, 2)
        )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            summary=summary
        )

    def validate_data(
        self,
        data: pd.DataFrame,
        schema: EntitySchema
    ) -> List[ValidationMessage]:
        """
        Validate actual data values against schema

        Args:
            data: DataFrame with data to validate
            schema: Target schema

        Returns:
            List of validation messages
        """
        messages = []

        for field in schema.fields:
            if field.name not in data.columns:
                continue

            column = data[field.name]

            # Validate email format
            if field.type == "email":
                invalid_emails = self._validate_email_column(column)
                for idx in invalid_emails:
                    messages.append(ValidationMessage(
                        field=field.name,
                        message=f"Invalid email format",
                        severity="error",
                        row_number=idx + 1,
                        suggestion="Ensure email is in format: name@domain.com"
                    ))

            # Validate date format
            if field.type == "date":
                invalid_dates = self._validate_date_column(column, field.format or "YYYY-MM-DD")
                for idx in invalid_dates:
                    messages.append(ValidationMessage(
                        field=field.name,
                        message=f"Invalid date format",
                        severity="warning",
                        row_number=idx + 1,
                        suggestion=f"Date should be in format: {field.format}"
                    ))

        return messages

    def _validate_email_column(self, series: pd.Series) -> List[int]:
        """Validate email format, return indices of invalid emails"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_indices = []

        for idx, value in series.items():
            if pd.notna(value):
                if not re.match(email_pattern, str(value)):
                    invalid_indices.append(idx)

        return invalid_indices

    def _validate_date_column(self, series: pd.Series, expected_format: str) -> List[int]:
        """Validate date format, return indices of invalid dates"""
        invalid_indices = []

        # Try to parse as datetime
        parsed = pd.to_datetime(series, errors='coerce')

        for idx, (original, parsed_val) in enumerate(zip(series, parsed)):
            if pd.notna(original) and pd.isna(parsed_val):
                invalid_indices.append(idx)

        return invalid_indices


# Singleton instance
_validation_engine = None


def get_validation_engine() -> ValidationEngine:
    """Get singleton ValidationEngine instance"""
    global _validation_engine
    if _validation_engine is None:
        _validation_engine = ValidationEngine()
    return _validation_engine
