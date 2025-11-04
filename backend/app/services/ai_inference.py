"""
AI Inference Service
Uses AI to infer schemas, correct field mappings, and detect entity types
"""

from typing import Dict, List, Optional, Tuple
import re
from difflib import SequenceMatcher
from collections import Counter

from app.services.schema_manager import get_schema_manager
from app.services.field_mapper import FieldMapper

try:
    from app.services.semantic_matcher import get_semantic_matcher
    SEMANTIC_MATCHING_AVAILABLE = True
except Exception:
    SEMANTIC_MATCHING_AVAILABLE = False


class AIInferenceService:
    """
    AI-powered schema inference and correction service

    This service helps when clients provide data that doesn't exactly match
    the Eightfold schema by:
    1. Detecting the most likely entity type from column names
    2. Inferring field mappings with higher intelligence
    3. Suggesting corrections for misnamed or mistyped fields
    """

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.field_mapper = FieldMapper()
        self.semantic_matcher = None
        if SEMANTIC_MATCHING_AVAILABLE:
            try:
                self.semantic_matcher = get_semantic_matcher()
            except Exception:
                pass

    def detect_entity_type(self, source_fields: List[str]) -> Tuple[str, float]:
        """
        Detect the most likely entity type from source field names

        Uses semantic similarity if available, falls back to string matching

        Args:
            source_fields: List of field names from uploaded file

        Returns:
            Tuple of (entity_name, confidence_score)
        """
        # Try semantic matching first (much more accurate!)
        if self.semantic_matcher and self.semantic_matcher.model:
            try:
                entities = self.schema_manager.get_available_entities()
                scores = {}

                for entity in entities:
                    entity_id = entity["id"]
                    if not self.schema_manager.entity_exists(entity_id):
                        continue

                    try:
                        # Use semantic matching to get average similarity
                        mappings = self.semantic_matcher.map_fields_batch(
                            source_fields,
                            entity_id,
                            min_confidence=0.3
                        )

                        # Calculate average confidence for mapped fields
                        confidences = [m['confidence'] for m in mappings if m['target_field']]
                        if confidences:
                            avg_confidence = sum(confidences) / len(source_fields)
                            scores[entity_id] = avg_confidence
                        else:
                            scores[entity_id] = 0.0

                    except Exception:
                        continue

                if scores:
                    best_entity = max(scores.items(), key=lambda x: x[1])
                    return best_entity[0], best_entity[1]

            except Exception as e:
                print(f"Semantic entity detection failed: {e}, falling back...")

        # Fallback to traditional string-based matching
        entities = self.schema_manager.get_available_entities()
        normalized_source = [self._normalize_field(f) for f in source_fields]
        scores = {}

        for entity in entities:
            entity_id = entity["id"]

            if not self.schema_manager.entity_exists(entity_id):
                continue

            try:
                schema = self.schema_manager.get_schema(entity_id)
                target_fields = [f.name for f in schema.fields]
                normalized_target = [self._normalize_field(f) for f in target_fields]

                score = self._calculate_entity_match_score(
                    normalized_source,
                    normalized_target,
                    entity_id
                )
                scores[entity_id] = score

            except Exception:
                continue

        if not scores:
            return "employee", 0.0

        best_entity = max(scores.items(), key=lambda x: x[1])
        return best_entity[0], best_entity[1]

    def _calculate_entity_match_score(
        self,
        source_fields: List[str],
        target_fields: List[str],
        entity_id: str
    ) -> float:
        """
        Calculate how well source fields match a target entity schema

        Uses multiple scoring factors:
        - Direct field name matches
        - Partial/fuzzy matches
        - Entity-specific keyword presence
        """
        if not source_fields:
            return 0.0

        # Direct and fuzzy matches
        match_count = 0
        for source in source_fields:
            for target in target_fields:
                similarity = SequenceMatcher(None, source, target).ratio()
                if similarity > 0.7:  # High similarity threshold
                    match_count += 1
                    break

        base_score = match_count / len(source_fields)

        # Boost score based on entity-specific keywords
        keyword_boost = self._calculate_keyword_boost(source_fields, entity_id)

        # Combine scores (base score weighted more heavily)
        final_score = (base_score * 0.8) + (keyword_boost * 0.2)

        return min(final_score, 1.0)

    def _calculate_keyword_boost(self, source_fields: List[str], entity_id: str) -> float:
        """
        Boost score based on entity-specific keywords in field names
        """
        # Define entity-specific keywords
        entity_keywords = {
            "employee": ["employee", "emp", "staff", "worker", "personnel"],
            "user": ["user", "account", "login", "username"],
            "position": ["position", "job", "requisition", "opening", "vacancy"],
            "candidate": ["candidate", "applicant", "application", "cand"],
            "course": ["course", "training", "class", "curriculum", "lesson"],
            "role": ["role", "permission", "access", "privilege"],
            "demand": ["demand", "forecast", "planning", "workforce"],
            "holiday": ["holiday", "vacation", "leave", "absence"],
            "org_unit": ["org", "organization", "department", "unit", "division"],
            "foundation_data": ["foundation", "master", "reference"],
            "pay_grade": ["pay", "grade", "salary", "compensation", "wage"],
            "project": ["project", "initiative", "program"],
            "succession_plan": ["succession", "pipeline", "talent"],
            "planned_event": ["event", "meeting", "schedule"],
            "certificate": ["certificate", "certification", "credential", "cert"],
            "offer": ["offer", "proposal", "compensation"]
        }

        keywords = entity_keywords.get(entity_id, [])
        if not keywords:
            return 0.0

        # Count keyword occurrences in field names
        keyword_count = 0
        for field in source_fields:
            field_lower = field.lower()
            for keyword in keywords:
                if keyword in field_lower:
                    keyword_count += 1
                    break

        return min(keyword_count / len(source_fields), 1.0)

    def _normalize_field(self, field_name: str) -> str:
        """
        Normalize field name for comparison

        - Convert to lowercase
        - Remove special characters
        - Remove common prefixes/suffixes
        """
        # Convert to lowercase
        normalized = field_name.lower()

        # Remove underscores, hyphens, spaces
        normalized = re.sub(r'[_\-\s]+', '', normalized)

        # Remove common prefixes
        prefixes = ['ef_', 'eightfold_', 'sf_', 'wd_', 'workday_', 'sap_']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break

        return normalized

    def infer_field_corrections(
        self,
        source_field: str,
        entity_name: str
    ) -> List[Dict[str, any]]:
        """
        Suggest corrections for a source field that might be misnamed

        Uses semantic similarity if available for much better suggestions

        Args:
            source_field: The field name from the source file
            entity_name: Target entity type

        Returns:
            List of suggested corrections with confidence scores
        """
        # Try semantic matching first
        if self.semantic_matcher and self.semantic_matcher.model:
            try:
                matches = self.semantic_matcher.find_best_match(
                    source_field,
                    entity_name,
                    top_k=3,
                    min_similarity=0.3
                )

                suggestions = []
                for match in matches:
                    suggestions.append({
                        "target_field": match['target_field'],
                        "display_name": match['display_name'],
                        "confidence": match['similarity'],
                        "reason": f"Semantic similarity: {match['similarity']:.2%}",
                        "description": match.get('description', ''),
                        "match_method": "semantic"
                    })

                return suggestions

            except Exception as e:
                print(f"Semantic field correction failed: {e}, falling back...")

        # Fallback to fuzzy matching
        schema = self.schema_manager.get_schema(entity_name)
        target_fields = [f.name for f in schema.fields]

        suggestions = []

        for target_field in target_fields:
            similarity = self._field_similarity(source_field, target_field)

            if similarity > 0.5:
                field_def = next(f for f in schema.fields if f.name == target_field)
                suggestions.append({
                    "target_field": target_field,
                    "display_name": field_def.display_name,
                    "confidence": similarity,
                    "reason": self._get_similarity_reason(source_field, target_field),
                    "match_method": "fuzzy"
                })

        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:3]

    def _field_similarity(self, source: str, target: str) -> float:
        """
        Calculate similarity between two field names

        Uses multiple comparison methods and returns the best score
        """
        # Normalize both fields
        norm_source = self._normalize_field(source)
        norm_target = self._normalize_field(target)

        # Direct match
        if norm_source == norm_target:
            return 1.0

        # Sequence matching
        seq_score = SequenceMatcher(None, norm_source, norm_target).ratio()

        # Check if one contains the other
        if norm_source in norm_target or norm_target in norm_source:
            containment_score = 0.85
        else:
            containment_score = 0.0

        # Check for common abbreviations/patterns
        abbr_score = self._check_abbreviation_match(source, target)

        # Return best score
        return max(seq_score, containment_score, abbr_score)

    def _check_abbreviation_match(self, source: str, target: str) -> float:
        """
        Check if fields match common abbreviation patterns

        Examples:
        - "fname" -> "first_name"
        - "empid" -> "employee_id"
        """
        abbr_patterns = {
            "fname": "first_name",
            "lname": "last_name",
            "empid": "employee_id",
            "empno": "employee_id",
            "userid": "user_id",
            "posid": "position_id",
            "candid": "candidate_id",
        }

        norm_source = self._normalize_field(source)
        norm_target = self._normalize_field(target)

        # Check if source matches any abbreviation pattern for target
        for abbr, full in abbr_patterns.items():
            if norm_source == abbr and norm_target == full:
                return 0.9
            if norm_source == full and norm_target == abbr:
                return 0.9

        return 0.0

    def _get_similarity_reason(self, source: str, target: str) -> str:
        """
        Get human-readable reason for similarity match
        """
        norm_source = self._normalize_field(source)
        norm_target = self._normalize_field(target)

        if norm_source == norm_target:
            return "Exact match (normalized)"

        if norm_source in norm_target:
            return f"'{source}' is contained in '{target}'"

        if norm_target in norm_source:
            return f"'{target}' is contained in '{source}'"

        similarity = SequenceMatcher(None, norm_source, norm_target).ratio()
        if similarity > 0.8:
            return "Very similar field names"
        elif similarity > 0.6:
            return "Similar field names"
        else:
            return "Partial match"

    def validate_and_suggest_fixes(
        self,
        source_fields: List[str],
        entity_name: str
    ) -> Dict[str, any]:
        """
        Validate source fields against target schema and suggest fixes

        Args:
            source_fields: List of field names from source file
            entity_name: Target entity type

        Returns:
            Dictionary with validation results and suggestions
        """
        schema = self.schema_manager.get_schema(entity_name)
        required_fields = [f.name for f in schema.get_required_fields()]

        # Get automatic mappings
        mappings = self.field_mapper.auto_map(source_fields, schema)

        # Find unmapped required fields
        mapped_targets = {m.target for m in mappings if m.target}
        missing_required = [f for f in required_fields if f not in mapped_targets]

        # Generate suggestions for missing required fields
        suggestions = {}
        for missing_field in missing_required:
            # Find best unmapped source field for this target
            unmapped_sources = [f for f in source_fields
                              if not any(m.source == f and m.target
                                       for m in mappings)]

            if unmapped_sources:
                best_match = max(
                    unmapped_sources,
                    key=lambda s: self._field_similarity(s, missing_field)
                )
                confidence = self._field_similarity(best_match, missing_field)

                if confidence > 0.4:  # Reasonable threshold
                    suggestions[missing_field] = {
                        "suggested_source": best_match,
                        "confidence": confidence,
                        "field_info": next(f for f in schema.fields if f.name == missing_field).dict()
                    }

        return {
            "valid": len(missing_required) == 0,
            "missing_required_fields": missing_required,
            "suggested_mappings": suggestions,
            "auto_mapped_count": len([m for m in mappings if m.target]),
            "total_source_fields": len(source_fields),
            "total_target_fields": len(schema.fields)
        }


# Singleton instance
_ai_inference_service = None


def get_ai_inference_service() -> AIInferenceService:
    """Get singleton AIInferenceService instance"""
    global _ai_inference_service
    if _ai_inference_service is None:
        _ai_inference_service = AIInferenceService()
    return _ai_inference_service
