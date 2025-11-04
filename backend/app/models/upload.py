"""
Upload models
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response from file upload"""
    filename: str = Field(..., description="Uploaded filename")
    file_id: str = Field(..., description="Unique file identifier for retrieving full data")
    row_count: int = Field(..., description="Number of rows in file")
    column_count: int = Field(..., description="Number of columns")
    columns: List[str] = Field(..., description="Column names")
    sample_data: List[Dict[str, Any]] = Field(..., description="Sample rows (first 10)")
    data_types: Dict[str, str] = Field(..., description="Detected data types for each column")
    file_size: int = Field(..., description="File size in bytes")
