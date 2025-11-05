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
from app.services.xml_transformer import get_xml_transformer

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


@router.post("/transform/preview-xml")
async def preview_xml_transformation(request: PreviewRequest):
    """
    Preview XML transformation with current mappings

    Returns a sample of the data transformed to Eightfold XML format

    Args:
        request: PreviewRequest with mappings and source data

    Returns:
        XML preview string

    Raises:
        400: Invalid request
        500: Error during transformation
    """
    try:
        import pandas as pd

        # Get source data
        source_data = request.source_data
        print(f"[XML_PREVIEW_DEBUG] file_id: {request.file_id}, has_source_data: {source_data is not None}")
        print(f"[XML_PREVIEW_DEBUG] mappings type: {type(request.mappings)}, first mapping type: {type(request.mappings[0]) if request.mappings else None}")

        if source_data is None and request.file_id:
            storage = get_file_storage()
            df = storage.get_dataframe(request.file_id)
            if df is None:
                raise HTTPException(status_code=404, detail="File not found")
            print(f"[XML_PREVIEW_DEBUG] Loaded DataFrame with {len(df)} rows, columns: {list(df.columns)}")
        else:
            df = pd.DataFrame(source_data)
            print(f"[XML_PREVIEW_DEBUG] Created DataFrame from source_data with {len(df)} rows")

        # Get sample
        sample_size = min(request.sample_size or 5, len(df))
        sample_df = df.head(sample_size)
        print(f"[XML_PREVIEW_DEBUG] Sample size: {sample_size}")

        # Transform to XML
        xml_transformer = get_xml_transformer()
        # Convert Pydantic models to dicts for xml_transformer
        print(f"[XML_PREVIEW_DEBUG] Converting mappings to dicts...")
        # Try model_dump() first (Pydantic v2), fallback to dict() (Pydantic v1)
        try:
            mappings_dicts = [m.model_dump() if hasattr(m, 'model_dump') else m.dict() for m in request.mappings]
        except Exception as e:
            print(f"[XML_PREVIEW_DEBUG] Error converting mappings: {e}")
            # If both fail, just try to access as dict
            mappings_dicts = [dict(m) for m in request.mappings]
        print(f"[XML_PREVIEW_DEBUG] Mappings converted. First mapping: {mappings_dicts[0] if mappings_dicts else None}")

        print(f"[XML_PREVIEW_DEBUG] Calling xml_transformer.transform_csv_to_xml...")
        xml_content = xml_transformer.transform_csv_to_xml(
            df=sample_df,
            mappings=mappings_dicts,
            entity_name=request.entity_name
        )
        print(f"[XML_PREVIEW_DEBUG] XML transform complete, length: {len(xml_content)}")

        return {
            "xml_preview": xml_content,
            "preview_row_count": sample_size,
            "total_row_count": len(df)
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[XML_PREVIEW_ERROR] {error_traceback}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "XML_PREVIEW_ERROR",
                    "message": f"Error generating XML preview: {str(e)}",
                },
                "status": 500
            }
        )


@router.post("/transform/export-xml")
async def export_xml(request: ExportRequest):
    """
    Export transformed data as Eightfold XML file

    Args:
        request: ExportRequest with mappings and source data (or file_id)

    Returns:
        XML file as download

    Raises:
        400: Invalid request
        404: File not found
        500: Error during export
    """
    try:
        import pandas as pd

        # Get source data
        source_data = request.source_data

        if source_data is None and request.file_id:
            storage = get_file_storage()
            df = storage.get_dataframe(request.file_id)

            if df is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": {
                            "code": "FILE_NOT_FOUND",
                            "message": f"File with ID '{request.file_id}' not found",
                        },
                        "status": 404
                    }
                )
        elif source_data is not None:
            df = pd.DataFrame(source_data)
        else:
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

        # Transform to XML
        xml_transformer = get_xml_transformer()
        # Convert Pydantic models to dicts for xml_transformer
        # Try model_dump() first (Pydantic v2), fallback to dict() (Pydantic v1)
        try:
            mappings_dicts = [m.model_dump() if hasattr(m, 'model_dump') else m.dict() for m in request.mappings]
        except Exception:
            mappings_dicts = [dict(m) for m in request.mappings]

        xml_content = xml_transformer.transform_csv_to_xml(
            df=df,
            mappings=mappings_dicts,
            entity_name=request.entity_name
        )

        # Generate filename
        output_filename = request.output_filename.replace('.csv', '.xml') if request.output_filename else 'export.xml'
        if not output_filename.endswith('.xml'):
            output_filename += '.xml'

        # Return as file download
        return StreamingResponse(
            iter([xml_content.encode('utf-8')]),
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "XML_EXPORT_ERROR",
                    "message": f"Error exporting XML: {str(e)}",
                },
                "status": 500
            }
        )

