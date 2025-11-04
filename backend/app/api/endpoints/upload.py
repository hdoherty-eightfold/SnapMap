"""
Upload API endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.upload import UploadResponse
from app.services.file_parser import get_file_parser
from app.services.file_storage import get_file_storage

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and parse CSV or Excel file

    Args:
        file: Uploaded file (CSV or Excel)

    Returns:
        UploadResponse with file metadata and sample data

    Raises:
        400: Invalid file format
        413: File too large
        500: Error parsing file
    """
    # Check file size (100 MB limit)
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

    # Read file content
    try:
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds 100 MB limit",
                    },
                    "status": 413
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "FILE_READ_ERROR",
                    "message": f"Error reading file: {str(e)}",
                },
                "status": 500
            }
        )

    # Parse file
    try:
        parser = get_file_parser()
        df = parser.parse_file(content, file.filename)

        # Get basic info
        row_count = len(df)
        column_count = len(df.columns)
        columns = df.columns.tolist()

        # Get sample data (first 10 rows)
        sample_data = df.head(10).to_dict('records')

        # Detect data types
        data_types = parser.detect_column_types(df)

        # Store full DataFrame for later retrieval
        storage = get_file_storage()
        file_id = storage.store_dataframe(df, file.filename)

        return UploadResponse(
            filename=file.filename,
            file_id=file_id,
            row_count=row_count,
            column_count=column_count,
            columns=columns,
            sample_data=sample_data,
            data_types=data_types,
            file_size=file_size
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE_FORMAT",
                    "message": str(e),
                    "details": {
                        "supported_formats": [".csv", ".xlsx", ".xls"]
                    }
                },
                "status": 400
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "PARSE_ERROR",
                    "message": f"Error parsing file: {str(e)}",
                },
                "status": 500
            }
        )
