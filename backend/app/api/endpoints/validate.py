"""
Validation API endpoints
"""

from fastapi import APIRouter, HTTPException
import pandas as pd

from app.models.validation import ValidationRequest, ValidationResult
from app.services.validator import get_validation_engine
from app.services.schema_manager import get_schema_manager

router = APIRouter()


@router.post("/validate", response_model=ValidationResult)
async def validate_data(request: ValidationRequest):
    """
    Validate mappings and data against schema

    Args:
        request: ValidationRequest with mappings and optional source data

    Returns:
        ValidationResult with errors, warnings, and summary

    Raises:
        400: Invalid request
        500: Error during validation
    """
    try:
        # Get schema
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema(request.schema_name)

        # Validate mappings
        validator = get_validation_engine()
        result = validator.validate_mappings(request.mappings, schema)

        # If source data provided, validate data values
        if request.source_data:
            df = pd.DataFrame(request.source_data)
            data_messages = validator.validate_data(df, schema)

            # Add data validation messages to result
            for msg in data_messages:
                if msg.severity == "error":
                    result.errors.append(msg)
                elif msg.severity == "warning":
                    result.warnings.append(msg)
                else:
                    result.info.append(msg)

            # Update summary
            result.summary.total_errors = len(result.errors)
            result.summary.total_warnings = len(result.warnings)
            result.is_valid = len(result.errors) == 0

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Error during validation: {str(e)}",
                },
                "status": 500
            }
        )
