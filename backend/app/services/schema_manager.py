"""
Schema Manager
Handles loading and managing entity schemas for all Eightfold entity types
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from functools import lru_cache

from app.models.schema import EntitySchema, FieldDefinition


class SchemaManager:
    """Manages entity schemas for all Eightfold entity types"""

    def __init__(self):
        self.schemas_dir = Path(__file__).parent.parent.parent.parent / "docs" / "schemas" / "backend_schemas"
        self._entity_registry = None

    @lru_cache(maxsize=10)
    def get_schema(self, entity_name: str) -> EntitySchema:
        """
        Get schema for an entity

        Args:
            entity_name: Name of the entity (e.g., "employee")

        Returns:
            EntitySchema object

        Raises:
            FileNotFoundError: If schema file doesn't exist
            ValueError: If schema JSON is invalid
        """
        schema_file = self.schemas_dir / f"{entity_name}_schema.json"

        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")

        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)

            return EntitySchema(**schema_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading schema: {e}")

    def get_validation_rules(self, entity_name: str) -> Dict[str, dict]:
        """
        Get validation rules for an entity

        Returns dictionary mapping field names to validation rules
        """
        schema = self.get_schema(entity_name)

        rules = {}
        for field in schema.fields:
            rule = {
                "required": field.required,
                "type": field.type,
            }

            if field.pattern:
                rule["pattern"] = field.pattern
            if field.min_length is not None:
                rule["min_length"] = field.min_length
            if field.max_length is not None:
                rule["max_length"] = field.max_length
            if field.format:
                rule["format"] = field.format

            rules[field.name] = rule

        return rules

    def get_required_field_names(self, entity_name: str) -> list:
        """Get list of required field names"""
        schema = self.get_schema(entity_name)
        return [f.name for f in schema.get_required_fields()]

    def get_optional_field_names(self, entity_name: str) -> list:
        """Get list of optional field names"""
        schema = self.get_schema(entity_name)
        return [f.name for f in schema.get_optional_fields()]

    @property
    def entity_registry(self) -> Dict:
        """Get entity registry with available entity types"""
        if self._entity_registry is None:
            registry_file = self.schemas_dir / "entity_registry.json"
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    self._entity_registry = json.load(f)
            else:
                # Return default registry if file doesn't exist
                self._entity_registry = {"entities": []}
        return self._entity_registry

    def get_available_entities(self) -> List[Dict]:
        """
        Get list of all available entity types

        Returns:
            List of entity metadata dictionaries
        """
        return self.entity_registry.get("entities", [])

    def entity_exists(self, entity_name: str) -> bool:
        """
        Check if an entity schema exists

        Args:
            entity_name: Name of the entity (e.g., "employee", "user")

        Returns:
            True if schema file exists, False otherwise
        """
        schema_file = self.schemas_dir / f"{entity_name}_schema.json"
        return schema_file.exists()


# Singleton instance
_schema_manager = None


def get_schema_manager() -> SchemaManager:
    """Get singleton SchemaManager instance"""
    global _schema_manager
    if _schema_manager is None:
        _schema_manager = SchemaManager()
    return _schema_manager
