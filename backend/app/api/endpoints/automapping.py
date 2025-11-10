"""
Auto-mapping API endpoints
"""

from fastapi import APIRouter, HTTPException

from app.models.mapping import AutoMapRequest, AutoMapResponse
from app.services.schema_manager import get_schema_manager
from app.services.field_mapper import get_field_mapper
from app.services.file_storage import get_file_storage
from app.services.file_parser import get_file_parser

router = APIRouter()


@router.post("/auto-map", response_model=AutoMapResponse)
async def auto_map_fields(request: AutoMapRequest):
    """
    Automatically map source fields to target fields using fuzzy matching

    This is the KEY feature of the application!

    Args:
        request: AutoMapRequest with file_id OR source_fields and options

    Returns:
        AutoMapResponse with mappings and statistics

    Raises:
        400: Invalid request (missing both file_id and source_fields)
        404: Target schema or file not found
        500: Error during auto-mapping
    """
    # Extract source fields from file_id if provided
    source_fields = request.source_fields
    column_types = {}
    df = None

    if not source_fields and request.file_id:
        # Auto-extract source fields from uploaded file
        storage = get_file_storage()
        df = storage.retrieve_dataframe(request.file_id)

        if df is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": f"File with ID '{request.file_id}' not found or expired",
                        "suggestion": "Please upload the file again to get a new file_id"
                    },
                    "status": 404
                }
            )

        source_fields = df.columns.tolist()

        # Detect column types from actual data
        file_parser = get_file_parser()
        column_types = file_parser.detect_column_types(df)

    # Validate request
    if not source_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Either 'file_id' or 'source_fields' must be provided",
                    "suggestion": "Upload a file first and use the file_id, or manually provide source_fields"
                },
                "status": 400
            }
        )

    try:
        # Get target schema
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema(request.target_schema)

        # Perform auto-mapping with column type hints
        mapper = get_field_mapper()
        mappings = mapper.auto_map(
            source_fields,
            schema,
            request.min_confidence,
            column_types=column_types  # Pass detected column types
        )

        # Calculate statistics
        mapped_count = len(mappings)
        total_source = len(source_fields)
        total_target = len(schema.fields)

        # Get unmapped fields
        mapped_sources = {m.source for m in mappings}
        unmapped_source = [f for f in source_fields if f not in mapped_sources]

        mapped_targets = {m.target for m in mappings}
        unmapped_target = [f.name for f in schema.fields if f.name not in mapped_targets]

        # Get required fields that are unmapped
        required_fields = schema.get_required_fields()
        required_unmapped = [f.name for f in required_fields if f.name not in mapped_targets]

        # Calculate mapping percentage
        mapping_percentage = (mapped_count / total_source * 100) if total_source > 0 else 0

        # If mapping percentage is very low, provide helpful error
        if mapping_percentage < 15 and mapped_count < 5:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "LOW_MAPPING_CONFIDENCE",
                        "message": f"Data mapping failed. Only {mapped_count} of {total_source} fields mapped ({mapping_percentage:.1f}%).",
                        "details": {
                            "mapped_count": mapped_count,
                            "total_source": total_source,
                            "mapping_percentage": round(mapping_percentage, 2),
                            "required_fields_missing": required_unmapped,
                            "unmapped_source_fields": unmapped_source[:10]
                        },
                        "suggestion": f"Required fields missing: {', '.join(required_unmapped[:5])}. Check field names or adjust mapping manually."
                    },
                    "status": 422
                }
            )

        return AutoMapResponse(
            mappings=mappings,
            total_mapped=mapped_count,
            total_source=total_source,
            total_target=total_target,
            mapping_percentage=round(mapping_percentage, 2),
            unmapped_source=unmapped_source,
            unmapped_target=unmapped_target
        )

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SCHEMA_NOT_FOUND",
                    "message": f"Target schema '{request.target_schema}' not found",
                    "suggestion": "Available schemas: employee, candidate. Check the schema name spelling."
                },
                "status": 404
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "AUTO_MAP_ERROR",
                    "message": f"Error during auto-mapping: {str(e)}",
                    "suggestion": "Check that all field names are valid strings and try again."
                },
                "status": 500
            }
        )
