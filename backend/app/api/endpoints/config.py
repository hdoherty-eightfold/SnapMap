"""
Configuration API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.config import (
    get_settings,
    update_setting,
    get_vector_db_options,
    get_ai_provider_options
)

router = APIRouter()


class UpdateConfigRequest(BaseModel):
    """Request model for updating configuration"""
    key: str
    value: str


class ConfigResponse(BaseModel):
    """Response model for configuration"""
    success: bool
    message: str


@router.get("/config")
async def get_configuration():
    """
    Get current configuration settings

    Returns all non-sensitive configuration values
    """
    settings = get_settings()

    return {
        "vector_db": {
            "type": settings.vector_db_type,
            "options": get_vector_db_options()
        },
        "ai_inference": {
            "enabled": settings.ai_inference_enabled,
            "provider": settings.ai_inference_provider,
            "options": get_ai_provider_options()
        },
        "api_keys": {
            "gemini_configured": bool(settings.gemini_api_key),
            "openai_configured": bool(settings.openai_api_key),
            "pinecone_configured": bool(settings.pinecone_api_key)
        },
        "application": {
            "max_file_size_mb": settings.max_file_size_mb,
            "debug_mode": settings.debug_mode
        }
    }


@router.post("/config/api-key", response_model=ConfigResponse)
async def update_api_key(request: UpdateConfigRequest):
    """
    Update API key configuration

    Args:
        request: UpdateConfigRequest with key and value

    Returns:
        ConfigResponse with success status
    """
    allowed_keys = [
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "WEAVIATE_API_KEY",
        "QDRANT_API_KEY"
    ]

    if request.key not in allowed_keys:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_KEY",
                    "message": f"Invalid configuration key: {request.key}",
                    "details": {
                        "allowed_keys": allowed_keys
                    }
                },
                "status": 400
            }
        )

    success = update_setting(request.key, request.value)

    if success:
        return ConfigResponse(
            success=True,
            message=f"Successfully updated {request.key}"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "UPDATE_FAILED",
                    "message": "Failed to update configuration"
                },
                "status": 500
            }
        )


@router.post("/config/vector-db", response_model=ConfigResponse)
async def update_vector_db(request: UpdateConfigRequest):
    """
    Update vector database configuration

    Args:
        request: UpdateConfigRequest with vector DB type

    Returns:
        ConfigResponse with success status
    """
    valid_types = ["chromadb", "pinecone", "weaviate", "qdrant", "local"]

    if request.value not in valid_types:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_TYPE",
                    "message": f"Invalid vector DB type: {request.value}",
                    "details": {
                        "valid_types": valid_types
                    }
                },
                "status": 400
            }
        )

    success = update_setting("VECTOR_DB_TYPE", request.value)

    if success:
        return ConfigResponse(
            success=True,
            message=f"Successfully updated vector database to {request.value}"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "UPDATE_FAILED",
                    "message": "Failed to update vector database configuration"
                },
                "status": 500
            }
        )


@router.post("/config/ai-provider", response_model=ConfigResponse)
async def update_ai_provider(request: UpdateConfigRequest):
    """
    Update AI inference provider

    Args:
        request: UpdateConfigRequest with AI provider type

    Returns:
        ConfigResponse with success status
    """
    valid_providers = ["gemini", "openai", "anthropic", "local"]

    if request.value not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_PROVIDER",
                    "message": f"Invalid AI provider: {request.value}",
                    "details": {
                        "valid_providers": valid_providers
                    }
                },
                "status": 400
            }
        )

    success = update_setting("AI_INFERENCE_PROVIDER", request.value)

    if success:
        return ConfigResponse(
            success=True,
            message=f"Successfully updated AI provider to {request.value}"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "UPDATE_FAILED",
                    "message": "Failed to update AI provider configuration"
                },
                "status": 500
            }
        )


@router.get("/config/test-api-key")
async def test_api_key(provider: str):
    """
    Test if an API key is valid

    Args:
        provider: API provider to test (gemini, openai, etc.)

    Returns:
        Test result with status
    """
    settings = get_settings()

    if provider == "gemini":
        if not settings.gemini_api_key:
            return {"valid": False, "message": "API key not configured"}

        try:
            from app.services.gemini_service import test_gemini_connection
            result = await test_gemini_connection(settings.gemini_api_key)
            return {"valid": result, "message": "API key is valid" if result else "API key is invalid"}
        except Exception as e:
            return {"valid": False, "message": str(e)}

    elif provider == "openai":
        if not settings.openai_api_key:
            return {"valid": False, "message": "API key not configured"}
        # Add OpenAI test logic here
        return {"valid": False, "message": "OpenAI testing not implemented yet"}

    else:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_PROVIDER",
                    "message": f"Unknown provider: {provider}"
                },
                "status": 400
            }
        )
