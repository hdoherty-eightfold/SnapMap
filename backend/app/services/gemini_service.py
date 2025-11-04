"""
Google Gemini AI Service
Provides intelligent file analysis, field inference, and data correction
"""

import json
from typing import List, Dict, Any, Optional
import asyncio

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")

from app.core.config import get_settings
from app.services.schema_manager import get_schema_manager


class GeminiService:
    """
    Google Gemini AI service for intelligent data processing
    """

    def __init__(self):
        self.settings = get_settings()
        self.schema_manager = get_schema_manager()
        self.model = None
        self._initialize()

    def _initialize(self):
        """Initialize Gemini API"""
        if not GEMINI_AVAILABLE:
            print("[WARNING] Gemini API not available")
            return

        if not self.settings.gemini_api_key:
            print("[WARNING] Gemini API key not configured")
            return

        try:
            genai.configure(api_key=self.settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("[OK] Gemini AI service initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Gemini: {e}")
            self.model = None

    async def analyze_file_issues(
        self,
        source_fields: List[str],
        sample_data: List[Dict[str, Any]],
        entity_name: str
    ) -> Dict[str, Any]:
        """
        Analyze uploaded file and detect issues

        Args:
            source_fields: List of source field names
            sample_data: Sample rows from uploaded file
            entity_name: Target entity type

        Returns:
            Dict with detected issues and suggested fixes
        """
        if not self.model:
            return {
                "issues_found": [],
                "suggestions": [],
                "can_auto_fix": False,
                "message": "Gemini AI not available"
            }

        # Get target schema
        try:
            schema = self.schema_manager.get_schema(entity_name)
            required_fields = [f.name for f in schema.fields if f.required]
            all_fields = [f.name for f in schema.fields]
        except Exception as e:
            return {
                "issues_found": [],
                "suggestions": [],
                "can_auto_fix": False,
                "message": f"Error loading schema: {str(e)}"
            }

        # Build prompt for Gemini
        prompt = f"""
You are a data quality analyst. Analyze this uploaded data file and identify issues.

TARGET SCHEMA: {entity_name}
Required Fields: {', '.join(required_fields)}
All Available Fields: {', '.join(all_fields)}

UPLOADED FILE:
Column Names: {', '.join(source_fields)}
Sample Data (first 3 rows):
{json.dumps(sample_data[:3], indent=2)}

TASK:
1. Identify missing required fields
2. Detect misnamed or misspelled columns
3. Find data quality issues (wrong formats, missing data, etc.)
4. Suggest field mappings and corrections
5. Determine if issues can be auto-fixed

Return a JSON response with this structure:
{{
  "issues_found": [
    {{
      "type": "missing_required_field" | "misspelled_field" | "data_quality" | "format_error",
      "severity": "critical" | "warning" | "info",
      "field": "field_name",
      "description": "Clear description of the issue",
      "affected_rows": number or "all"
    }}
  ],
  "suggestions": [
    {{
      "issue_type": "type from above",
      "field": "source_field",
      "suggestion": "What to do",
      "target_field": "suggested_target_field",
      "confidence": 0.0-1.0,
      "auto_fixable": true/false
    }}
  ],
  "can_auto_fix": true/false,
  "summary": "Brief summary of issues and fixes"
}}

IMPORTANT: Return ONLY valid JSON, no markdown formatting.
"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )

            # Parse response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse Gemini response: {e}")
            return {
                "issues_found": [],
                "suggestions": [],
                "can_auto_fix": False,
                "message": "Failed to parse AI response"
            }
        except Exception as e:
            print(f"[ERROR] Gemini API error: {e}")
            return {
                "issues_found": [],
                "suggestions": [],
                "can_auto_fix": False,
                "message": f"AI analysis failed: {str(e)}"
            }

    async def suggest_field_mapping(
        self,
        source_field: str,
        entity_name: str,
        context: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest target field mapping using AI

        Args:
            source_field: Source field name to map
            entity_name: Target entity type
            context: Additional context (other field names)

        Returns:
            List of suggested mappings with confidence scores
        """
        if not self.model:
            return []

        try:
            schema = self.schema_manager.get_schema(entity_name)
            target_fields = [
                {
                    "name": f.name,
                    "display_name": f.display_name,
                    "description": f.description
                }
                for f in schema.fields
            ]
        except Exception as e:
            print(f"Error loading schema: {e}")
            return []

        context_str = f"Other source fields: {', '.join(context)}" if context else ""

        prompt = f"""
You are a data mapping expert. Suggest the best target field mapping.

SOURCE FIELD: {source_field}
{context_str}

TARGET SCHEMA ({entity_name}):
{json.dumps(target_fields, indent=2)}

TASK:
Suggest the top 3 most likely target fields for "{source_field}".
Consider:
- Field name similarity
- Semantic meaning
- Common naming conventions
- Context from other fields

Return a JSON array:
[
  {{
    "target_field": "FIELD_NAME",
    "confidence": 0.0-1.0,
    "reasoning": "Why this mapping makes sense"
  }}
]

IMPORTANT: Return ONLY valid JSON array, no markdown formatting.
"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )

            response_text = response.text.strip()

            # Remove markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            suggestions = json.loads(response_text.strip())
            return suggestions

        except Exception as e:
            print(f"Error getting suggestions: {e}")
            return []

    async def infer_data_corrections(
        self,
        field_name: str,
        sample_values: List[Any],
        expected_type: str
    ) -> Dict[str, Any]:
        """
        Infer data corrections for problematic values

        Args:
            field_name: Field name
            sample_values: Sample values with issues
            expected_type: Expected data type

        Returns:
            Dict with correction suggestions
        """
        if not self.model:
            return {"corrections": [], "message": "AI not available"}

        prompt = f"""
You are a data quality expert. Suggest corrections for problematic values.

FIELD: {field_name}
EXPECTED TYPE: {expected_type}
SAMPLE VALUES WITH ISSUES:
{json.dumps(sample_values[:10], indent=2)}

TASK:
1. Identify the issues with these values
2. Suggest corrections to match the expected type
3. Provide transformation rules

Return JSON:
{{
  "issues": ["list of issues"],
  "corrections": [
    {{
      "original": "value",
      "corrected": "value",
      "rule": "transformation rule"
    }}
  ],
  "transformation_pattern": "General pattern to apply"
}}

IMPORTANT: Return ONLY valid JSON, no markdown.
"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )

            response_text = response.text.strip()

            # Remove markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            return result

        except Exception as e:
            print(f"Error getting corrections: {e}")
            return {"corrections": [], "message": str(e)}


async def test_gemini_connection(api_key: str) -> bool:
    """
    Test Gemini API connection

    Args:
        api_key: Gemini API key to test

    Returns:
        bool: True if connection successful
    """
    if not GEMINI_AVAILABLE:
        return False

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = await asyncio.to_thread(
            model.generate_content,
            "Say 'OK' if you can read this."
        )
        return "ok" in response.text.lower()
    except Exception as e:
        print(f"Gemini connection test failed: {e}")
        return False


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get singleton GeminiService instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
