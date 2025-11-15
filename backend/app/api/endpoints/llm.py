"""
LLM Management Endpoints
Handles LLM configuration, API key testing, and provider management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import httpx
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


class TestKeyRequest(BaseModel):
    """Test API key request model"""
    provider: str
    api_key: str
    model: Optional[str] = None


class TestKeyResponse(BaseModel):
    """Test API key response model"""
    valid: bool
    provider: str
    model_tested: Optional[str] = None
    error: Optional[str] = None


@router.post("/api/llm/test-key", response_model=TestKeyResponse)
async def test_llm_key(request: TestKeyRequest):
    """Test LLM API key validity"""
    try:
        if request.provider == 'google':
            return await test_google_key(request.api_key, request.model)
        elif request.provider == 'openai':
            return await test_openai_key(request.api_key, request.model)
        elif request.provider == 'anthropic':
            return await test_anthropic_key(request.api_key, request.model)
        elif request.provider == 'grok':
            return await test_grok_key(request.api_key, request.model)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing {request.provider} API key: {e}")
        return TestKeyResponse(
            valid=False,
            provider=request.provider,
            model_tested=request.model,
            error=f"Test failed: {str(e)}"
        )


async def test_google_key(api_key: str, model: Optional[str] = None) -> TestKeyResponse:
    """Test Google Gemini API key"""
    model_to_test = model or 'gemini-2.0-flash-exp'

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_to_test}:generateContent"
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{
                "parts": [{"text": "Say 'API key test successful'"}]
            }]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{url}?key={api_key}",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data:
                    return TestKeyResponse(
                        valid=True,
                        provider='google',
                        model_tested=model_to_test
                    )

            # Try to get error message from response
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            except:
                error_msg = f"HTTP {response.status_code}"

            return TestKeyResponse(
                valid=False,
                provider='google',
                model_tested=model_to_test,
                error=error_msg
            )

    except httpx.TimeoutException:
        return TestKeyResponse(
            valid=False,
            provider='google',
            model_tested=model_to_test,
            error="Request timeout"
        )
    except Exception as e:
        return TestKeyResponse(
            valid=False,
            provider='google',
            model_tested=model_to_test,
            error=str(e)
        )


async def test_openai_key(api_key: str, model: Optional[str] = None) -> TestKeyResponse:
    """Test OpenAI API key"""
    model_to_test = model or 'gpt-3.5-turbo'

    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_to_test,
            "messages": [{"role": "user", "content": "Say 'API key test successful'"}],
            "max_tokens": 10
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return TestKeyResponse(
                    valid=True,
                    provider='openai',
                    model_tested=model_to_test
                )

            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            except:
                error_msg = f"HTTP {response.status_code}"

            return TestKeyResponse(
                valid=False,
                provider='openai',
                model_tested=model_to_test,
                error=error_msg
            )

    except Exception as e:
        return TestKeyResponse(
            valid=False,
            provider='openai',
            model_tested=model_to_test,
            error=str(e)
        )


async def test_anthropic_key(api_key: str, model: Optional[str] = None) -> TestKeyResponse:
    """Test Anthropic Claude API key"""
    model_to_test = model or 'claude-3-haiku-20240307'

    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": model_to_test,
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Say 'API key test successful'"}]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return TestKeyResponse(
                    valid=True,
                    provider='anthropic',
                    model_tested=model_to_test
                )

            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            except:
                error_msg = f"HTTP {response.status_code}"

            return TestKeyResponse(
                valid=False,
                provider='anthropic',
                model_tested=model_to_test,
                error=error_msg
            )

    except Exception as e:
        return TestKeyResponse(
            valid=False,
            provider='anthropic',
            model_tested=model_to_test,
            error=str(e)
        )


async def test_grok_key(api_key: str, model: Optional[str] = None) -> TestKeyResponse:
    """Test Grok API key"""
    model_to_test = model or 'grok-beta'

    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_to_test,
            "messages": [{"role": "user", "content": "Say 'API key test successful'"}],
            "max_tokens": 10
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return TestKeyResponse(
                    valid=True,
                    provider='grok',
                    model_tested=model_to_test
                )

            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            except:
                error_msg = f"HTTP {response.status_code}"

            return TestKeyResponse(
                valid=False,
                provider='grok',
                model_tested=model_to_test,
                error=error_msg
            )

    except Exception as e:
        return TestKeyResponse(
            valid=False,
            provider='grok',
            model_tested=model_to_test,
            error=str(e)
        )


@router.get("/api/llm/providers")
async def get_providers():
    """Get available LLM providers and their models"""
    return {
        "providers": {
            "google": {
                "name": "Google Gemini",
                "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                "icon": "✨",
                "free": True,
                "recommended": True
            },
            "grok": {
                "name": "Grok (xAI)",
                "models": ["grok-beta"],
                "icon": "🚀",
                "free": True
            },
            "openai": {
                "name": "OpenAI",
                "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                "icon": "🤖",
                "premium": True
            },
            "anthropic": {
                "name": "Anthropic",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                "icon": "🧠",
                "premium": True
            }
        }
    }


# Health check endpoint
@router.get("/api/llm/health")
async def llm_health_check():
    """Health check for LLM service"""
    return {
        "status": "healthy",
        "service": "llm-management",
        "timestamp": "2023-12-15T10:00:00Z"
    }