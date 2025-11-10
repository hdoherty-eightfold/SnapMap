"""
Upload API endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.upload import UploadResponse, FileFormatResponse
from app.services.file_parser import get_file_parser
from app.services.file_storage import get_file_storage
from app.services.data_validator import get_data_validator

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
        df, parse_metadata = parser.parse_file(content, file.filename)

        # Validate no data loss during parsing
        validator = get_data_validator()

        # Check for multi-value fields (Siemens format with ||)
        multi_value_info = validator.validate_multi_value_fields(
            df,
            multi_value_fields=df.columns.tolist(),
            separator="||"
        )

        # Get basic info
        row_count = len(df)
        column_count = len(df.columns)
        columns = df.columns.tolist()

        # Get sample data (first 5 rows for preview)
        sample_data = df.head(5).to_dict('records')

        # Detect data types
        data_types = parser.detect_column_types(df)

        # Add multi-value field detection to metadata
        if multi_value_info["has_multi_value_fields"]:
            parse_metadata["multi_value_fields"] = multi_value_info["fields_analyzed"]

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
            file_size=file_size,
            detected_delimiter=parse_metadata.get("detected_delimiter"),
            detected_encoding=parse_metadata.get("detected_encoding"),
            source_fields=columns,
            preview=sample_data
        )

    except ValueError as e:
        error_message = str(e)
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE_FORMAT",
                    "message": error_message,
                    "details": {
                        "supported_formats": [".csv", ".xlsx", ".xls"],
                        "suggestion": "Please check the file format and encoding. For CSV files, ensure the correct delimiter is used."
                    }
                },
                "status": 400
            }
        )
    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "PARSE_ERROR",
                    "message": f"Unable to parse file '{file.filename}'. {error_message}",
                    "suggestion": "Verify the file is not corrupted and matches one of the supported formats (CSV, Excel)."
                },
                "status": 500
            }
        )


@router.post("/detect-file-format", response_model=FileFormatResponse)
async def detect_file_format(file: UploadFile = File(...)):
    """
    Detect file format details without full parsing

    This endpoint analyzes a file to detect:
    - Delimiter (for CSV files)
    - Character encoding
    - Field names and count
    - Row count
    - Special characters
    - Multi-value fields (containing ||)
    - Suggested entity type

    Args:
        file: Uploaded file (CSV or Excel)

    Returns:
        FileFormatResponse with detected format details

    Raises:
        400: Invalid file format
        500: Error detecting format
    """
    # Read file content
    try:
        content = await file.read()
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

    # Detect format
    try:
        parser = get_file_parser()
        format_info = parser.detect_file_format(content, file.filename)

        return FileFormatResponse(**format_info)

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
                    "code": "FORMAT_DETECTION_ERROR",
                    "message": f"Error detecting file format: {str(e)}",
                },
                "status": 500
            }
        )
