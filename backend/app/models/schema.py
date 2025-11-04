"""
Schema models for Eightfold entities
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


DataType = Literal["string", "number", "date", "email", "datetime", "boolean"]


class FieldDefinition(BaseModel):
    """Definition of a single field in an entity schema"""
    name: str = Field(..., description="Field name (UPPERCASE)")
    display_name: str = Field(..., description="Human-readable field name")
    type: DataType = Field(..., description="Data type")
    required: bool = Field(..., description="Whether field is required")
    max_length: Optional[int] = Field(None, description="Maximum length for string fields")
    min_length: Optional[int] = Field(None, description="Minimum length")
    pattern: Optional[str] = Field(None, description="Regex validation pattern")
    format: Optional[str] = Field(None, description="Format string (for dates/datetimes)")
    example: str = Field(..., description="Example value")
    description: str = Field(..., description="Field description")
    default_value: Optional[str] = Field(None, description="Default value if not mapped")


class EntitySchema(BaseModel):
    """Complete schema for an entity"""
    entity_name: str = Field(..., description="Entity name (lowercase)")
    display_name: str = Field(..., description="Human-readable entity name")
    description: str = Field(..., description="Entity description")
    fields: List[FieldDefinition] = Field(..., description="List of field definitions")

    def get_required_fields(self) -> List[FieldDefinition]:
        """Get all required fields"""
        return [f for f in self.fields if f.required]

    def get_optional_fields(self) -> List[FieldDefinition]:
        """Get all optional fields"""
        return [f for f in self.fields if not f.required]

    def get_field_by_name(self, name: str) -> Optional[FieldDefinition]:
        """Get field definition by name"""
        for field in self.fields:
            if field.name == name:
                return field
        return None
