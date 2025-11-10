"""
Gemini-Powered Field Reasoning for Ambiguous Mappings
100% FREE using Google Gemini Flash API

This module adds intelligent reasoning to field mapping for cases where
vector similarity is ambiguous (40-70% confidence).

FREE TIER LIMITS (Gemini Flash):
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

For typical field mapping (5-10 ambiguous fields per file):
- Can process 150-300 files per day for FREE
- Average latency: 200-400ms per field
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from functools import lru_cache
import time
from pathlib import Path

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")


class GeminiFieldReasoner:
    """
    FREE intelligent field reasoning using Google Gemini Flash

    Features:
    - Uses Gemini 1.5 Flash (completely FREE, fast)
    - DUAL API KEY SUPPORT with automatic failover
    - In-memory caching to minimize API calls
    - Sample data analysis for context
    - Batch processing to stay within rate limits
    - Automatic fallback to vector-only if quota exceeded
    """

    def __init__(self, api_keys: list):
        """
        Initialize with multiple API keys for failover

        Args:
            api_keys: List of Google Gemini API keys (e.g., [key1, key2])
                     If one hits rate limit, automatically switches to next
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package required. Install: pip install google-generativeai")

        # Store API keys for failover
        if isinstance(api_keys, str):
            api_keys = [api_keys]  # Convert single key to list

        self.api_keys = api_keys
        self.current_key_index = 0
        self.key_failures = {i: 0 for i in range(len(api_keys))}  # Track failures per key

        # Configure initial key
        self._configure_key(self.current_key_index)

        # In-memory cache to avoid duplicate API calls
        self._cache = {}

        # Rate limiting (free tier: 15 req/min)
        self._last_request_time = 0
        self._min_request_interval = 4.0  # 15 requests per minute = 4 seconds between requests

        # Request counter per key
        self._requests_today = {i: 0 for i in range(len(api_keys))}
        self._requests_last_reset = time.time()

    def _configure_key(self, key_index: int):
        """Configure Gemini with specific API key"""
        try:
            genai.configure(api_key=self.api_keys[key_index])
            # Use the latest free Gemini model (as of 2025)
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.current_key_index = key_index
            print(f"[OK] Configured Gemini with API Key #{key_index + 1}")
        except Exception as e:
            print(f"[WARNING] Failed to configure API Key #{key_index + 1}: {e}")
            raise

    def _switch_to_next_key(self) -> bool:
        """
        Switch to next available API key

        Returns:
            True if successfully switched, False if no keys available
        """
        original_index = self.current_key_index

        # Try each key in order
        for attempt in range(len(self.api_keys)):
            next_index = (original_index + attempt + 1) % len(self.api_keys)

            # Skip keys with too many failures
            if self.key_failures[next_index] >= 5:
                print(f"[WARNING] Skipping API Key #{next_index + 1} (too many failures)")
                continue

            # Check if this key has quota available
            if self._requests_today.get(next_index, 0) < 1500:
                try:
                    self._configure_key(next_index)
                    print(f"[OK] Switched to API Key #{next_index + 1}")
                    return True
                except Exception as e:
                    print(f"[WARNING] Failed to switch to Key #{next_index + 1}: {e}")
                    self.key_failures[next_index] += 1
                    continue

        print("[ERROR] All API keys exhausted or failed")
        return False

    def reason_field_mapping(
        self,
        source_field: str,
        target_candidates: List[Dict],
        sample_data: Optional[List] = None,
        entity_type: str = "unknown"
    ) -> Dict:
        """
        Use Gemini to reason about ambiguous field mapping

        Args:
            source_field: The source field name (e.g., "EmpNo", "WorkTel")
            target_candidates: List of potential target fields with similarity scores
                [{"name": "EMPLOYEE_ID", "similarity": 0.65, "description": "..."}]
            sample_data: Optional sample values from the source field
            entity_type: Target entity type (candidate, employee, etc.)

        Returns:
            {
                "recommended_target": "EMPLOYEE_ID",
                "confidence": 0.82,
                "reasoning": "EmpNo is standard abbreviation for Employee Number",
                "method": "gemini"
            }
        """
        # Check cache first
        cache_key = self._make_cache_key(source_field, target_candidates, entity_type)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Check rate limits
        if not self._check_rate_limit():
            # Quota exceeded - fallback to best vector match
            return {
                "recommended_target": target_candidates[0]["name"] if target_candidates else None,
                "confidence": target_candidates[0]["similarity"] if target_candidates else 0.0,
                "reasoning": "Rate limit reached - using vector similarity",
                "method": "vector_fallback"
            }

        # Build prompt
        prompt = self._build_reasoning_prompt(
            source_field,
            target_candidates,
            sample_data,
            entity_type
        )

        try:
            # Rate limiting
            self._wait_for_rate_limit()

            # Call Gemini API
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)

            # Cache the result
            self._cache[cache_key] = result

            # Update request counter
            self._requests_today[self.current_key_index] = self._requests_today.get(self.current_key_index, 0) + 1

            return result

        except Exception as e:
            error_msg = str(e).lower()

            # Check if it's a rate limit error
            if 'quota' in error_msg or 'rate limit' in error_msg or '429' in error_msg:
                print(f"[WARNING] Rate limit hit on API Key #{self.current_key_index + 1}")

                # Try to switch to next key
                if self._switch_to_next_key():
                    print("[INFO] Retrying with new API key...")
                    # Retry the request with new key
                    try:
                        self._wait_for_rate_limit()
                        response = self.model.generate_content(prompt)
                        result = self._parse_gemini_response(response.text)
                        self._cache[cache_key] = result
                        self._requests_today[self.current_key_index] = self._requests_today.get(self.current_key_index, 0) + 1
                        return result
                    except Exception as retry_error:
                        print(f"[WARNING] Retry failed: {retry_error}")

            print(f"Gemini reasoning failed: {e}")
            # Track failure
            self.key_failures[self.current_key_index] += 1

            # Fallback to best vector match
            return {
                "recommended_target": target_candidates[0]["name"] if target_candidates else None,
                "confidence": target_candidates[0]["similarity"] if target_candidates else 0.0,
                "reasoning": f"Gemini failed - using vector similarity. Error: {str(e)[:100]}",
                "method": "vector_fallback"
            }

    def batch_reason_fields(
        self,
        field_mappings: List[Dict],
        entity_type: str = "unknown"
    ) -> List[Dict]:
        """
        Process multiple ambiguous fields in a single batch
        More efficient - uses one API call instead of N calls

        Args:
            field_mappings: List of field mapping requests
                [{
                    "source_field": "EmpNo",
                    "candidates": [...],
                    "sample_data": [...]
                }]

        Returns:
            List of reasoning results matching input order
        """
        if not field_mappings:
            return []

        # Check rate limit for batch
        if not self._check_rate_limit():
            # Return vector fallback for all
            return [
                {
                    "recommended_target": fm["candidates"][0]["name"] if fm["candidates"] else None,
                    "confidence": fm["candidates"][0]["similarity"] if fm["candidates"] else 0.0,
                    "reasoning": "Rate limit reached",
                    "method": "vector_fallback"
                }
                for fm in field_mappings
            ]

        # Build batch prompt
        prompt = self._build_batch_reasoning_prompt(field_mappings, entity_type)

        try:
            self._wait_for_rate_limit()
            response = self.model.generate_content(prompt)
            results = self._parse_batch_response(response.text, len(field_mappings))
            self._requests_today[self.current_key_index] = self._requests_today.get(self.current_key_index, 0) + 1
            return results

        except Exception as e:
            error_msg = str(e).lower()

            # Check if it's a rate limit error
            if 'quota' in error_msg or 'rate limit' in error_msg or '429' in error_msg:
                print(f"[WARNING] Rate limit hit on API Key #{self.current_key_index + 1}")

                # Try to switch to next key
                if self._switch_to_next_key():
                    print("[INFO] Retrying batch with new API key...")
                    try:
                        self._wait_for_rate_limit()
                        response = self.model.generate_content(prompt)
                        results = self._parse_batch_response(response.text, len(field_mappings))
                        self._requests_today[self.current_key_index] = self._requests_today.get(self.current_key_index, 0) + 1
                        return results
                    except Exception as retry_error:
                        print(f"[WARNING] Retry failed: {retry_error}")

            print(f"Batch reasoning failed: {e}")
            self.key_failures[self.current_key_index] += 1

            # Fallback to vector matches
            return [
                {
                    "recommended_target": fm["candidates"][0]["name"] if fm["candidates"] else None,
                    "confidence": fm["candidates"][0]["similarity"] if fm["candidates"] else 0.0,
                    "reasoning": "Batch failed - using vector",
                    "method": "vector_fallback"
                }
                for fm in field_mappings
            ]

    def _build_reasoning_prompt(
        self,
        source_field: str,
        candidates: List[Dict],
        sample_data: Optional[List],
        entity_type: str
    ) -> str:
        """Build optimized prompt for Gemini Flash"""

        # Format candidates
        candidates_text = "\n".join([
            f"{i+1}. {c['name']} (similarity: {c['similarity']:.2f}) - {c.get('description', 'No description')}"
            for i, c in enumerate(candidates[:5])  # Limit to top 5
        ])

        # Add sample data if available
        sample_text = ""
        if sample_data and len(sample_data) > 0:
            sample_values = [str(v)[:50] for v in sample_data[:5]]  # Truncate long values
            sample_text = f"\nSample values from '{source_field}':\n" + "\n".join([f"  - {v}" for v in sample_values])

        prompt = f"""You are a data mapping expert. Map this source field to the best target field.

SOURCE FIELD: "{source_field}"
ENTITY TYPE: {entity_type}
{sample_text}

TARGET FIELD OPTIONS:
{candidates_text}

INSTRUCTIONS:
1. Consider the field name, abbreviations, and sample data
2. Choose the BEST matching target field
3. Provide confidence (0.50-0.90 scale)
4. Give brief reasoning (1 sentence)

OUTPUT (JSON only, no markdown):
{{
  "target": "EMPLOYEE_ID",
  "confidence": 0.82,
  "reasoning": "EmpNo is standard abbreviation for Employee ID"
}}"""

        return prompt

    def _build_batch_reasoning_prompt(
        self,
        field_mappings: List[Dict],
        entity_type: str
    ) -> str:
        """Build batch prompt - more efficient than individual calls"""

        fields_text = ""
        for i, fm in enumerate(field_mappings[:10]):  # Limit to 10 fields per batch
            candidates_text = ", ".join([
                f"{c['name']}({c['similarity']:.2f})"
                for c in fm["candidates"][:3]
            ])

            sample_text = ""
            if fm.get("sample_data"):
                samples = [str(v)[:30] for v in fm["sample_data"][:3]]
                sample_text = f" [samples: {', '.join(samples)}]"

            fields_text += f"\n{i+1}. '{fm['source_field']}' → Options: {candidates_text}{sample_text}"

        prompt = f"""Map these {len(field_mappings)} source fields to target fields for {entity_type} entity.

FIELDS TO MAP:{fields_text}

OUTPUT (JSON array only, no markdown):
[
  {{"target": "EMPLOYEE_ID", "confidence": 0.82, "reasoning": "EmpNo = Employee ID"}},
  {{"target": "FIRST_NAME", "confidence": 0.78, "reasoning": "FName is common abbreviation"}}
]"""

        return prompt

    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini JSON response"""
        try:
            # Extract JSON from response (Gemini might add markdown)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            return {
                "recommended_target": data.get("target"),
                "confidence": float(data.get("confidence", 0.75)),
                "reasoning": data.get("reasoning", ""),
                "method": "gemini"
            }

        except Exception as e:
            print(f"Failed to parse Gemini response: {e}\nResponse: {response_text[:200]}")
            return {
                "recommended_target": None,
                "confidence": 0.0,
                "reasoning": f"Parse error: {str(e)}",
                "method": "error"
            }

    def _parse_batch_response(self, response_text: str, expected_count: int) -> List[Dict]:
        """Parse batch JSON response"""
        try:
            # Extract JSON array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON array found")

            data = json.loads(json_match.group())

            results = []
            for item in data[:expected_count]:
                results.append({
                    "recommended_target": item.get("target"),
                    "confidence": float(item.get("confidence", 0.75)),
                    "reasoning": item.get("reasoning", ""),
                    "method": "gemini_batch"
                })

            # Fill in missing items with None
            while len(results) < expected_count:
                results.append({
                    "recommended_target": None,
                    "confidence": 0.0,
                    "reasoning": "Missing from batch response",
                    "method": "error"
                })

            return results

        except Exception as e:
            print(f"Failed to parse batch response: {e}")
            return [{
                "recommended_target": None,
                "confidence": 0.0,
                "reasoning": f"Parse error: {str(e)}",
                "method": "error"
            }] * expected_count

    def _make_cache_key(self, source_field: str, candidates: List[Dict], entity_type: str) -> str:
        """Create cache key for deduplication"""
        candidate_names = sorted([c["name"] for c in candidates[:3]])
        return f"{source_field}_{entity_type}_{'_'.join(candidate_names)}"

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits

        Free tier limits:
        - 15 requests per minute
        - 1,500 requests per day (per key)
        """
        # Reset daily counter if needed
        if time.time() - self._requests_last_reset > 86400:  # 24 hours
            self._requests_today = {i: 0 for i in range(len(self.api_keys))}
            self._requests_last_reset = time.time()

        # Check daily limit for current key
        current_requests = self._requests_today.get(self.current_key_index, 0)
        if current_requests >= 1500:
            print(f"[WARNING] API Key #{self.current_key_index + 1} daily quota (1,500) reached.")

            # Try to switch to another key
            if self._switch_to_next_key():
                return True
            else:
                print("[WARNING] All API keys exhausted. Using vector fallback.")
                return False

        return True

    def _wait_for_rate_limit(self):
        """Wait if necessary to stay within rate limits"""
        time_since_last = time.time() - self._last_request_time
        if time_since_last < self._min_request_interval:
            wait_time = self._min_request_interval - time_since_last
            time.sleep(wait_time)

        self._last_request_time = time.time()

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics for all API keys"""
        total_requests = sum(self._requests_today.values())
        total_limit = len(self.api_keys) * 1500

        # Per-key stats
        key_stats = []
        for i, key in enumerate(self.api_keys):
            masked_key = f"{key[:20]}..." if len(key) > 20 else key
            requests = self._requests_today.get(i, 0)
            failures = self.key_failures.get(i, 0)
            is_current = (i == self.current_key_index)

            key_stats.append({
                "key_number": i + 1,
                "key_preview": masked_key,
                "requests_today": requests,
                "remaining": 1500 - requests,
                "failures": failures,
                "active": is_current
            })

        return {
            "total_requests_today": total_requests,
            "total_daily_limit": total_limit,
            "total_remaining": total_limit - total_requests,
            "api_keys_count": len(self.api_keys),
            "current_key": self.current_key_index + 1,
            "cache_size": len(self._cache),
            "key_stats": key_stats
        }

    def clear_cache(self):
        """Clear in-memory cache"""
        self._cache.clear()
        print("Cache cleared")


# Singleton instance
_gemini_reasoner = None


def get_gemini_reasoner(api_keys: list = None) -> GeminiFieldReasoner:
    """
    Get singleton Gemini reasoner instance

    Args:
        api_keys: List of Google Gemini API keys (required on first call)
                 Can also be a single string key
    """
    global _gemini_reasoner

    if _gemini_reasoner is None:
        if not api_keys:
            raise ValueError("API key(s) required on first initialization")
        _gemini_reasoner = GeminiFieldReasoner(api_keys)

    return _gemini_reasoner
