"""
Proficiency Assessment Endpoints
Handles LLM-based proficiency assessment with configurable levels and prompts
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import logging
import asyncio
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.database import ProficiencyBatch
from app.services.llm_service import LLMService
# from app.services.langchain_service import LangChainService  # Temporarily disabled due to import issues
from app.utils.json_parser import parse_llm_response
from app.utils.chunking import (
    calculate_chunk_size,
    create_chunks,
    get_missing_skills,
    merge_assessment_results
)
from app.utils.retry import (
    RetryConfig,
    retry_with_fallback,
    ProgressTracker,
    AssessmentAttempt,
    InsufficientBalanceError,
    RateLimitError
)

logger = logging.getLogger(__name__)

router = APIRouter()


class ProficiencyLevel(BaseModel):
    """Proficiency level configuration"""
    level: int
    name: str
    description: str
    color: Optional[str] = None  # Optional - only used for UI display


class LLMConfig(BaseModel):
    """LLM configuration for assessment"""
    provider: str = Field(..., description="LLM provider (openai, anthropic, google, grok, huggingface, deepseek, ollama, openrouter)")
    model: str = Field(..., description="Model name")
    api_key: str = Field(..., description="API key for the provider")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(2000, ge=100, le=128000, description="Maximum tokens to generate (128K for Ollama models)")


class SkillAssessment(BaseModel):
    """Individual skill assessment result"""
    skill_name: str
    proficiency_numeric: int
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = []
    reasoning: str
    years_experience: Optional[float] = None


class AssessmentRequest(BaseModel):
    """Proficiency assessment request"""
    skills: List[Dict[str, Any]] = Field(..., description="Skills to assess")
    proficiency_levels: List[ProficiencyLevel] = Field(..., description="Proficiency level definitions")
    llm_config: LLMConfig = Field(..., description="LLM configuration")
    prompt_template: str = Field(..., description="Assessment prompt template")


class TestLLMRequest(BaseModel):
    """Test LLM connection request"""
    provider: str
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2000


class TestAssessmentRequest(BaseModel):
    """Test assessment request"""
    skills: List[Dict[str, Any]]
    proficiency_levels: List[ProficiencyLevel]
    llm_config: LLMConfig
    prompt_template: str
    sample_text: str
    context: Optional[str] = None


class AssessmentResponse(BaseModel):
    """Assessment response"""
    assessments: List[SkillAssessment]
    total_skills: int
    processing_time_seconds: float
    llm_provider: str
    llm_model: str
    prompt_used: str
    llm_response: str  # FULL LLM response for debugging
    assessment_id: str
    timestamp: str


class ChunkConfig(BaseModel):
    """Chunking configuration"""
    enabled: bool = True
    size: Union[int, str] = "auto"  # Number of skills per chunk or "auto"
    strategy: str = Field("adaptive", description="Chunking strategy: fixed, adaptive, conservative")
    retry_failed: bool = True
    parallel_chunks: int = Field(1, ge=1, le=5, description="Number of chunks to process in parallel")


class RetryConfigModel(BaseModel):
    """Retry configuration model"""
    max_retries: int = Field(3, ge=1, le=10)
    backoff_factor: float = Field(2.0, ge=1.0, le=5.0)
    initial_delay: float = Field(1.0, ge=0.1, le=10.0)
    fallback_models: List[str] = Field(default_factory=list)


class ChunkedAssessmentRequest(BaseModel):
    """Chunked proficiency assessment request"""
    skills: List[Dict[str, Any]] = Field(..., description="Skills to assess")
    proficiency_levels: List[ProficiencyLevel] = Field(..., description="Proficiency level definitions")
    llm_config: LLMConfig = Field(..., description="LLM configuration")
    prompt_template: str = Field(..., description="Assessment prompt template")
    chunk_config: ChunkConfig = Field(default_factory=ChunkConfig)
    retry_config: RetryConfigModel = Field(default_factory=RetryConfigModel)


class ChunkedAssessmentResponse(BaseModel):
    """Chunked assessment response"""
    assessment_id: str
    assessments: List[Dict[str, Any]]
    total_skills: int
    completed_skills: int
    failed_skills: List[Dict[str, Any]]
    total_chunks: int
    chunk_size: int
    processing_time_seconds: float
    llm_provider: str
    llm_model: str
    timestamp: str
    progress: Dict[str, Any]


def create_assessment_prompt(
    skills: List[Dict[str, Any]],
    proficiency_levels: List[ProficiencyLevel],
    template: str
) -> str:
    """Create the assessment prompt from template and data"""

    # Prepare skills list
    skills_text = "\n".join([f"- {skill.get('name', 'Unknown')}" for skill in skills])

    # Prepare proficiency levels
    levels_text = "\n".join([f"- {level.name} ({level.level}): {level.description}"
                            for level in proficiency_levels])

    # Replace template variables using simple string replacement
    # This approach doesn't treat curly braces as special characters
    prompt = template
    prompt = prompt.replace("{skills}", skills_text)
    prompt = prompt.replace("{skills_to_assess}", skills_text)  # Backward compatibility
    prompt = prompt.replace("{proficiency_levels}", levels_text)
    prompt = prompt.replace("{text}", "")  # Backward compatibility
    prompt = prompt.replace("{context}", "")  # Backward compatibility

    return prompt


def _clean_json_response(raw_response: str) -> str:
    """Clean LLM response to extract pure JSON from markdown code blocks - matches skill_prof_gen"""
    if not raw_response:
        return raw_response

    # Remove markdown code blocks (```json ... ``` or ``` ... ```)
    import re

    # Pattern to match ```json ... ``` or ``` ... ```
    code_block_pattern = r'```(?:json)?\s*(.*?)\s*```'
    match = re.search(code_block_pattern, raw_response, re.DOTALL)

    if match:
        cleaned = match.group(1).strip()
        logger.info(f"Extracted JSON from code block, length: {len(cleaned)}")
        return cleaned

    # If no code blocks, return as-is (might already be clean JSON)
    return raw_response.strip()


def _extract_json_from_response(cleaned_response: str):
    """Extract JSON from cleaned response - handles both arrays and objects"""
    import re
    import json

    logger.info(f"Attempting to extract JSON from cleaned response (length: {len(cleaned_response)})")
    logger.info(f"Cleaned response preview (first 500 chars): {cleaned_response[:500]}")
    logger.info(f"Cleaned response preview (last 500 chars): {cleaned_response[-500:]}")

    # Try to extract JSON array first (common LLM response format)
    # Use a smarter approach to find the complete JSON array by tracking bracket depth
    array_start = cleaned_response.find('[')
    if array_start != -1:
        depth = 0
        in_string = False
        escape_next = False

        for i in range(array_start, len(cleaned_response)):
            char = cleaned_response[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if not in_string:
                if char == '[':
                    depth += 1
                elif char == ']':
                    depth -= 1
                    if depth == 0:
                        # Found the matching closing bracket
                        json_str = cleaned_response[array_start:i+1]
                        logger.info(f"Found JSON array, length: {len(json_str)}")
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON parsing failed: {e}")
                            logger.error(f"Failed JSON string (first 1000 chars): {json_str[:1000]}")
                            logger.error(f"Failed JSON string (last 1000 chars): {json_str[-1000:]}")
                            raise

    # Try to extract JSON object
    object_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
    if object_match:
        json_str = object_match.group()
        logger.info(f"Found JSON object, length: {len(json_str)}")
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Failed JSON string (first 1000 chars): {json_str[:1000]}")
            raise

    # Try to parse the entire cleaned response as JSON
    logger.info("No JSON pattern found, trying to parse entire response")
    return json.loads(cleaned_response)


def parse_llm_response(response_text: str, skills: List[Dict[str, Any]]) -> List[SkillAssessment]:
    """Parse LLM response into structured assessments - matches skill_prof_gen"""
    try:
        # Clean the response to extract JSON from markdown code blocks (matches skill_prof_gen)
        cleaned_response = _clean_json_response(response_text)
        logger.info(f"Cleaned response, length: {len(cleaned_response)}")

        # Extract JSON object using regex (matches skill_prof_gen)
        llm_json = _extract_json_from_response(cleaned_response)

        # Handle both list and dict formats (matches skill_prof_gen)
        if isinstance(llm_json, list):
            assessments_list = llm_json
        else:
            assessments_list = llm_json.get('assessments', [])

        assessments = []

        for item in assessments_list:
            skill_name = item.get('skill_name', '')

            # Parse proficiency level - support multiple field names
            # Try: proficiency_level, proficiency_numeric, proficiency (in that order)
            prof_numeric = item.get('proficiency_level', item.get('proficiency_numeric', item.get('proficiency')))

            # If we don't have numeric proficiency, try to derive from level text if present (backward compatibility)
            if prof_numeric is None:
                prof_level = item.get('proficiency_level', item.get('level', ''))
                if prof_level:
                    level_map = {
                        'novice': 1, 'beginner': 1,
                        'developing': 2, 'basic': 2,
                        'intermediate': 3, 'proficient': 3,
                        'advanced': 4, 'expert': 5
                    }
                    prof_numeric = level_map.get(prof_level.lower(), 3)
                else:
                    prof_numeric = 3  # Default to intermediate

            assessment = SkillAssessment(
                skill_name=skill_name,
                proficiency_numeric=int(prof_numeric),
                confidence_score=float(item.get('confidence_score', 0.5)),
                evidence=item.get('evidence', []),
                reasoning=item.get('reasoning', ''),
                years_experience=item.get('years_experience')
            )
            assessments.append(assessment)

        logger.info(f"Successfully parsed {len(assessments)} assessments")
        return assessments

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        logger.error(f"Response (first 1000 chars): {response_text[:1000]}")
        # Re-raise the error - NO FALLBACK DATA
        raise ValueError(f"Invalid JSON in LLM response: {str(e)}. Response preview: {response_text[:500]}")

    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}", exc_info=True)
        logger.error(f"Response text (first 1000 chars): {response_text[:1000]}")
        # Re-raise the error - NO FALLBACK DATA
        raise ValueError(f"Failed to parse LLM response: {str(e)}. Response preview: {response_text[:500]}")


@router.post("/api/proficiency/test-llm")
async def test_llm_connection(request: TestLLMRequest):
    """Test LLM connection and basic functionality"""
    try:
        llm_service = LLMService(
            provider=request.provider,
            api_key=request.api_key,
            model=request.model
        )

        # Simple test prompt - designed to avoid safety filters
        test_prompt = "Please respond with: 'API connection successful'"

        # Test the connection
        response = await llm_service.call_llm_async(
            prompt=test_prompt,
            provider=request.provider,
            model=request.model,
            api_key=request.api_key,
            temperature=request.temperature,
            max_tokens=min(request.max_tokens, 500)  # Limit for test
        )

        if response:
            return {
                "success": True,
                "response": response,
                "provider": request.provider,
                "model": request.model,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="No response from LLM")

    except Exception as e:
        logger.error(f"LLM test error: {e}")
        raise HTTPException(status_code=400, detail=f"LLM test failed: {str(e)}")


@router.post("/api/proficiency/test-assessment")
async def test_assessment(request: TestAssessmentRequest):
    """Run a test assessment with sample data"""
    try:
        # Normalize provider name (accept both 'google' and 'gemini', 'anthropic' and 'claude')
        provider = request.llm_config.provider.lower()
        if provider == "google":
            provider = "gemini"
        elif provider == "anthropic":
            provider = "claude"

        llm_service = LLMService(
            provider=provider,
            api_key=request.llm_config.api_key,
            model=request.llm_config.model
        )
        start_time = datetime.now()

        # Create assessment prompt
        prompt = create_assessment_prompt(
            text=request.sample_text,
            skills=request.skills,
            proficiency_levels=request.proficiency_levels,
            template=request.prompt_template,
            context=request.context
        )

        # Call LLM
        response = await llm_service.call_llm_async(
            prompt=prompt,
            provider=provider,
            model=request.llm_config.model,
            api_key=request.llm_config.api_key,
            temperature=request.llm_config.temperature,
            max_tokens=request.llm_config.max_tokens
        )

        # Parse response
        assessments = parse_llm_response(response, request.skills)

        processing_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "assessments": [assessment.dict() for assessment in assessments],
            "raw_response": response,
            "prompt_used": prompt,
            "processing_time_seconds": processing_time,
            "test_skills_count": len(request.skills),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Test assessment error: {e}")
        raise HTTPException(status_code=400, detail=f"Test assessment failed: {str(e)}")


@router.post("/api/proficiency/assess", response_model=AssessmentResponse)
async def assess_proficiencies(request: AssessmentRequest):
    """Run full proficiency assessment with automatic chunking for large batches"""
    try:
        logger.info(f"Starting assessment for {len(request.skills)} skills")

        # Normalize provider name (accept both 'google' and 'gemini', 'anthropic' and 'claude')
        provider = request.llm_config.provider.lower()
        if provider == "google":
            provider = "gemini"
        elif provider == "anthropic":
            provider = "claude"

        llm_service = LLMService(
            provider=provider,
            api_key=request.llm_config.api_key,
            model=request.llm_config.model
        )
        start_time = datetime.now()

        # Chunking configuration
        # For Gemini, use smaller chunks to avoid truncation (responses are cut off with too many skills)
        # For other providers, larger chunks are fine
        if provider == "gemini":
            chunk_size = 5  # Process 5 skills at a time for Gemini
            logger.info(f"Using Gemini-optimized chunking: {chunk_size} skills per batch")
        else:
            chunk_size = 10  # Other providers can handle more
            logger.info(f"Using standard chunking: {chunk_size} skills per batch")

        # Split skills into chunks
        skill_chunks = [request.skills[i:i + chunk_size] for i in range(0, len(request.skills), chunk_size)]
        logger.info(f"Split {len(request.skills)} skills into {len(skill_chunks)} chunks")

        all_assessments = []
        full_llm_response = ""  # Combine all LLM responses for debugging
        full_prompt = ""  # Store the prompt from first chunk

        # Process each chunk
        for chunk_idx, skill_chunk in enumerate(skill_chunks, 1):
            logger.info(f"Processing chunk {chunk_idx}/{len(skill_chunks)} with {len(skill_chunk)} skills")

            # Create assessment prompt for this chunk
            try:
                logger.info(f"Using prompt template (first 200 chars): {request.prompt_template[:200] if request.prompt_template else 'None'}...")
                prompt = create_assessment_prompt(
                    skills=skill_chunk,
                    proficiency_levels=request.proficiency_levels,
                    template=request.prompt_template
                )
                logger.info(f"Created prompt for chunk {chunk_idx}, length: {len(prompt)} chars")

                # Store first chunk's prompt for response
                if chunk_idx == 1:
                    full_prompt = prompt
            except Exception as e:
                logger.error(f"Prompt creation error: {e}")
                error_detail = {
                    "error": "Template formatting failed BEFORE calling LLM",
                    "message": str(e),
                    "template_preview": request.prompt_template[:500] if request.prompt_template else "None",
                    "hint": "Your prompt template has formatting errors. The LLM was NOT called yet. Fix the template first.",
                    "common_fix": "In JSON examples, use {{ and }} instead of { and }. Example: {{\"skill_name\": \"Python\"}}",
                    "phase": "TEMPLATE_FORMATTING"
                }
                raise HTTPException(status_code=400, detail=error_detail)

            # Call LLM for this chunk
            logger.info(f"Calling LLM for chunk {chunk_idx}: {provider}/{request.llm_config.model}")
            try:
                response = await llm_service.call_llm_async(
                    prompt=prompt,
                    provider=provider,
                    model=request.llm_config.model,
                    api_key=request.llm_config.api_key,
                    temperature=request.llm_config.temperature,
                    max_tokens=request.llm_config.max_tokens
                )
                logger.info(f"LLM response received for chunk {chunk_idx}, length: {len(response)} chars")
                full_llm_response += f"\n\n=== CHUNK {chunk_idx} ===\n{response}"
            except ValueError as e:
                # Handle LLM-specific errors (e.g., Gemini safety filter)
                logger.error(f"LLM call failed for chunk {chunk_idx}: {e}")
                error_msg = str(e)

                # Check if it's a Gemini safety filter error
                if "safety filter" in error_msg.lower():
                    error_detail = {
                        "error": "LLM Safety Filter Triggered",
                        "message": error_msg,
                        "provider": provider,
                        "model": request.llm_config.model,
                        "chunk": f"{chunk_idx}/{len(skill_chunks)}",
                        "hint": "The AI model's safety filter blocked this request. This usually happens with sensitive content.",
                        "solutions": [
                            "Try using a different AI model (OpenAI, Anthropic, or Grok)",
                            "Simplify your prompt template",
                            "If using Gemini, try Gemini Flash instead of Gemini Pro",
                            "Remove JSON examples from the prompt that might trigger filters"
                        ],
                        "phase": "LLM_CALL",
                        "prompt_preview": prompt[:500]  # First 500 chars of prompt for debugging
                    }
                else:
                    error_detail = {
                        "error": "LLM Call Failed",
                        "message": error_msg,
                        "provider": provider,
                        "model": request.llm_config.model,
                        "chunk": f"{chunk_idx}/{len(skill_chunks)}",
                        "phase": "LLM_CALL",
                        "prompt_preview": prompt[:500]
                    }
                raise HTTPException(status_code=500, detail=error_detail)
            except Exception as e:
                # Handle other LLM errors (network, auth, etc.)
                logger.error(f"LLM call failed for chunk {chunk_idx} with unexpected error: {e}", exc_info=True)
                error_detail = {
                    "error": "LLM Call Failed",
                    "message": str(e),
                    "type": type(e).__name__,
                    "provider": provider,
                    "model": request.llm_config.model,
                    "chunk": f"{chunk_idx}/{len(skill_chunks)}",
                    "phase": "LLM_CALL"
                }
                raise HTTPException(status_code=500, detail=error_detail)

            # Parse response for this chunk
            try:
                chunk_assessments = parse_llm_response(response, skill_chunk)
                logger.info(f"Successfully parsed {len(chunk_assessments)} assessments from chunk {chunk_idx}")
                all_assessments.extend(chunk_assessments)
            except Exception as e:
                logger.error(f"Response parsing error for chunk {chunk_idx}: {e}")
                logger.error(f"Raw LLM response: {response[:1000]}...")
                error_detail = {
                    "error": "LLM response parsing failed AFTER calling LLM",
                    "message": str(e),
                    "chunk": f"{chunk_idx}/{len(skill_chunks)}",
                    "llm_response_preview": response,  # FULL response for debugging
                    "llm_response_length": len(response),
                    "hint": "The LLM was called successfully but returned malformed JSON. See the FULL LLM response below.",
                    "common_fix": "The LLM might not be following the prompt format. Try making the prompt more explicit about JSON format.",
                    "phase": "LLM_RESPONSE_PARSING"
                }
                raise HTTPException(status_code=500, detail=error_detail)

        processing_time = (datetime.now() - start_time).total_seconds()

        # Generate assessment ID
        import uuid
        assessment_id = str(uuid.uuid4())

        result = AssessmentResponse(
            assessments=all_assessments,
            total_skills=len(request.skills),
            processing_time_seconds=processing_time,
            llm_provider=request.llm_config.provider,
            llm_model=request.llm_config.model,
            prompt_used=full_prompt,  # Use first chunk's prompt as representative
            llm_response=full_llm_response,  # Include ALL chunk responses for debugging
            assessment_id=assessment_id,
            timestamp=datetime.now().isoformat()
        )

        logger.info(f"Assessment completed successfully: {len(all_assessments)} skills assessed in {processing_time:.2f}s using {len(skill_chunks)} chunks")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assessment error: {e}", exc_info=True)
        error_detail = {
            "error": "Unexpected assessment error",
            "message": str(e),
            "type": type(e).__name__
        }
        raise HTTPException(status_code=500, detail=error_detail)


# @router.post("/api/proficiency/assess-langchain")
# async def assess_proficiencies_langchain(request: AssessmentRequest):
#     """Run proficiency assessment using LangChain for structured output"""
#     # Temporarily disabled due to LangChain import issues
#     raise HTTPException(status_code=501, detail="LangChain integration temporarily unavailable")


@router.post("/api/proficiency/batch-assess")
async def batch_assess_proficiencies(requests: List[AssessmentRequest]):
    """Run batch proficiency assessments"""
    try:
        results = []

        # Process requests concurrently (limit concurrent requests to avoid rate limits)
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests

        async def assess_single(request: AssessmentRequest):
            async with semaphore:
                return await assess_proficiencies(request)

        # Run assessments
        tasks = [assess_single(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separate successful and failed results
        successful = []
        failed = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    "request_index": i,
                    "error": str(result)
                })
            else:
                successful.append(result)

        return {
            "successful_assessments": len(successful),
            "failed_assessments": len(failed),
            "results": successful,
            "errors": failed,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Batch assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch assessment failed: {str(e)}")


@router.get("/api/proficiency/providers")
async def get_available_providers():
    """Get list of available LLM providers and their models"""
    return {
        "providers": [
            {
                "id": "google",
                "name": "Google Gemini",
                "description": "Gemini 2.5, fast and FREE",
                "models": ["gemini-2.5-flash", "gemini-2.5-pro"],
                "free_tier": True,
                "recommended": True
            },
            {
                "id": "huggingface",
                "name": "Hugging Face",
                "description": "800K+ open-source models, FREE tier",
                "models": [
                    "mistralai/Mistral-7B-Instruct-v0.2",
                    "meta-llama/Llama-3-8b-chat-hf",
                    "HuggingFaceH4/zephyr-7b-beta",
                    "tiiuae/falcon-7b-instruct",
                    "google/flan-t5-xxl"
                ],
                "free_tier": True,
                "recommended": True
            },
            {
                "id": "grok",
                "name": "Grok (xAI)",
                "description": "Fast, free tier available",
                "models": ["grok-beta", "grok-2-latest", "grok-vision-beta"],
                "free_tier": True
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "GPT-4, high quality",
                "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                "free_tier": False
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "description": "Claude, excellent reasoning",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                "free_tier": False
            }
        ]
    }


@router.get("/api/proficiency/default-prompt")
async def get_default_prompt_template():
    """Get the default assessment prompt template"""
    template = """Analyze the following text and assess proficiency levels for the listed skills.

Text to analyze:
{text}

{context}

Skills to assess:
{skills}

Proficiency levels:
{proficiency_levels}

For each skill, provide:
1. Numeric proficiency level (1-5)
2. Confidence score (0.0 to 1.0)
3. Brief reasoning for the assessment

Return as JSON array with format:
[
  {{
    "skill_name": "skill name",
    "proficiency_numeric": 1-5,
    "confidence_score": 0.0-1.0,
    "evidence": ["brief evidence 1", "brief evidence 2"],
    "reasoning": "brief explanation",
    "years_experience": estimated years or null
  }}
]

IMPORTANT: Keep responses concise. Return ONLY valid JSON, no extra text."""

    return {
        "template": template,
        "variables": ["text", "context", "skills", "proficiency_levels"],
        "description": "Default proficiency assessment prompt template"
    }


@router.post("/api/proficiency/export-to-eightfold-detailed")
async def export_to_eightfold_detailed(request: dict):
    """
    Export assessment results to Eightfold with detailed per-skill tracking

    Returns detailed status for each skill including:
    - Success/failure status
    - API response data
    - Error messages
    - Warnings

    Request body:
    {
        "assessments": List[Dict],  # Assessment results
        "environment_id": str,      # Eightfold environment ID
        "role_id": str,             # Role ID to update
        "role_title": str,          # Role title (optional)
        "test_mode": bool           # If true, only push first 3 skills for testing
    }
    """
    try:
        assessments = request.get('assessments', [])
        environment_id = request.get('environment_id', 'adoherty_demo')
        role_id = request.get('role_id')
        role_title = request.get('role_title')
        test_mode = request.get('test_mode', False)

        if not assessments:
            raise HTTPException(status_code=400, detail="No assessments provided")

        if not role_id:
            raise HTTPException(
                status_code=400,
                detail="Role ID is required"
            )

        # Use the EightfoldClient
        from app.services.eightfold_client import get_eightfold_client
        client = get_eightfold_client(environment_id)

        # Test mode: only process first 3 skills
        if test_mode:
            assessments = assessments[:3]
            logger.info(f"TEST MODE: Processing only {len(assessments)} skills")

        # Track detailed results
        detailed_results = []
        success_count = 0
        failure_count = 0
        warning_count = 0

        # Push all skills in one batch (Eightfold API accepts batch updates)
        result = await client.push_proficiencies(
            role_id=role_id,
            proficiencies=assessments,
            role_title=role_title
        )

        if result.get('success'):
            # All skills successfully pushed
            for assessment in assessments:
                detailed_results.append({
                    "skill_name": assessment.get('skill_name'),
                    "status": "success",
                    "proficiency_level": assessment.get('proficiency_level') or assessment.get('proficiency_numeric'),
                    "confidence_score": assessment.get('confidence_score'),
                    "message": "Successfully pushed to Eightfold",
                    "api_response": result.get('response', {})
                })
                success_count += 1
        else:
            # Batch push failed - mark all as failed
            error_msg = result.get('error', 'Unknown error')
            for assessment in assessments:
                detailed_results.append({
                    "skill_name": assessment.get('skill_name'),
                    "status": "failed",
                    "proficiency_level": assessment.get('proficiency_level') or assessment.get('proficiency_numeric'),
                    "confidence_score": assessment.get('confidence_score'),
                    "error": error_msg,
                    "message": f"Failed to push: {error_msg}",
                    "tried_endpoints": result.get('tried_endpoints', [])
                })
                failure_count += 1

        return {
            "success": success_count > 0,
            "test_mode": test_mode,
            "total_skills": len(assessments),
            "success_count": success_count,
            "failure_count": failure_count,
            "warning_count": warning_count,
            "environment": environment_id,
            "role_id": role_id,
            "role_title": role_title,
            "results": detailed_results,
            "endpoint_used": result.get('endpoint'),
            "method_used": result.get('method'),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detailed export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/api/proficiency/export-to-eightfold")
async def export_to_eightfold(request: dict):
    """
    Export assessment results to Eightfold platform using role-based skill mapping

    This endpoint implements the workflow from skill_prof_gen:
    1. Receives proficiency map from frontend (skill_name -> proficiency_numeric)
    2. Fetches the original role from Eightfold (or uses role_data from frontend)
    3. Updates role's skillProficiencies array with new proficiency values
    4. Excludes read-only "level" field from update
    5. Sends PUT request to update the role

    Request body:
    {
        "assessments": List[Dict],          # Assessment results (for reference)
        "proficiency_map": Dict[str, int],  # skill_name -> proficiency_numeric (1-5)
        "environment_id": str,              # Eightfold environment ID
        "role_id": str,                     # Role ID to update
        "role_title": str,                  # Role title (optional)
        "role_data": Dict,                  # Original role data from extraction (optional)
        "auth_token": str                   # Auth token from Step 2 (optional)
    }
    """
    try:
        assessments = request.get('assessments', [])
        proficiency_map = request.get('proficiency_map', {})
        environment_id = request.get('environment_id', 'adoherty_demo')
        role_id = request.get('role_id')
        role_title = request.get('role_title')
        role_data = request.get('role_data')  # Original role from Step 2
        auth_token = request.get('auth_token')  # Auth token from Step 2

        if not assessments and not proficiency_map:
            raise HTTPException(status_code=400, detail="No assessments or proficiency map provided")

        if not role_id:
            raise HTTPException(
                status_code=400,
                detail="Role ID is required. Please specify which role to update in Eightfold."
            )

        # Build proficiency map if not provided (backward compatibility)
        if not proficiency_map and assessments:
            proficiency_map = {}
            for assessment in assessments:
                skill_name = assessment.get('skill_name', '')
                proficiency = assessment.get('proficiency_numeric', assessment.get('proficiency_level', 3))
                # Normalize skill name for matching (lowercase, trimmed)
                normalized_name = skill_name.lower().strip()
                proficiency_map[normalized_name] = proficiency
            logger.info(f"Built proficiency map from {len(proficiency_map)} assessments")

        # Get auth token if not provided (auto-authenticate)
        if not auth_token and environment_id in ['adoherty_demo', 'ADOHERTY_DEMO']:
            import httpx
            auth_url = "https://apiv2.eightfold.ai/oauth/v1/authenticate"
            auth_headers = {
                "Authorization": "Basic MU92YTg4T1JyMlFBVktEZG8wc1dycTdEOnBOY1NoMno1RlFBMTZ6V2QwN3cyeUFvc3QwTU05MmZmaXFFRDM4ZzJ4SFVyMGRDaw==",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            auth_data = {
                "grant_type": "password",
                "username": "adoherty_api",
                "password": "JdE1wWX^zJFJ"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                auth_response = await client.post(auth_url, headers=auth_headers, data=auth_data)
                if auth_response.status_code == 200:
                    auth_result = auth_response.json()
                    auth_token = auth_result.get("access_token")
                else:
                    raise HTTPException(status_code=401, detail="Failed to authenticate with Eightfold")

        if not auth_token:
            raise HTTPException(status_code=401, detail="Authentication token required")

        # Get role data if not provided by frontend
        if not role_data:
            logger.info(f"Fetching role data from Eightfold for role_id: {role_id}")
            # Fetch role from Eightfold API
            # This would require implementing a get_role method in EightfoldClient
            # For now, we'll require role_data from frontend
            logger.warning("Role data not provided - using proficiency map only")
            role_data = {
                "id": role_id,
                "title": role_title or role_id,
                "skillProficiencies": []
            }

        # Update role's skillProficiencies with new proficiency values
        updated_skills = []
        skill_proficiencies = role_data.get('skillProficiencies', [])

        logger.info(f"Processing {len(skill_proficiencies)} skills from role")

        # Early return if role has no skills to update
        if len(skill_proficiencies) == 0:
            logger.warning(f"Role {role_id} has no skillProficiencies to update")
            return {
                "success": True,
                "exported_count": 0,
                "assessed_skills": 0,
                "total_skills": 0,
                "skipped_skills": 0,
                "environment": environment_id,
                "role_id": role_id,
                "role_title": role_data.get('title', role_title or role_id),
                "message": "Role has no skillProficiencies to update",
                "reason": "Role has no skillProficiencies array - nothing to update",
                "endpoint_used": f"https://apiv2.eightfold.ai/api/v2/JIE/roles/{role_id}",
                "method_used": "SKIPPED",
                "timestamp": datetime.now().isoformat()
            }

        for skill in skill_proficiencies:
            skill_name = skill.get('name', '')
            normalized_name = skill_name.lower().strip()

            # Check if this skill was assessed
            if normalized_name in proficiency_map:
                # Update proficiency with assessed value
                new_proficiency = proficiency_map[normalized_name]
                updated_skill = {
                    "name": skill_name,  # Use original capitalization
                    "proficiency": new_proficiency,
                    # DO NOT include "level" - it's read-only in Eightfold API
                    "skillGroupList": skill.get('skillGroupList', [])
                }
                updated_skills.append(updated_skill)
                logger.debug(f"Updated skill '{skill_name}' with proficiency {new_proficiency}")
            else:
                # Keep existing proficiency for skills that weren't assessed
                existing_proficiency = skill.get('proficiency')
                if existing_proficiency is not None:
                    updated_skill = {
                        "name": skill_name,
                        "proficiency": existing_proficiency,
                        "skillGroupList": skill.get('skillGroupList', [])
                    }
                    updated_skills.append(updated_skill)
                    logger.debug(f"Kept existing proficiency {existing_proficiency} for skill '{skill_name}'")

        logger.info(f"Built update payload with {len(updated_skills)} skills")

        # Build role update payload (matches skill_prof_gen pattern)
        # Note: archivalStatus expects boolean (true = archived, false = active)
        archival_status_value = role_data.get('archivalStatus')
        is_archived = False  # Default to active (not archived)
        if isinstance(archival_status_value, bool):
            is_archived = archival_status_value
        elif isinstance(archival_status_value, str):
            # Convert string values like 'ARCHIVED' to boolean
            is_archived = archival_status_value.upper() in ['ARCHIVED', 'TRUE', '1']

        role_update_payload = {
            "title": role_data.get('title', role_title or role_id),
            "skillProficiencies": updated_skills,
            "roleDescription": role_data.get('roleDescription', ''),
            "archivalStatus": is_archived
        }

        # Push proficiencies to Eightfold via PUT request
        import httpx
        update_url = f"https://apiv2.eightfold.ai/api/v2/JIE/roles/{role_id}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            update_response = await client.put(update_url, headers=headers, json=role_update_payload)

            if update_response.status_code == 200:
                assessed_count = len([s for s in updated_skills if s['name'].lower().strip() in proficiency_map])
                skipped_count = len(updated_skills) - assessed_count

                logger.info(f"Successfully updated role {role_id} with {len(updated_skills)} skills")
                return {
                    "success": True,
                    "exported_count": len(updated_skills),
                    "assessed_skills": assessed_count,
                    "total_skills": len(updated_skills),
                    "skipped_skills": skipped_count,
                    "environment": environment_id,
                    "role_id": role_id,
                    "role_title": role_update_payload['title'],
                    "message": f"Successfully updated {len(updated_skills)} skills (assessed: {assessed_count})",
                    "reason": f"Updated {assessed_count} assessed skills, kept {skipped_count} existing proficiencies",
                    "endpoint_used": update_url,
                    "method_used": "PUT",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_detail = update_response.text
                logger.error(f"Failed to update role {role_id}: {error_detail}")
                raise HTTPException(
                    status_code=update_response.status_code,
                    detail=f"Failed to update role in Eightfold: {error_detail}"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Eightfold export error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export to Eightfold failed: {str(e)}")


@router.post("/api/proficiency/assess/chunked", response_model=ChunkedAssessmentResponse)
async def assess_proficiencies_chunked(request: ChunkedAssessmentRequest):
    """
    Assess proficiencies with intelligent chunking, retry logic, and fallback models
    This endpoint provides production-ready reliability with:
    - Automatic chunking based on model limits
    - Multi-stage JSON parsing with fallback
    - Retry logic with exponential backoff
    - Automatic model fallback on failure
    - Progress tracking
    """
    import uuid
    from app.utils.json_parser import parse_llm_response
    from app.utils.chunking import calculate_chunk_size, create_chunks, merge_assessment_results
    from app.utils.retry import RetryConfig, ProgressTracker, AssessmentAttempt

    try:
        start_time = datetime.now()
        assessment_id = str(uuid.uuid4())

        # Normalize provider
        provider = request.llm_config.provider.lower()
        if provider == "google":
            provider = "gemini"
        elif provider == "anthropic":
            provider = "claude"

        # Determine output format from prompt template
        output_format = "simple" if "proficiency_level" in request.prompt_template and "evidence" not in request.prompt_template else "detailed"

        # Calculate chunk size
        if request.chunk_config.size == "auto":
            chunk_size = calculate_chunk_size(
                total_skills=len(request.skills),
                model=request.llm_config.model,
                strategy=request.chunk_config.strategy,
                output_format=output_format
            )
        else:
            chunk_size = int(request.chunk_config.size)

        logger.info(f"Chunked assessment: {len(request.skills)} skills, chunk_size={chunk_size}, strategy={request.chunk_config.strategy}")

        # Create chunks
        chunks = create_chunks(request.skills, chunk_size)

        # Initialize progress tracker
        progress = ProgressTracker(
            total_skills=len(request.skills),
            total_chunks=len(chunks),
            assessment_id=assessment_id
        )

        # Initialize retry config
        retry_config = RetryConfig(
            max_retries=request.retry_config.max_retries,
            backoff_factor=request.retry_config.backoff_factor,
            initial_delay=request.retry_config.initial_delay,
            fallback_models=request.retry_config.fallback_models
        )

        all_results = []
        failed_skills = []

        # Process each chunk
        for chunk_idx, chunk in enumerate(chunks, 1):
            progress.update_chunk(chunk_idx)

            # Create prompt for this chunk
            prompt = create_assessment_prompt(chunk, request.proficiency_levels, request.prompt_template)

            # Get skill names for parsing validation
            expected_skill_names = [skill.get('name', '') for skill in chunk]

            try:
                # Call LLM with retry logic
                llm_service = LLMService(
                    provider=provider,
                    api_key=request.llm_config.api_key,
                    model=request.llm_config.model
                )

                response_text = await llm_service.call_llm_async(
                    prompt=prompt,
                    provider=provider,
                    model=request.llm_config.model,
                    api_key=request.llm_config.api_key,
                    temperature=request.llm_config.temperature,
                    max_tokens=request.llm_config.max_tokens
                )

                # Parse response using multi-stage parser
                parse_result = parse_llm_response(
                    response=response_text,
                    expected_skills=expected_skill_names,
                    required_fields=["skill_name", "proficiency_level"]
                )

                # Add successfully parsed skills
                all_results = merge_assessment_results(all_results, parse_result.parsed_skills)

                # Track completion
                for skill in parse_result.parsed_skills:
                    progress.mark_completed(skill.get('skill_name', ''))

                # Track missing skills for retry
                if parse_result.missing_skills:
                    logger.warning(f"Chunk {chunk_idx}: {len(parse_result.missing_skills)} skills missing from response")
                    for missing_name in parse_result.missing_skills:
                        # Find the original skill dict
                        missing_skill = next((s for s in chunk if s.get('name') == missing_name), None)
                        if missing_skill and missing_skill not in failed_skills:
                            failed_skills.append(missing_skill)

                # Record attempt
                attempt = AssessmentAttempt(
                    model=request.llm_config.model,
                    attempt_number=1,
                    timestamp=datetime.now(),
                    success=True,
                    skills_parsed=len(parse_result.parsed_skills),
                    skills_missing=len(parse_result.missing_skills)
                )
                progress.add_attempt(attempt)

            except Exception as e:
                logger.error(f"Chunk {chunk_idx} failed: {str(e)}")

                # Mark all skills in chunk as failed
                for skill in chunk:
                    skill_name = skill.get('name', '')
                    progress.mark_failed(skill_name, str(e))
                    if skill not in failed_skills:
                        failed_skills.append(skill)

                # Record failed attempt
                attempt = AssessmentAttempt(
                    model=request.llm_config.model,
                    attempt_number=1,
                    timestamp=datetime.now(),
                    success=False,
                    error=str(e),
                    skills_parsed=0,
                    skills_missing=len(chunk)
                )
                progress.add_attempt(attempt)

        # Retry failed skills if enabled
        if failed_skills and request.chunk_config.retry_failed:
            logger.info(f"Retrying {len(failed_skills)} failed skills...")

            # Create smaller chunks for retry (more conservative)
            retry_chunk_size = min(5, chunk_size // 2) if chunk_size > 5 else chunk_size
            retry_chunks = create_chunks(failed_skills, retry_chunk_size)

            for retry_idx, retry_chunk in enumerate(retry_chunks, 1):
                try:
                    prompt = create_assessment_prompt(retry_chunk, request.proficiency_levels, request.prompt_template)
                    expected_names = [s.get('name', '') for s in retry_chunk]

                    llm_service = LLMService(
                        provider=provider,
                        api_key=request.llm_config.api_key,
                        model=request.llm_config.model
                    )

                    response_text = await llm_service.call_llm_async(
                        prompt=prompt,
                        provider=provider,
                        model=request.llm_config.model,
                        api_key=request.llm_config.api_key,
                        temperature=request.llm_config.temperature,
                        max_tokens=request.llm_config.max_tokens
                    )

                    parse_result = parse_llm_response(response_text, expected_names)

                    # Merge retry results
                    all_results = merge_assessment_results(all_results, parse_result.parsed_skills)

                    # Update progress
                    for skill in parse_result.parsed_skills:
                        skill_name = skill.get('skill_name', '')
                        progress.mark_completed(skill_name)
                        # Remove from failed list
                        failed_skills = [s for s in failed_skills if s.get('name') != skill_name]

                except Exception as e:
                    logger.error(f"Retry chunk {retry_idx} failed: {str(e)}")

        # Build response
        processing_time = (datetime.now() - start_time).total_seconds()
        failed_skill_dicts = [{'name': s.get('name'), 'error': 'Failed to assess'} for s in failed_skills]

        return ChunkedAssessmentResponse(
            assessment_id=assessment_id,
            assessments=all_results,
            total_skills=len(request.skills),
            completed_skills=len(all_results),
            failed_skills=failed_skill_dicts,
            total_chunks=len(chunks),
            chunk_size=chunk_size,
            processing_time_seconds=processing_time,
            llm_provider=provider,
            llm_model=request.llm_config.model,
            timestamp=datetime.now().isoformat(),
            progress=progress.get_progress()
        )

    except Exception as e:
        logger.error(f"Chunked assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@router.get("/api/proficiency/health")
async def proficiency_health_check():
    """Health check for proficiency assessment service"""
    return {
        "status": "healthy",
        "service": "proficiency-assessment",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Assessment Batch Management Endpoints
# ============================================================================

class SaveAssessmentBatchRequest(BaseModel):
    """Request model for saving an assessment batch"""
    batch_name: str = Field(..., min_length=1, max_length=255, description="Name for this assessment batch")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    assessments: List[Dict] = Field(..., description="List of assessment results")
    llm_config: Dict = Field(..., description="LLM configuration used")
    configuration_id: Optional[str] = Field(None, description="ID of configuration used")
    proficiency_levels: List[Dict] = Field(..., description="Proficiency levels used")
    prompt_template: str = Field(..., description="Prompt template used")
    total_processing_time_ms: Optional[int] = Field(None, description="Total processing time")


class AssessmentBatchResponse(BaseModel):
    """Response model for assessment batch"""
    id: str
    batch_name: str
    description: Optional[str]
    total_skills: int
    completed_skills: int
    failed_skills: int
    llm_provider: str
    llm_model: str
    status: str
    average_confidence: Optional[float]
    total_processing_time_ms: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]


class AssessmentBatchDetailResponse(AssessmentBatchResponse):
    """Detailed response with assessment results"""
    assessments: List[Dict]
    llm_config: Dict
    proficiency_levels: List[Dict]
    prompt_template: str
    configuration_id: Optional[str]


@router.post("/api/proficiency/batches", response_model=AssessmentBatchDetailResponse)
async def save_assessment_batch(
    request: SaveAssessmentBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Save a completed assessment batch to the database for later retrieval.
    Checks for duplicates based on assessment content similarity.
    """
    try:
        # Calculate statistics
        total_skills = len(request.assessments)
        completed_skills = len([a for a in request.assessments if a.get('proficiency_level')])
        failed_skills = total_skills - completed_skills

        # Calculate average confidence
        confidences = [a.get('confidence_score', 0) for a in request.assessments if a.get('confidence_score')]
        average_confidence = sum(confidences) / len(confidences) if confidences else None

        # Check for duplicate assessments
        # Create a signature based on skills and their proficiency levels
        assessment_signature = sorted([
            f"{a.get('skill_name', '')}:{a.get('proficiency_level', 0)}"
            for a in request.assessments
        ])

        # Query recent batches (last 100) to check for duplicates
        recent_batches = db.query(ProficiencyBatch).order_by(
            ProficiencyBatch.created_at.desc()
        ).limit(100).all()

        for existing_batch in recent_batches:
            if existing_batch.assessments_data:
                existing_signature = sorted([
                    f"{a.get('skill_name', '')}:{a.get('proficiency_level', 0)}"
                    for a in existing_batch.assessments_data
                ])

                # If signatures match exactly, return existing batch instead of creating duplicate
                if assessment_signature == existing_signature:
                    logger.info(f"Duplicate assessment detected, returning existing batch: {existing_batch.id}")
                    return {
                        "id": existing_batch.id,
                        "batch_name": existing_batch.batch_name,
                        "description": existing_batch.description,
                        "total_skills": existing_batch.total_skills,
                        "completed_skills": existing_batch.completed_skills,
                        "failed_skills": existing_batch.failed_skills,
                        "llm_provider": existing_batch.llm_provider,
                        "llm_model": existing_batch.llm_model,
                        "status": existing_batch.status,
                        "average_confidence": existing_batch.average_confidence,
                        "total_processing_time_ms": existing_batch.total_processing_time_ms,
                        "created_at": existing_batch.created_at,
                        "completed_at": existing_batch.completed_at,
                        "assessments": existing_batch.assessments_data or [],
                        "llm_config": existing_batch.llm_config_data or {},
                        "proficiency_levels": existing_batch.proficiency_levels_data or [],
                        "prompt_template": existing_batch.prompt_template or "",
                        "configuration_id": existing_batch.configuration_id
                    }

        # No duplicate found, create new batch record
        batch = ProficiencyBatch(
            batch_name=request.batch_name,
            description=request.description,
            total_skills=total_skills,
            completed_skills=completed_skills,
            failed_skills=failed_skills,
            llm_provider=request.llm_config.get('provider', 'unknown'),
            llm_model=request.llm_config.get('model', 'unknown'),
            status='completed',
            progress_percentage=100.0,
            average_confidence=average_confidence,
            total_processing_time_ms=request.total_processing_time_ms,
            completed_at=datetime.utcnow(),
            # Store full assessment data
            assessments_data=request.assessments,
            llm_config_data=request.llm_config,
            proficiency_levels_data=request.proficiency_levels,
            prompt_template=request.prompt_template,
            configuration_id=request.configuration_id
        )

        db.add(batch)
        db.commit()
        db.refresh(batch)

        return {
            "id": batch.id,
            "batch_name": batch.batch_name,
            "description": request.description,
            "total_skills": batch.total_skills,
            "completed_skills": batch.completed_skills,
            "failed_skills": batch.failed_skills,
            "llm_provider": batch.llm_provider,
            "llm_model": batch.llm_model,
            "status": batch.status,
            "average_confidence": batch.average_confidence,
            "total_processing_time_ms": batch.total_processing_time_ms,
            "created_at": batch.created_at,
            "completed_at": batch.completed_at,
            "assessments": request.assessments,
            "llm_config": request.llm_config,
            "proficiency_levels": request.proficiency_levels,
            "prompt_template": request.prompt_template,
            "configuration_id": request.configuration_id
        }

    except Exception as e:
        logger.error(f"Error saving assessment batch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save assessment batch: {str(e)}"
        )


@router.get("/api/proficiency/batches", response_model=List[AssessmentBatchResponse])
async def list_assessment_batches(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all saved assessment batches with pagination and search
    """
    try:
        query = db.query(ProficiencyBatch)

        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(ProficiencyBatch.batch_name.ilike(search_term))

        # Order by most recent first
        query = query.order_by(ProficiencyBatch.created_at.desc())

        # Pagination
        batches = query.offset(offset).limit(limit).all()

        return [
            {
                "id": batch.id,
                "batch_name": batch.batch_name,
                "description": batch.description,
                "total_skills": batch.total_skills,
                "completed_skills": batch.completed_skills,
                "failed_skills": batch.failed_skills,
                "llm_provider": batch.llm_provider,
                "llm_model": batch.llm_model,
                "status": batch.status,
                "average_confidence": batch.average_confidence,
                "total_processing_time_ms": batch.total_processing_time_ms,
                "created_at": batch.created_at,
                "completed_at": batch.completed_at
            }
            for batch in batches
        ]

    except Exception as e:
        logger.error(f"Error listing assessment batches: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list assessment batches: {str(e)}"
        )


@router.get("/api/proficiency/batches/{batch_id}", response_model=AssessmentBatchDetailResponse)
async def get_assessment_batch(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific assessment batch by ID with full details
    """
    try:
        batch = db.query(ProficiencyBatch).filter(ProficiencyBatch.id == batch_id).first()

        if not batch:
            raise HTTPException(
                status_code=404,
                detail="Assessment batch not found"
            )

        return {
            "id": batch.id,
            "batch_name": batch.batch_name,
            "description": batch.description,
            "total_skills": batch.total_skills,
            "completed_skills": batch.completed_skills,
            "failed_skills": batch.failed_skills,
            "llm_provider": batch.llm_provider,
            "llm_model": batch.llm_model,
            "status": batch.status,
            "average_confidence": batch.average_confidence,
            "total_processing_time_ms": batch.total_processing_time_ms,
            "created_at": batch.created_at,
            "completed_at": batch.completed_at,
            "assessments": batch.assessments_data or [],
            "llm_config": batch.llm_config_data or {},
            "proficiency_levels": batch.proficiency_levels_data or [],
            "prompt_template": batch.prompt_template or "",
            "configuration_id": batch.configuration_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessment batch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get assessment batch: {str(e)}"
        )


@router.delete("/api/proficiency/batches/{batch_id}")
async def delete_assessment_batch(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an assessment batch by ID
    """
    try:
        batch = db.query(ProficiencyBatch).filter(ProficiencyBatch.id == batch_id).first()

        if not batch:
            raise HTTPException(
                status_code=404,
                detail="Assessment batch not found"
            )

        db.delete(batch)
        db.commit()

        return {
            "success": True,
            "message": f"Assessment batch '{batch.batch_name}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assessment batch: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete assessment batch: {str(e)}"
        )


# ============================================================================
# PUSH TO EIGHTFOLD
# ============================================================================

class PushToEightfoldRequest(BaseModel):
    """Request model for pushing proficiencies to Eightfold"""
    environment_id: str = Field(..., description="Eightfold environment ID")
    role_id: str = Field(..., description="Eightfold role ID to update")
    role_title: Optional[str] = Field(None, description="Optional role title for logging")
    assessments: List[Dict[str, Any]] = Field(..., description="List of skill proficiency assessments")


class PushToEightfoldResponse(BaseModel):
    """Response model for push to Eightfold operation"""
    success: bool
    updated: int
    role_id: str
    role_title: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@router.post("/api/proficiency/push-to-eightfold", response_model=PushToEightfoldResponse)
async def push_proficiencies_to_eightfold(request: PushToEightfoldRequest):
    """
    Push skill proficiency assessments to Eightfold for a specific role

    This endpoint:
    1. Authenticates with Eightfold using stored environment credentials
    2. Transforms proficiency assessments to Eightfold API format
    3. Pushes the proficiencies to the role in Eightfold
    4. Returns success/failure status

    Request body:
    ```json
    {
        "environment_id": "env-123",
        "role_id": "role-456",
        "role_title": "Senior Software Engineer",
        "assessments": [
            {
                "skill_name": "Python",
                "proficiency_level": 4,
                "confidence_score": 0.92,
                "reasoning": "...",
                "evidence": ["..."]
            }
        ]
    }
    ```
    """
    try:
        logger.info(f"Pushing proficiencies to Eightfold role: {request.role_id}")
        logger.info(f"Environment ID: {request.environment_id}")
        logger.info(f"Number of assessments: {len(request.assessments)}")

        # Import here to avoid circular dependency
        from app.services.eightfold_client import get_eightfold_client

        # Create Eightfold client
        client = get_eightfold_client(request.environment_id)

        # Push proficiencies
        result = await client.push_proficiencies(
            role_id=request.role_id,
            proficiencies=request.assessments,
            role_title=request.role_title
        )

        if result.get("success"):
            logger.info(f"Successfully pushed {result.get('updated', 0)} proficiencies")
            return PushToEightfoldResponse(
                success=True,
                updated=result.get("updated", 0),
                role_id=request.role_id,
                role_title=request.role_title,
                endpoint=result.get("endpoint"),
                method=result.get("method"),
                details=result.get("response")
            )
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Failed to push proficiencies: {error_msg}")
            return PushToEightfoldResponse(
                success=False,
                updated=0,
                role_id=request.role_id,
                role_title=request.role_title,
                error=error_msg,
                details=result
            )

    except ValueError as e:
        # Environment not found or not active
        logger.error(f"Environment error: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error pushing proficiencies to Eightfold: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to push proficiencies: {str(e)}"
        )