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
        self.schemas_dir = Path(__file__).parent.parent / "schemas"
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
        min_confidence: float = None
    ) -> List[Mapping]:
        """
        Automatically map source fields to target fields using semantic matching

        Args:
            source_fields: List of source field names
            target_schema: Target entity schema
            min_confidence: Minimum confidence threshold (default: 0.70)

        Returns:
            List of Mapping objects sorted by confidence (highest first)
        """
        if min_confidence is not None:
            self.min_confidence = min_confidence

        # Try semantic matching first (much better!)
        if self.semantic_matcher and self.semantic_matcher.model:
            try:
                semantic_mappings = self.semantic_matcher.map_fields_batch(
                    source_fields,
                    target_schema.entity_name,
                    min_confidence=self.min_confidence
                )

                # Convert to Mapping objects
                mappings = []
                for sm in semantic_mappings:
                    if sm['target_field']:
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

                mappings.sort(key=lambda m: m.confidence, reverse=True)
                return mappings

            except Exception as e:
                print(f"Semantic mapping failed, falling back to fuzzy: {e}")

        # Fallback to traditional fuzzy matching
        mappings = []
        used_targets = set()

        for source_field in source_fields:
            best_match = self.get_best_match(
                source_field,
                target_schema.fields,
                used_targets
            )

            if best_match and best_match.confidence >= self.min_confidence:
                mappings.append(best_match)
                used_targets.add(best_match.target)

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
        Calculate match confidence and method

        Args:
            source: Source field name
            target: Target field name

        Returns:
            Tuple of (confidence, method)
            - confidence: 0.0 to 1.0
            - method: "exact" | "alias" | "fuzzy"
        """
        # Normalize strings for comparison
        source_norm = self._normalize(source)
        target_norm = self._normalize(target)

        # 1. Exact match (100% confidence)
        if source_norm == target_norm:
            return (1.0, "exact")

        # 2. Alias match (98% confidence)
        if target in self.alias_dictionary:
            aliases = [self._normalize(a) for a in self.alias_dictionary[target]]
            if source_norm in aliases:
                return (0.98, "alias")

        # 3. Fuzzy match using Levenshtein distance (70-97% confidence)
        similarity = self._levenshtein_similarity(source_norm, target_norm)

        if similarity >= 0.70:
            return (similarity, "fuzzy")

        return (0.0, "none")

    def _normalize(self, text: str) -> str:
        """
        Normalize field name for comparison

        Removes special characters, converts to lowercase
        """
        # Remove special characters (keep only alphanumeric)
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        # Convert to lowercase
        return text.lower()

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
