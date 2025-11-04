"""
Auto-mapping API endpoints
"""

from fastapi import APIRouter, HTTPException

from app.models.mapping import AutoMapRequest, AutoMapResponse
from app.services.schema_manager import get_schema_manager
from app.services.field_mapper import get_field_mapper

router = APIRouter()


@router.post("/auto-map", response_model=AutoMapResponse)
async def auto_map_fields(request: AutoMapRequest):
    """
    Automatically map source fields to target fields using fuzzy matching

    This is the KEY feature of the application!

    Args:
        request: AutoMapRequest with source fields and options

    Returns:
        AutoMapResponse with mappings and statistics

    Raises:
        400: Invalid request (empty source fields)
        404: Target schema not found
        500: Error during auto-mapping
    """
    # Validate request
    if not request.source_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "source_fields cannot be empty",
                },
                "status": 400
            }
        )

    try:
        # Get target schema
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema(request.target_schema)

        # Perform auto-mapping
        mapper = get_field_mapper()
        mappings = mapper.auto_map(
            request.source_fields,
            schema,
            request.min_confidence
        )

        # Calculate statistics
        mapped_count = len(mappings)
        total_source = len(request.source_fields)
        total_target = len(schema.fields)

        # Get unmapped fields
        mapped_sources = {m.source for m in mappings}
        unmapped_source = [f for f in request.source_fields if f not in mapped_sources]

        mapped_targets = {m.target for m in mappings}
        unmapped_target = [f.name for f in schema.fields if f.name not in mapped_targets]

        # Calculate mapping percentage
        mapping_percentage = (mapped_count / total_source * 100) if total_source > 0 else 0

        return AutoMapResponse(
            mappings=mappings,
            total_mapped=mapped_count,
            total_source=total_source,
            total_target=total_target,
            mapping_percentage=round(mapping_percentage, 2),
            unmapped_source=unmapped_source,
            unmapped_target=unmapped_target
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SCHEMA_NOT_FOUND",
                    "message": f"Schema '{request.target_schema}' not found",
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
                },
                "status": 500
            }
        )
