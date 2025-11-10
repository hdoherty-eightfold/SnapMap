"""
Upload models
"""

from typing import List, Dict, Any, Optional
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
    # Enhanced fields
    detected_delimiter: Optional[str] = Field(None, description="Auto-detected delimiter for CSV files")
    detected_encoding: Optional[str] = Field(None, description="Auto-detected character encoding")
    source_fields: List[str] = Field(..., description="Auto-extracted source field names")
    preview: List[Dict[str, Any]] = Field(..., description="Preview of first 5 rows")


class FileFormatResponse(BaseModel):
    """Response from file format detection"""
    delimiter: Optional[str] = Field(None, description="Detected delimiter for CSV files")
    encoding: str = Field(..., description="Detected character encoding")
    has_header: bool = Field(..., description="Whether file has header row")
    row_count: int = Field(..., description="Number of rows in file")
    field_count: int = Field(..., description="Number of fields/columns")
    preview_fields: List[str] = Field(..., description="Preview of field names")
    special_characters_detected: List[str] = Field(default_factory=list, description="Special/non-ASCII characters found")
    multi_value_fields: List[str] = Field(default_factory=list, description="Fields containing multi-value separators (||)")
    suggested_entity: Optional[str] = Field(None, description="AI-suggested entity type based on field names")
