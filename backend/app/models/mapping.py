"""
Mapping models for field auto-mapping
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


MatchMethod = Literal["exact", "alias", "fuzzy", "manual"]


class Alternative(BaseModel):
    """Alternative field mapping suggestion"""
    target: str = Field(..., description="Target field name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")


class Mapping(BaseModel):
    """Field mapping from source to target"""
    source: str = Field(..., description="Source field name")
    target: str = Field(..., description="Target field name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    method: MatchMethod = Field(..., description="Matching method used")
    alternatives: Optional[List[Alternative]] = Field(None, description="Alternative mappings")


class AutoMapRequest(BaseModel):
    """Request for auto-mapping"""
    source_fields: List[str] = Field(..., description="List of source field names")
    target_schema: Optional[str] = Field("employee", description="Target schema name")
    min_confidence: Optional[float] = Field(0.70, ge=0.0, le=1.0, description="Minimum confidence threshold")


class AutoMapResponse(BaseModel):
    """Response from auto-mapping"""
    mappings: List[Mapping] = Field(..., description="List of mappings")
    total_mapped: int = Field(..., description="Number of fields mapped")
    total_source: int = Field(..., description="Total source fields")
    total_target: int = Field(..., description="Total target fields")
    mapping_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage mapped")
    unmapped_source: List[str] = Field(..., description="Source fields not mapped")
    unmapped_target: List[str] = Field(..., description="Target fields not mapped")
