"""
Validation models
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

from app.models.mapping import Mapping


Severity = Literal["error", "warning", "info"]


class ValidationMessage(BaseModel):
    """Single validation message"""
    field: str = Field(..., description="Field name")
    message: str = Field(..., description="Validation message")
    severity: Severity = Field(..., description="Message severity")
    row_number: Optional[int] = Field(None, description="Row number if applicable")
    suggestion: Optional[str] = Field(None, description="Suggestion to fix")


class ValidationSummary(BaseModel):
    """Validation summary statistics"""
    total_errors: int = Field(..., description="Number of errors")
    total_warnings: int = Field(..., description="Number of warnings")
    required_fields_mapped: int = Field(..., description="Required fields that are mapped")
    required_fields_total: int = Field(..., description="Total required fields")
    mapping_completeness: float = Field(..., description="Percentage of required fields mapped")


class ValidationRequest(BaseModel):
    """Request for validation"""
    mappings: List[Mapping] = Field(..., description="Field mappings to validate")
    source_data: Optional[List[Dict[str, Any]]] = Field(None, description="Source data to validate")
    schema_name: Optional[str] = Field("employee", description="Schema name")


class ValidationResult(BaseModel):
    """Complete validation result"""
    is_valid: bool = Field(..., description="Whether data is valid")
    errors: List[ValidationMessage] = Field(default_factory=list, description="Error messages")
    warnings: List[ValidationMessage] = Field(default_factory=list, description="Warning messages")
    info: List[ValidationMessage] = Field(default_factory=list, description="Info messages")
    summary: ValidationSummary = Field(..., description="Validation summary")
