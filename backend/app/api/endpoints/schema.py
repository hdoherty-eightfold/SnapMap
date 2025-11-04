"""
Schema API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List

from app.models.schema import EntitySchema
from app.services.schema_manager import get_schema_manager

router = APIRouter()


@router.get("/schema/{entity_name}", response_model=EntitySchema)
async def get_entity_schema(entity_name: str):
    """
    Get schema for an entity

    Args:
        entity_name: Entity name (e.g., "employee")

    Returns:
        Entity schema with field definitions

    Raises:
        404: Entity schema not found
        500: Error loading schema
    """
    try:
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema(entity_name)
        return schema
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SCHEMA_NOT_FOUND",
                    "message": f"Schema for entity '{entity_name}' not found",
                },
                "status": 404
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SCHEMA_LOAD_ERROR",
                    "message": f"Error loading schema: {str(e)}",
                },
                "status": 500
            }
        )


@router.get("/validation-rules/{entity_name}")
async def get_validation_rules(entity_name: str) -> Dict[str, dict]:
    """
    Get validation rules for an entity

    Args:
        entity_name: Entity name (e.g., "employee")

    Returns:
        Dictionary mapping field names to validation rules

    Raises:
        404: Entity schema not found
        500: Error loading rules
    """
    try:
        schema_manager = get_schema_manager()
        rules = schema_manager.get_validation_rules(entity_name)
        return {
            "entity_name": entity_name,
            "rules": rules
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SCHEMA_NOT_FOUND",
                    "message": f"Schema for entity '{entity_name}' not found",
                },
                "status": 404
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "VALIDATION_RULES_ERROR",
                    "message": f"Error loading validation rules: {str(e)}",
                },
                "status": 500
            }
        )


@router.get("/entities")
async def get_available_entities():
    """
    Get list of all available entity types

    Returns:
        Dictionary with list of available entities

    Raises:
        500: Error loading entities
    """
    try:
        schema_manager = get_schema_manager()
        entities = schema_manager.get_available_entities()
        return {
            "entities": entities,
            "count": len(entities)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "ENTITY_LIST_ERROR",
                    "message": f"Error loading entities: {str(e)}",
                },
                "status": 500
            }
        )
