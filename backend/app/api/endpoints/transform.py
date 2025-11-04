"""
Transformation API endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import StringIO

from app.models.transform import PreviewRequest, PreviewResponse, ExportRequest
from app.services.transformer import get_transformation_engine
from app.services.schema_manager import get_schema_manager
from app.services.file_storage import get_file_storage

router = APIRouter()


@router.post("/transform/preview", response_model=PreviewResponse)
async def preview_transformation(request: PreviewRequest):
    """
    Preview data transformation with current mappings

    Args:
        request: PreviewRequest with mappings and source data

    Returns:
        PreviewResponse with transformed sample data

    Raises:
        400: Invalid request
        500: Error during transformation
    """
    try:
        # Get schema
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema(request.entity_name)

        # Transform data
        engine = get_transformation_engine()
        transformed_df, transformations = engine.transform_data(
            request.source_data,
            request.mappings,
            schema
        )

        # Get sample
        sample_size = min(request.sample_size or 5, len(transformed_df))
        sample_df = transformed_df.head(sample_size)

        return PreviewResponse(
            transformed_data=sample_df.to_dict('records'),
            transformations_applied=transformations,
            row_count=len(transformed_df),
            warnings=[]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "TRANSFORMATION_ERROR",
                    "message": f"Error during transformation: {str(e)}",
                },
                "status": 500
            }
        )


@router.post("/transform/export")
async def export_csv(request: ExportRequest):
    """
    Export transformed data as CSV file

    Args:
        request: ExportRequest with mappings and source data (or file_id)

    Returns:
        CSV file as download

    Raises:
        400: Invalid request (neither source_data nor file_id provided)
        404: File not found (if using file_id)
        500: Error during export
    """
    try:
        # Get source data - either from request or from stored file
        source_data = request.source_data

        if source_data is None and request.file_id:
            # Retrieve full data from storage using file_id
            storage = get_file_storage()
            df = storage.retrieve_dataframe(request.file_id)

            if df is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": {
                            "code": "FILE_NOT_FOUND",
                            "message": f"File with ID '{request.file_id}' not found or expired",
                        },
                        "status": 404
                    }
                )

            # Convert DataFrame to list of dicts
            source_data = df.to_dict('records')

        elif source_data is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "MISSING_SOURCE_DATA",
                        "message": "Either 'source_data' or 'file_id' must be provided",
                    },
                    "status": 400
                }
            )

        # Get schema
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema(request.entity_name)

        # Transform all data
        engine = get_transformation_engine()
        transformed_df, _ = engine.transform_data(
            source_data,
            request.mappings,
            schema
        )

        # Convert to CSV
        csv_buffer = StringIO()
        transformed_df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()

        # Return as file download
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={request.output_filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "EXPORT_ERROR",
                    "message": f"Error exporting CSV: {str(e)}",
                },
                "status": 500
            }
        )
