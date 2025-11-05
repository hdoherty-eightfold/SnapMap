"""
Transformation models
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.models.mapping import Mapping


class PreviewRequest(BaseModel):
    """Request for transformation preview"""
    mappings: List[Mapping] = Field(..., description="Field mappings")
    source_data: Optional[List[Dict[str, Any]]] = Field(None, description="Source data rows (optional if file_id provided)")
    file_id: Optional[str] = Field(None, description="File ID from upload (alternative to source_data)")
    sample_size: Optional[int] = Field(5, description="Number of rows to preview")
    entity_name: Optional[str] = Field("employee", description="Entity type to transform to")


class PreviewResponse(BaseModel):
    """Response from transformation preview"""
    transformed_data: List[Dict[str, Any]] = Field(..., description="Transformed data rows")
    transformations_applied: List[str] = Field(..., description="List of transformations")
    row_count: int = Field(..., description="Number of rows transformed")
    warnings: List[str] = Field(default_factory=list, description="Warnings")


class ExportRequest(BaseModel):
    """Request for CSV export"""
    mappings: List[Mapping] = Field(..., description="Field mappings")
    source_data: Optional[List[Dict[str, Any]]] = Field(None, description="All source data (optional if file_id provided)")
    file_id: Optional[str] = Field(None, description="File ID from upload (alternative to source_data)")
    output_filename: Optional[str] = Field("EMPLOYEE-MAIN.csv", description="Output filename")
    entity_name: Optional[str] = Field("employee", description="Entity type to transform to")
