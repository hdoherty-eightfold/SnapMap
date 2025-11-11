"""
Field Mapper
Intelligent field mapping using semantic embeddings (primary) and fuzzy matching (fallback)
"""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Set, Tuple, Optional
from functools import lru_cache

from app.models.schema import EntitySchema, FieldDefinition
from app.models.mapping import Mapping, Alternative

try:
    from app.services.semantic_matcher import get_semantic_matcher
    SEMANTIC_MATCHING_AVAILABLE = True
except Exception:
    SEMANTIC_MATCHING_AVAILABLE = False


class FieldMapper:
    """
    Smart field mapper with semantic embeddings and fuzzy matching fallback

    Prioritizes semantic matching for better accuracy, falls back to fuzzy matching
    """

    def __init__(self):
        self.schemas_dir = Path(__file__).parent.parent.parent.parent / "docs" / "schemas" / "backend_schemas"
        self.alias_dictionary = self._load_aliases()
        self.min_confidence = 0.70  # Only suggest if 70%+ confidence

        # Load semantic matcher if available
        self.semantic_matcher = None
        if SEMANTIC_MATCHING_AVAILABLE:
            try:
                self.semantic_matcher = get_semantic_matcher()
            except Exception as e:
                print(f"Semantic matcher not available: {e}")

    def _load_aliases(self) -> Dict[str, List[str]]:
        """Load field name aliases from JSON file"""
        alias_file = self.schemas_dir / "field_aliases.json"

        if not alias_file.exists():
            return {}

        try:
            with open(alias_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load aliases: {e}")
            return {}

    def auto_map(
        self,
        source_fields: List[str],
        target_schema: EntitySchema,
        min_confidence: float = None,
        column_types: Optional[Dict[str, str]] = None
    ) -> List[Mapping]:
        """
        Automatically map source fields to target fields using hybrid approach

        Uses multi-stage matching:
        1. Alias/exact/partial matching (highest priority - 85-100% confidence)
        2. Semantic embedding matching (medium priority - 70-85% confidence)
        3. Fuzzy string matching (fallback - 70-84% confidence)

        Args:
            source_fields: List of source field names
            target_schema: Target entity schema
            min_confidence: Minimum confidence threshold (default: 0.70)
            column_types: Optional dict mapping column names to detected types (email, phone, date, etc.)

        Returns:
            List of Mapping objects sorted by confidence (highest first)
        """
        if min_confidence is not None:
            self.min_confidence = min_confidence

        column_types = column_types or {}
        mappings = []
        used_targets = set()

        # STAGE 1: Try enhanced fuzzy/alias matching first (most accurate for known patterns)
        for source_field in source_fields:
            best_match = self.get_best_match(
                source_field,
                target_schema.fields,
                used_targets
            )

            # Accept high-confidence matches (85%+) immediately
            if best_match and best_match.confidence >= 0.85:
                mappings.append(best_match)
                used_targets.add(best_match.target)

        # Track which source fields were mapped
        mapped_sources = {m.source for m in mappings}
        unmapped_sources = [f for f in source_fields if f not in mapped_sources]

        # STAGE 2: Try semantic matching for remaining unmapped fields
        if unmapped_sources and self.semantic_matcher and self.semantic_matcher.model:
            try:
                semantic_mappings = self.semantic_matcher.map_fields_batch(
                    unmapped_sources,
                    target_schema.entity_name,
                    min_confidence=self.min_confidence,
                    column_types=column_types  # Pass column types to semantic matcher
                )

                # Convert semantic mappings to Mapping objects
                for sm in semantic_mappings:
                    if sm['target_field'] and sm['target_field'] not in used_targets:
                        alternatives = [
                            Alternative(target=alt['target_field'], confidence=alt['similarity'])
                            for alt in sm.get('alternatives', [])
                        ]
                        mappings.append(Mapping(
                            source=sm['source_field'],
                            target=sm['target_field'],
                            confidence=sm['confidence'],
                            method='semantic',
                            alternatives=alternatives if alternatives else None
                        ))
                        used_targets.add(sm['target_field'])
                        mapped_sources.add(sm['source_field'])

            except Exception as e:
                print(f"Semantic mapping encountered error: {e}")

        # STAGE 3: Final pass - try lower confidence fuzzy matches for any remaining fields
        still_unmapped = [f for f in source_fields if f not in mapped_sources]
        for source_field in still_unmapped:
            best_match = self.get_best_match(
                source_field,
                target_schema.fields,
                used_targets
            )

            # Accept matches above minimum confidence threshold
            if best_match and best_match.confidence >= self.min_confidence:
                mappings.append(best_match)
                used_targets.add(best_match.target)

        # Sort by confidence (highest first)
        mappings.sort(key=lambda m: m.confidence, reverse=True)
        return mappings

    def get_best_match(
        self,
        source_field: str,
        target_fields: List[FieldDefinition],
        used_targets: Set[str]
    ) -> Optional[Mapping]:
        """
        Get best matching target field for a source field

        Args:
            source_field: Source field name
            target_fields: List of target field definitions
            used_targets: Set of already-used target field names

        Returns:
            Mapping object or None if no good match found
        """
        candidates = []

        for target_field in target_fields:
            if target_field.name in used_targets:
                continue

            # Calculate match confidence and method
            confidence, method = self.calculate_match(
                source_field,
                target_field.name
            )

            if confidence > 0:
                candidates.append({
                    "target": target_field.name,
                    "confidence": confidence,
                    "method": method
                })

        if not candidates:
            return None

        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x["confidence"], reverse=True)

        # Get top 3 alternatives (excluding the best match)
        alternatives = [
            Alternative(target=c["target"], confidence=c["confidence"])
            for c in candidates[1:4]
        ]

        return Mapping(
            source=source_field,
            target=candidates[0]["target"],
            confidence=candidates[0]["confidence"],
            method=candidates[0]["method"],
            alternatives=alternatives if alternatives else None
        )

    def calculate_match(
        self,
        source: str,
        target: str
    ) -> Tuple[float, str]:
        """
        Calculate match confidence and method using multi-stage priority-based matching

        Priority order:
        1. Exact match (100% confidence)
        2. Alias dictionary lookup (95% confidence)
        3. Substring/partial matching (85-90% confidence)
        4. Fuzzy string matching (70-84% confidence)

        Args:
            source: Source field name
            target: Target field name

        Returns:
            Tuple of (confidence, method)
            - confidence: 0.0 to 1.0
            - method: "exact" | "alias" | "partial" | "fuzzy"
        """
        # Normalize strings for comparison
        source_norm = self.normalize_field_name(source)
        target_norm = self.normalize_field_name(target)

        # STAGE 1: Exact match (100% confidence)
        if source_norm == target_norm:
            return (1.0, "exact")

        # STAGE 2: Alias dictionary lookup (95% confidence)
        if target in self.alias_dictionary:
            # Normalize all aliases for comparison
            aliases_norm = [self.normalize_field_name(a) for a in self.alias_dictionary[target]]
            if source_norm in aliases_norm:
                return (0.95, "alias")

        # STAGE 3: Partial/Substring matching (85-90% confidence)
        # Handles cases like:
        # - "PersonID" contains "ID" -> matches "CANDIDATE_ID"
        # - "WorkEmails" contains "Email" -> matches "EMAIL"
        partial_score = self._calculate_partial_match(source_norm, target_norm)
        if partial_score > 0:
            return (partial_score, "partial")

        # STAGE 4: Enhanced alias matching with partial overlap
        # Check if source matches any alias substring
        if target in self.alias_dictionary:
            for alias in self.alias_dictionary[target]:
                alias_norm = self.normalize_field_name(alias)
                partial_alias_score = self._calculate_partial_match(source_norm, alias_norm)
                if partial_alias_score >= 0.85:
                    # Adjust confidence slightly lower for partial alias match
                    return (min(partial_alias_score - 0.05, 0.93), "alias_partial")

        # STAGE 5: Fuzzy match using Levenshtein distance (70-84% confidence)
        similarity = self._levenshtein_similarity(source_norm, target_norm)

        if similarity >= 0.70:
            # Cap fuzzy matching at 0.84 to prioritize other methods
            return (min(similarity, 0.84), "fuzzy")

        return (0.0, "none")

    def _calculate_partial_match(self, source: str, target: str) -> float:
        """
        Calculate partial/substring match confidence

        Handles compound field names like:
        - "personid" vs "candidateid" (both contain "id")
        - "workemails" vs "email" ("email" is substring)

        Args:
            source: Normalized source field name
            target: Normalized target field name

        Returns:
            Confidence score (0.0 to 0.90)
        """
        if not source or not target:
            return 0.0

        # Direct substring match
        if source in target or target in source:
            # Calculate confidence based on length ratio
            min_len = min(len(source), len(target))
            max_len = max(len(source), len(target))
            ratio = min_len / max_len

            # High confidence for good substring matches
            if ratio >= 0.6:  # e.g., "email" in "workemails" (5/10 = 0.5)
                return 0.85 + (ratio * 0.05)  # 0.85 to 0.90

        # Check for common suffix/prefix patterns
        # e.g., "personid" and "candidateid" both end with "id"
        common_suffixes = ["id", "name", "email", "phone", "date", "time", "timestamp", "ts", "url", "location"]
        for suffix in common_suffixes:
            if source.endswith(suffix) and target.endswith(suffix):
                # Both end with same meaningful suffix
                return 0.82

        # Check for common word components
        # Split camelCase and extract words
        source_words = self._extract_words(source)
        target_words = self._extract_words(target)

        if source_words and target_words:
            # Calculate word overlap
            common_words = source_words.intersection(target_words)
            if common_words:
                overlap_ratio = len(common_words) / max(len(source_words), len(target_words))
                if overlap_ratio >= 0.5:
                    return 0.80 + (overlap_ratio * 0.05)

        return 0.0

    def _extract_words(self, text: str) -> Set[str]:
        """
        Extract meaningful word components from a field name

        Examples:
        - "workemails" -> {"work", "email", "emails"}
        - "personid" -> {"person", "id"}
        - "lastactivitytimestamp" -> {"last", "activity", "time", "timestamp"}

        Args:
            text: Normalized field name

        Returns:
            Set of extracted words
        """
        words = set()

        # Common word patterns in field names
        patterns = [
            "work", "home", "business", "personal", "primary", "secondary",
            "first", "last", "middle", "full", "legal",
            "email", "emails", "phone", "phones", "address",
            "name", "id", "number", "code", "key",
            "date", "time", "timestamp", "ts", "datetime",
            "activity", "modified", "updated", "created",
            "person", "candidate", "employee", "user", "staff", "worker",
            "location", "office", "site", "city", "country",
            "title", "position", "role", "job",
            "status", "state", "stage",
            "url", "link", "website"
        ]

        # Check for each pattern in the text
        for pattern in patterns:
            if pattern in text:
                words.add(pattern)

        return words

    def _normalize(self, text: str) -> str:
        """
        Normalize field name for comparison

        Removes special characters, converts to lowercase
        """
        # Remove special characters (keep only alphanumeric)
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        # Convert to lowercase
        return text.lower()

    def normalize_field_name(self, text: str) -> str:
        """
        Advanced normalization for field name matching

        Handles multi-word variations:
        - "WorkEmails" -> "workemails"
        - "Work_Emails" -> "workemails"
        - "work-emails" -> "workemails"
        - "WORK EMAILS" -> "workemails"

        Args:
            text: Field name to normalize

        Returns:
            Normalized field name (lowercase, no separators)
        """
        if not text:
            return ""

        # Convert to lowercase
        normalized = text.lower()

        # Remove all separators: underscores, hyphens, spaces
        normalized = re.sub(r'[_\-\s]+', '', normalized)

        # Remove any remaining special characters
        normalized = re.sub(r'[^a-z0-9]', '', normalized)

        return normalized

    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate Levenshtein similarity (0.0 to 1.0)

        Uses Python's built-in SequenceMatcher for efficient calculation
        """
        if not s1 or not s2:
            return 0.0

        return SequenceMatcher(None, s1, s2).ratio()


# Singleton instance
_field_mapper = None


def get_field_mapper() -> FieldMapper:
    """Get singleton FieldMapper instance"""
    global _field_mapper
    if _field_mapper is None:
        _field_mapper = FieldMapper()
    return _field_mapper
