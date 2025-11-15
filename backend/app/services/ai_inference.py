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

    def detect_entity_type(self, source_fields: List[str], filename: str = None) -> Dict[str, any]:
        """
        Detect the most likely entity type from source field names with detailed analysis

        Uses semantic similarity if available, falls back to string matching

        Args:
            source_fields: List of field names from uploaded file
            filename: Original filename (optional, helps with detection)

        Returns:
            Dictionary with detection results including format variant and matched patterns
        """
        # Debug logging (can be disabled for production)
        # print(f"[DEBUG] Entity detection called with:")
        # print(f"  - Source fields: {source_fields}")
        # print(f"  - Filename: {filename}")

        # First run keyword-based detection to get baseline scores
        entities = self.schema_manager.get_available_entities()
        normalized_source = [self._normalize_field(f) for f in source_fields]
        keyword_scores = {}

        # Check filename for entity hints first
        filename_boost = {}
        if filename:
            filename_boost = self._detect_entity_from_filename(filename)

        for entity in entities:
            entity_id = entity["id"]
            if not self.schema_manager.entity_exists(entity_id):
                continue

            try:
                schema = self.schema_manager.get_schema(entity_id)
                target_fields = [f.name for f in schema.fields]
                normalized_target = [self._normalize_field(f) for f in target_fields]

                # Calculate keyword-based score
                keyword_score = self._calculate_keyword_boost(source_fields, entity_id)

                # Apply filename boost if available
                if entity_id in filename_boost:
                    keyword_score = min(keyword_score + filename_boost[entity_id], 1.0)

                keyword_scores[entity_id] = keyword_score
                # print(f"[DEBUG] {entity_id}: keyword_score={keyword_score:.3f}")

            except Exception:
                continue

        # Find the best keyword-based detection
        best_keyword_entity = max(keyword_scores.items(), key=lambda x: x[1]) if keyword_scores else ("employee", 0.0)
        keyword_entity, keyword_confidence = best_keyword_entity

        # print(f"[DEBUG] Best keyword match: {keyword_entity} ({keyword_confidence:.3f})")

        # If keyword detection has high confidence (>0.7), trust it over semantic matching
        if keyword_confidence > 0.7:
            # print(f"[DEBUG] High keyword confidence, using keyword result")

            # Detect format variant for high-confidence keyword result
            format_info = self._detect_format_variant(source_fields, keyword_entity)

            return {
                "detected_entity": keyword_entity,
                "confidence": keyword_confidence,
                "variant": format_info["variant"],
                "description": format_info["description"],
                "variant_confidence": format_info["confidence"],
                "matched_patterns": format_info["matched_patterns"],
                "sample_file": format_info.get("sample_file"),
                "filename": filename
            }

        # Try semantic matching for additional validation
        if self.semantic_matcher and self.semantic_matcher.model:
            try:
                semantic_scores = {}

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
                            semantic_scores[entity_id] = avg_confidence
                        else:
                            semantic_scores[entity_id] = 0.0

                    except Exception:
                        continue

                if semantic_scores:
                    best_semantic = max(semantic_scores.items(), key=lambda x: x[1])
                    semantic_entity, semantic_confidence = best_semantic
                    # print(f"[DEBUG] Best semantic match: {semantic_entity} ({semantic_confidence:.3f})")

                    # Combine keyword and semantic scores with preference for keyword
                    final_scores = {}
                    for entity_id in keyword_scores:
                        keyword_score = keyword_scores.get(entity_id, 0.0)
                        semantic_score = semantic_scores.get(entity_id, 0.0)

                        # Weight keyword matching more heavily for better employee detection
                        combined_score = (keyword_score * 0.7) + (semantic_score * 0.3)
                        final_scores[entity_id] = combined_score
                        # print(f"[DEBUG] {entity_id}: combined_score={combined_score:.3f} (k:{keyword_score:.3f}, s:{semantic_score:.3f})")

                    best_combined = max(final_scores.items(), key=lambda x: x[1])
                    combined_entity, combined_confidence = best_combined

                    # Detect format variant for combined result
                    format_info = self._detect_format_variant(source_fields, combined_entity)

                    return {
                        "detected_entity": combined_entity,
                        "confidence": combined_confidence,
                        "variant": format_info["variant"],
                        "description": format_info["description"],
                        "variant_confidence": format_info["confidence"],
                        "matched_patterns": format_info["matched_patterns"],
                        "sample_file": format_info.get("sample_file"),
                        "filename": filename
                    }

            except Exception as e:
                # print(f"[DEBUG] Semantic entity detection failed: {e}, using keyword result")
                pass

        # Return detailed result with format variant information
        # print(f"[DEBUG] Using keyword result as fallback")

        # Detect format variant for the detected entity
        format_info = self._detect_format_variant(source_fields, keyword_entity)

        return {
            "detected_entity": keyword_entity,
            "confidence": keyword_confidence,
            "variant": format_info["variant"],
            "description": format_info["description"],
            "variant_confidence": format_info["confidence"],
            "matched_patterns": format_info["matched_patterns"],
            "sample_file": format_info.get("sample_file"),
            "filename": filename
        }

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

        # Combine scores - give more weight to keyword matching for better entity detection
        # Especially important when field names don't match exactly but context is clear
        if keyword_boost > 0.5:
            # Strong keyword match - weight keywords heavily
            final_score = (base_score * 0.4) + (keyword_boost * 0.6)
        else:
            # Weak keyword match - weight field matching more
            final_score = (base_score * 0.7) + (keyword_boost * 0.3)

        return min(final_score, 1.0)

    def _calculate_keyword_boost(self, source_fields: List[str], entity_id: str) -> float:
        """
        Boost score based on entity-specific keywords in field names
        Enhanced with better employee detection patterns
        """
        # Define entity-specific keywords with more specificity and real-world patterns
        entity_keywords = {
            "employee": [
                # Core employee identifiers (highest weight)
                "employee", "worker", "staff", "personnel", "emp",
                # Common HR field patterns
                "hire", "hiring", "start_date", "join", "onboard",
                "salary", "wage", "compensation", "pay", "bonus",
                "manager", "supervisor", "reports_to", "manager_name",
                "department", "division", "business_unit", "org_unit",
                "job_title", "title", "position", "role", "job_profile", "job_code",
                "location", "office", "work_location", "site",
                "phone", "work_phone", "extension",
                "legal_first", "legal_last", "preferred_name",
                "termination", "separation", "end_date",
                # Skills and performance
                "skill", "competency", "performance", "review",
                "level", "grade", "band",
                # Cost centers and organizational data
                "cost_center", "cost_centre", "budget_code"
            ],
            "user": [
                # System user fields
                "user", "account", "login", "username", "password", "auth",
                "permission", "access", "privilege", "role",
                "created", "last_login", "status", "active", "inactive",
                "profile", "settings", "preferences"
            ],
            "position": ["position", "job", "requisition", "opening", "vacancy", "posting", "req"],
            "candidate": ["candidate", "applicant", "application", "cand", "interview", "application_date"],
            "course": ["course", "training", "class", "curriculum", "lesson", "certification", "learning"],
            "role": ["role", "permission", "access", "privilege", "function", "responsibility"],
            "demand": ["demand", "forecast", "planning", "workforce", "headcount", "capacity"],
            "holiday": ["holiday", "vacation", "leave", "absence", "time_off", "pto"],
            "org_unit": ["org", "organization", "department", "unit", "division", "team", "group"],
            "foundation_data": ["foundation", "master", "reference", "lookup", "config"],
            "pay_grade": ["pay", "grade", "salary", "compensation", "wage", "band", "level"],
            "project": ["project", "initiative", "program", "assignment", "allocation"],
            "succession_plan": ["succession", "pipeline", "talent", "successor", "career_path"],
            "planned_event": ["event", "meeting", "schedule", "calendar", "appointment"],
            "certificate": ["certificate", "certification", "credential", "cert", "license"],
            "offer": ["offer", "proposal", "compensation", "package", "offer_date"]
        }

        keywords = entity_keywords.get(entity_id, [])
        if not keywords:
            return 0.0

        # Enhanced high-confidence patterns for better employee detection
        high_confidence_patterns = {
            "employee": [
                # Exact field name matches (weight 5x)
                ("employee_id", 5.0), ("worker_id", 5.0), ("emp_id", 5.0), ("staff_id", 5.0),
                ("hire_date", 4.0), ("hiring_date", 4.0), ("start_date", 4.0),
                ("manager_name", 4.0), ("supervisor", 4.0), ("reports_to", 4.0),
                ("job_title", 4.0), ("job_profile", 4.0), ("position_title", 4.0),
                ("cost_center", 4.0), ("cost_centre", 4.0),
                ("work_location", 3.5), ("work_phone", 3.5),
                ("legal_first_name", 3.5), ("legal_last_name", 3.5),
                ("business_unit", 3.0), ("department", 3.0)
            ],
            "user": [
                # System user patterns (weight 5x)
                ("user_id", 5.0), ("username", 5.0), ("login", 4.0),
                ("password", 4.0), ("last_login", 4.0),
                ("created_date", 3.0), ("account_status", 3.0)
            ]
        }

        # Calculate weighted keyword score
        keyword_score = 0.0
        total_weight = 0.0

        # Get high confidence patterns for this entity
        high_conf_patterns = high_confidence_patterns.get(entity_id, [])

        for field in source_fields:
            field_lower = self._normalize_field(field).lower()
            field_original = field.lower()

            # Check high-confidence patterns first
            pattern_matched = False
            for pattern, weight in high_conf_patterns:
                pattern_norm = self._normalize_field(pattern).lower()

                # Check both normalized and original field names
                if (pattern_norm in field_lower or field_lower in pattern_norm or
                    pattern.lower() in field_original or field_original in pattern.lower()):
                    keyword_score += weight
                    total_weight += weight
                    pattern_matched = True
                    break

            # If no high-confidence pattern matched, check regular keywords
            if not pattern_matched:
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if (keyword_lower in field_lower or keyword_lower in field_original):
                        keyword_score += 1.0
                        total_weight += 1.0
                        break
                else:
                    # No keyword match, add minimal weight
                    total_weight += 0.1

        # Calculate normalized score with emphasis on matched patterns
        if total_weight > 0:
            base_score = keyword_score / total_weight

            # Boost employee detection if we have strong employee indicators
            if entity_id == "employee":
                # Check for strong employee field combinations
                employee_indicators = 0
                for field in source_fields:
                    field_norm = self._normalize_field(field).lower()
                    if any(pattern in field_norm for pattern in ["worker", "employee", "hire", "manager", "job", "cost"]):
                        employee_indicators += 1

                # Boost score if we have multiple employee indicators
                if employee_indicators >= 3:
                    base_score *= 1.5
                elif employee_indicators >= 2:
                    base_score *= 1.2

            return min(base_score, 1.0)

        return 0.0

    def _detect_entity_from_filename(self, filename: str) -> Dict[str, float]:
        """
        Detect entity type hints from filename

        Args:
            filename: The original filename

        Returns:
            Dictionary with entity_id -> confidence_boost mappings
        """
        filename_lower = filename.lower()
        filename_patterns = {
            "employee": ["employee", "worker", "staff", "personnel", "emp", "hr"],
            "user": ["user", "account", "login", "auth"],
            "position": ["position", "job", "requisition", "opening"],
            "candidate": ["candidate", "applicant", "application"],
            "course": ["course", "training", "class"],
            "role": ["role", "permission", "access"],
            "demand": ["demand", "forecast", "planning"],
            "holiday": ["holiday", "vacation", "leave"],
            "org_unit": ["org", "organization", "department"],
            "pay_grade": ["pay", "grade", "salary"],
            "project": ["project", "initiative"],
            "succession_plan": ["succession", "pipeline"],
            "planned_event": ["event", "meeting"],
            "certificate": ["certificate", "cert"],
            "offer": ["offer", "proposal"]
        }

        boosts = {}
        for entity_id, patterns in filename_patterns.items():
            for pattern in patterns:
                if pattern in filename_lower:
                    # Give higher boost for exact pattern matches
                    if pattern == filename_lower.split('.')[0]:  # Exact filename match
                        boosts[entity_id] = 0.3
                    else:
                        boosts[entity_id] = 0.15
                    break

        return boosts

    def _detect_format_variant(self, source_fields: List[str], entity_type: str) -> Dict[str, any]:
        """
        Detect the specific format variant within an entity type

        Args:
            source_fields: List of field names from uploaded file
            entity_type: Detected entity type

        Returns:
            Dictionary with format variant details
        """
        if entity_type != "employee":
            return {
                "variant": entity_type.title(),
                "description": f"Standard {entity_type} format",
                "confidence": 1.0,
                "matched_patterns": []
            }

        # Employee format patterns
        employee_variants = {
            "workday": {
                "name": "Employee - Workday Format",
                "description": "Workday/SAP style employee data with Worker_ID and Legal names",
                "patterns": [
                    "worker_id", "legal_first_name", "legal_last_name",
                    "cost_center", "job_profile", "manager_name"
                ],
                "sample_file": "employee_sample_1.csv"
            },
            "successfactors": {
                "name": "Employee - SuccessFactors Format",
                "description": "SuccessFactors style employee data with userId and camelCase fields",
                "patterns": [
                    "userid", "firstname", "lastname", "hiredate",
                    "reportsto", "businessphone"
                ],
                "sample_file": "employee_sample_2.csv"
            },
            "standard": {
                "name": "Employee - Standard Format",
                "description": "Standard Eightfold employee schema format",
                "patterns": [
                    "employee_id", "first_name", "last_name",
                    "email", "hire_date", "title"
                ],
                "sample_file": None
            }
        }

        # Normalize source fields for comparison
        normalized_source = [self._normalize_field(f).lower() for f in source_fields]

        best_variant = None
        best_score = 0
        matched_patterns = []

        for variant_id, variant_info in employee_variants.items():
            score = 0
            current_patterns = []

            for pattern in variant_info["patterns"]:
                if pattern in normalized_source:
                    score += 1
                    current_patterns.append(pattern)

            # Calculate confidence as percentage of patterns matched
            confidence = score / len(variant_info["patterns"])

            if confidence > best_score:
                best_score = confidence
                best_variant = variant_info
                matched_patterns = current_patterns

        if best_variant and best_score > 0.3:  # At least 30% of patterns matched
            return {
                "variant": best_variant["name"],
                "description": best_variant["description"],
                "confidence": best_score,
                "matched_patterns": matched_patterns,
                "sample_file": best_variant["sample_file"]
            }
        else:
            return {
                "variant": "Employee - Standard Format",
                "description": "Standard employee format with mixed field patterns",
                "confidence": 0.5,
                "matched_patterns": matched_patterns,
                "sample_file": None
            }

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
