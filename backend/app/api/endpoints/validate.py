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
        404: Schema not found
        422: Validation failed with specific errors
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

        # If there are validation errors, return them with a helpful message
        if result.errors:
            error_count = len(result.errors)
            sample_errors = result.errors[:5]  # Show first 5 errors

            error_summary = []
            for err in sample_errors:
                if err.row_number:
                    error_summary.append(f"Row {err.row_number}: {err.message}")
                else:
                    error_summary.append(f"{err.field}: {err.message}")

            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "VALIDATION_FAILED",
                        "message": f"Validation failed for {error_count} record(s)",
                        "details": {
                            "total_errors": error_count,
                            "sample_errors": error_summary,
                            "full_validation_result": result.dict()
                        },
                        "suggestion": "Review the errors and fix the data. Download error report for complete details."
                    },
                    "status": 422
                }
            )

        return result

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SCHEMA_NOT_FOUND",
                    "message": f"Schema '{request.schema_name}' not found",
                    "suggestion": "Available schemas: employee, candidate. Check the schema name."
                },
                "status": 404
            }
        )
    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Error during validation: {error_message}",
                    "suggestion": "Check that mappings are in correct format and data is valid JSON."
                },
                "status": 500
            }
        )
