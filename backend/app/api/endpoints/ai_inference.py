"""
AI Inference API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.services.ai_inference import get_ai_inference_service

router = APIRouter()


class DetectEntityRequest(BaseModel):
    """Request model for entity type detection"""
    source_fields: List[str]


class DetectEntityResponse(BaseModel):
    """Response model for entity type detection"""
    detected_entity: str
    confidence: float
    all_scores: Dict[str, float]


class InferCorrectionsRequest(BaseModel):
    """Request model for field correction inference"""
    source_field: str
    entity_name: str


class ValidateSchemaRequest(BaseModel):
    """Request model for schema validation"""
    source_fields: List[str]
    entity_name: str


@router.post("/detect-entity", response_model=DetectEntityResponse)
async def detect_entity_type(request: DetectEntityRequest):
    """
    Detect the most likely entity type from source field names

    Uses AI to analyze field names and determine which Eightfold entity
    type the uploaded file most likely represents.

    Args:
        request: DetectEntityRequest with source field names

    Returns:
        DetectEntityResponse with detected entity and confidence

    Raises:
        400: Invalid request (empty source fields)
        500: Error during detection
    """
    if not request.source_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "source_fields cannot be empty",
                },
                "status": 400
            }
        )

    try:
        ai_service = get_ai_inference_service()
        entity_name, confidence = ai_service.detect_entity_type(request.source_fields)

        # Get scores for all entities for transparency
        from app.services.schema_manager import get_schema_manager
        schema_manager = get_schema_manager()
        entities = schema_manager.get_available_entities()

        all_scores = {}
        for entity in entities:
            if schema_manager.entity_exists(entity["id"]):
                try:
                    schema = schema_manager.get_schema(entity["id"])
                    target_fields = [f.name for f in schema.fields]
                    normalized_source = [ai_service._normalize_field(f) for f in request.source_fields]
                    normalized_target = [ai_service._normalize_field(f) for f in target_fields]
                    score = ai_service._calculate_entity_match_score(
                        normalized_source,
                        normalized_target,
                        entity["id"]
                    )
                    all_scores[entity["id"]] = round(score, 3)
                except:
                    continue

        return DetectEntityResponse(
            detected_entity=entity_name,
            confidence=round(confidence, 3),
            all_scores=all_scores
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "DETECTION_ERROR",
                    "message": f"Error detecting entity type: {str(e)}",
                },
                "status": 500
            }
        )


@router.post("/infer-corrections")
async def infer_field_corrections(request: InferCorrectionsRequest):
    """
    Suggest corrections for a source field that might be misnamed

    Uses AI to suggest which target field a source field should map to,
    even if the names don't match exactly.

    Args:
        request: InferCorrectionsRequest with source field and entity

    Returns:
        List of suggested corrections with confidence scores

    Raises:
        400: Invalid request
        404: Entity schema not found
        500: Error during inference
    """
    if not request.source_field or not request.entity_name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "source_field and entity_name are required",
                },
                "status": 400
            }
        )

    try:
        ai_service = get_ai_inference_service()
        suggestions = ai_service.infer_field_corrections(
            request.source_field,
            request.entity_name
        )

        return {
            "source_field": request.source_field,
            "entity_name": request.entity_name,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SCHEMA_NOT_FOUND",
                    "message": f"Schema for entity '{request.entity_name}' not found",
                },
                "status": 404
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INFERENCE_ERROR",
                    "message": f"Error inferring corrections: {str(e)}",
                },
                "status": 500
            }
        )


@router.post("/validate-schema")
async def validate_and_suggest(request: ValidateSchemaRequest):
    """
    Validate source fields against target schema and suggest fixes

    Analyzes the uploaded fields against the target schema and provides:
    - Missing required fields
    - Suggested mappings for missing fields
    - Overall validation status

    Args:
        request: ValidateSchemaRequest with source fields and entity

    Returns:
        Validation results with suggestions

    Raises:
        400: Invalid request
        404: Entity schema not found
        500: Error during validation
    """
    if not request.source_fields or not request.entity_name:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "source_fields and entity_name are required",
                },
                "status": 400
            }
        )

    try:
        ai_service = get_ai_inference_service()
        validation = ai_service.validate_and_suggest_fixes(
            request.source_fields,
            request.entity_name
        )

        return {
            "entity_name": request.entity_name,
            "validation": validation
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SCHEMA_NOT_FOUND",
                    "message": f"Schema for entity '{request.entity_name}' not found",
                },
                "status": 404
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Error validating schema: {str(e)}",
                },
                "status": 500
            }
        )
