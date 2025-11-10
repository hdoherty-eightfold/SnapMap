"""
Enhanced Field Mapper with FREE Gemini Integration
100% FREE - No costs, all open source

This integrates your existing vector-based field mapper with Gemini reasoning
for ambiguous cases. Completely free using Google Gemini's free tier.

STACK (All FREE):
- Sentence Transformers: FREE (open source)
- ChromaDB: FREE (open source)
- Google Gemini Flash: FREE (1,500 requests/day)
- PostgreSQL: FREE (open source)
- Redis: FREE (open source)
"""

from typing import List, Dict, Optional
import os
from enum import Enum

from app.services.field_mapper import get_field_mapper
from app.services.semantic_matcher import get_semantic_matcher
from app.models.mapping import Mapping, Alternative
from app.models.schema import EntitySchema

try:
    from app.services.gemini_field_reasoner import get_gemini_reasoner
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ConfidenceTier(Enum):
    """Confidence tier thresholds"""
    HIGH = 0.85      # Auto-approve (alias/exact matches)
    MEDIUM = 0.70    # Vector similarity - good enough
    LOW = 0.40       # Trigger Gemini reasoning
    REJECT = 0.40    # Below this, reject


class EnhancedFieldMapper:
    """
    Three-tier field mapping with FREE Gemini reasoning

    TIER 1 (85-100%): Alias dictionary + exact matches → AUTO-APPROVE
    TIER 2 (70-85%): Vector semantic similarity → AUTO-APPROVE
    TIER 3 (40-70%): Gemini reasoning for ambiguous → BOOST CONFIDENCE
    TIER 4 (<40%): No match → MANUAL REVIEW

    100% FREE operation:
    - Uses Google Gemini Flash free tier (1,500 requests/day)
    - Typically only 5-10% of fields need Gemini (rest handled by vector)
    - Can process 150-300 files/day completely free
    """

    def __init__(self, gemini_api_keys: Optional[list] = None, enable_gemini: bool = True):
        """
        Initialize enhanced mapper

        Args:
            gemini_api_keys: List of Google Gemini API keys (or set GEMINI_API_KEY/GEMINI_API_KEY_2 env vars)
                            Can also be a single string key
            enable_gemini: Enable Gemini reasoning tier (default: True)
        """
        # Core mappers (always available)
        self.field_mapper = get_field_mapper()
        self.semantic_matcher = get_semantic_matcher()

        # Gemini reasoner (optional enhancement)
        self.gemini_reasoner = None
        self.enable_gemini = enable_gemini and GEMINI_AVAILABLE

        if self.enable_gemini:
            # Get API keys from parameter or environment
            if gemini_api_keys:
                if isinstance(gemini_api_keys, str):
                    api_keys = [gemini_api_keys]
                else:
                    api_keys = gemini_api_keys
            else:
                # Try to get keys from environment variables
                api_keys = []
                key1 = os.getenv('GEMINI_API_KEY')
                key2 = os.getenv('GEMINI_API_KEY_2')

                if key1:
                    api_keys.append(key1)
                if key2:
                    api_keys.append(key2)

            if api_keys:
                try:
                    self.gemini_reasoner = get_gemini_reasoner(api_keys)
                    print(f"[OK] Gemini reasoning enabled with {len(api_keys)} API key(s) (FREE tier)")
                except Exception as e:
                    print(f"[WARNING] Gemini initialization failed: {e}")
                    self.enable_gemini = False
            else:
                print("[WARNING] No GEMINI_API_KEY set - running in vector-only mode")
                self.enable_gemini = False

    def map_fields(
        self,
        source_fields: List[str],
        target_schema: EntitySchema,
        sample_data: Optional[Dict[str, List]] = None,
        min_confidence: float = 0.70
    ) -> Dict:
        """
        Enhanced multi-tier field mapping

        Args:
            source_fields: List of source field names
            target_schema: Target entity schema
            sample_data: Optional dict of {field_name: [sample_values]}
            min_confidence: Minimum confidence threshold

        Returns:
            {
                "mappings": [Mapping objects],
                "stats": {
                    "total_fields": 22,
                    "tier1_alias": 8,      # 85-100% confidence
                    "tier2_vector": 10,    # 70-85% confidence
                    "tier3_gemini": 2,     # 40-70% → boosted
                    "tier4_manual": 2,     # <40% → needs review
                    "auto_approved": 18,   # ≥70% total
                    "needs_review": 4,     # <70% total
                    "gemini_used": True,
                    "gemini_requests": 1   # Batch request for 2 fields
                }
            }
        """
        mappings = []
        used_targets = set()

        stats = {
            "total_fields": len(source_fields),
            "tier1_alias": 0,
            "tier2_vector": 0,
            "tier3_gemini": 0,
            "tier4_manual": 0,
            "gemini_requests": 0
        }

        # TIER 1: High-confidence alias/exact matches (85-100%)
        tier1_mappings = self._tier1_alias_matching(
            source_fields, target_schema, used_targets
        )
        mappings.extend(tier1_mappings)
        stats["tier1_alias"] = len(tier1_mappings)

        mapped_sources = {m.source for m in tier1_mappings}

        # TIER 2: Vector semantic matching (70-85%)
        unmapped = [f for f in source_fields if f not in mapped_sources]
        if unmapped:
            tier2_mappings, tier2_stats = self._tier2_vector_matching(
                unmapped, target_schema, used_targets, sample_data
            )
            mappings.extend(tier2_mappings)
            stats["tier2_vector"] = tier2_stats["high_confidence"]
            mapped_sources.update(m.source for m in tier2_mappings)

            # Track ambiguous fields for Tier 3
            ambiguous_fields = tier2_stats.get("ambiguous_fields", [])

            # TIER 3: Gemini reasoning for ambiguous fields (40-70%)
            if self.enable_gemini and self.gemini_reasoner and ambiguous_fields:
                tier3_mappings, gemini_count = self._tier3_gemini_reasoning(
                    ambiguous_fields, target_schema, used_targets, sample_data
                )
                mappings.extend(tier3_mappings)
                stats["tier3_gemini"] = len(tier3_mappings)
                stats["gemini_requests"] = gemini_count
                mapped_sources.update(m.source for m in tier3_mappings)

        # TIER 4: Unmapped fields (need manual review)
        still_unmapped = [f for f in source_fields if f not in mapped_sources]
        stats["tier4_manual"] = len(still_unmapped)

        # Add unmapped fields with low confidence (use empty string for target and 'manual' for method)
        for field in still_unmapped:
            mappings.append(Mapping(
                source=field,
                target="",  # Empty string instead of None for Pydantic validation
                confidence=0.0,
                method="manual",  # 'manual' is valid in Mapping model schema
                alternatives=None
            ))

        # Calculate summary stats
        auto_approved = [m for m in mappings if m.confidence >= min_confidence]
        needs_review = [m for m in mappings if m.confidence < min_confidence]

        stats.update({
            "auto_approved": len(auto_approved),
            "needs_review": len(needs_review),
            "auto_approval_rate": len(auto_approved) / len(source_fields) if source_fields else 0,
            "gemini_used": stats["gemini_requests"] > 0
        })

        # Sort by confidence (highest first)
        mappings.sort(key=lambda m: m.confidence, reverse=True)

        return {
            "mappings": mappings,
            "stats": stats
        }

    def _tier1_alias_matching(
        self,
        source_fields: List[str],
        target_schema: EntitySchema,
        used_targets: set
    ) -> List[Mapping]:
        """Tier 1: High-confidence alias/exact matching"""
        mappings = []

        for source in source_fields:
            match = self.field_mapper.get_best_match(
                source, target_schema.fields, used_targets
            )

            # Accept high-confidence matches (85%+)
            if match and match.confidence >= ConfidenceTier.HIGH.value:
                mappings.append(match)
                used_targets.add(match.target)

        return mappings

    def _tier2_vector_matching(
        self,
        source_fields: List[str],
        target_schema: EntitySchema,
        used_targets: set,
        sample_data: Optional[Dict[str, List]]
    ) -> tuple[List[Mapping], Dict]:
        """
        Tier 2: Vector semantic matching

        Returns:
            (mappings, stats_dict)
        """
        mappings = []
        ambiguous_fields = []
        high_confidence_count = 0

        for source in source_fields:
            matches = self.semantic_matcher.find_best_match(
                source,
                target_schema.entity_name,
                top_k=3,
                min_similarity=ConfidenceTier.LOW.value  # Lower threshold to catch ambiguous
            )

            if not matches:
                ambiguous_fields.append({
                    "source_field": source,
                    "candidates": [],
                    "sample_data": sample_data.get(source, []) if sample_data else []
                })
                continue

            best = matches[0]

            # Skip if target already used
            if best['target_field'] in used_targets:
                continue

            # High confidence (70-85%) - use vector match
            if best['similarity'] >= ConfidenceTier.MEDIUM.value:
                alternatives = [
                    Alternative(target=m['target_field'], confidence=m['similarity'])
                    for m in matches[1:3]
                    if m['target_field'] not in used_targets
                ]

                mappings.append(Mapping(
                    source=source,
                    target=best['target_field'],
                    confidence=best['similarity'],
                    method='vector',
                    alternatives=alternatives if alternatives else None
                ))
                used_targets.add(best['target_field'])
                high_confidence_count += 1

            # Ambiguous (40-70%) - flag for Gemini reasoning
            elif best['similarity'] >= ConfidenceTier.LOW.value:
                # Prepare for Gemini reasoning
                candidates = [
                    {
                        "name": m['target_field'],
                        "similarity": m['similarity'],
                        "description": m.get('description', '')
                    }
                    for m in matches
                    if m['target_field'] not in used_targets
                ]

                ambiguous_fields.append({
                    "source_field": source,
                    "candidates": candidates,
                    "sample_data": sample_data.get(source, []) if sample_data else []
                })

        stats = {
            "high_confidence": high_confidence_count,
            "ambiguous_fields": ambiguous_fields
        }

        return mappings, stats

    def _tier3_gemini_reasoning(
        self,
        ambiguous_fields: List[Dict],
        target_schema: EntitySchema,
        used_targets: set,
        sample_data: Optional[Dict]
    ) -> tuple[List[Mapping], int]:
        """
        Tier 3: Gemini reasoning for ambiguous fields

        Uses BATCH processing to minimize API calls (1 call for up to 10 fields)

        Returns:
            (mappings, gemini_request_count)
        """
        if not ambiguous_fields:
            return [], 0

        mappings = []
        request_count = 0

        # Batch process fields (up to 10 per batch to stay efficient)
        batch_size = 10
        for i in range(0, len(ambiguous_fields), batch_size):
            batch = ambiguous_fields[i:i + batch_size]

            try:
                # Single batch API call for multiple fields
                results = self.gemini_reasoner.batch_reason_fields(
                    batch,
                    entity_type=target_schema.entity_name
                )
                request_count += 1

                # Process results
                for field_info, result in zip(batch, results):
                    target = result.get("recommended_target")
                    confidence = result.get("confidence", 0.0)

                    # Only use if target is available and confidence is reasonable
                    if target and target not in used_targets and confidence >= 0.60:
                        # Get original vector candidates for alternatives
                        vector_alts = [
                            Alternative(target=c["name"], confidence=c["similarity"])
                            for c in field_info["candidates"][1:3]
                            if c["name"] not in used_targets and c["name"] != target
                        ]

                        mappings.append(Mapping(
                            source=field_info["source_field"],
                            target=target,
                            confidence=confidence,
                            method='semantic',  # Use 'semantic' (valid in Mapping model)
                            alternatives=vector_alts if vector_alts else None
                        ))
                        used_targets.add(target)

            except Exception as e:
                print(f"Gemini batch reasoning failed: {e}")
                # Fall back to vector matches for this batch
                for field_info in batch:
                    if field_info["candidates"]:
                        best = field_info["candidates"][0]
                        if best["name"] not in used_targets:
                            mappings.append(Mapping(
                                source=field_info["source_field"],
                                target=best["name"],
                                confidence=best["similarity"],
                                method='fuzzy',  # Use 'fuzzy' (valid in Mapping model)
                                alternatives=None
                            ))
                            used_targets.add(best["name"])

        return mappings, request_count

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        if self.gemini_reasoner:
            return self.gemini_reasoner.get_usage_stats()
        else:
            return {
                "gemini_enabled": False,
                "message": "Gemini not initialized"
            }


# Singleton instance
_enhanced_mapper = None


def get_enhanced_mapper(
    gemini_api_keys: Optional[list] = None,
    enable_gemini: bool = True
) -> EnhancedFieldMapper:
    """
    Get singleton enhanced mapper instance

    Args:
        gemini_api_keys: List of Google Gemini API keys (or set GEMINI_API_KEY/GEMINI_API_KEY_2 env vars)
                        Can also be a single string key
        enable_gemini: Enable Gemini reasoning tier
    """
    global _enhanced_mapper

    if _enhanced_mapper is None:
        _enhanced_mapper = EnhancedFieldMapper(
            gemini_api_keys=gemini_api_keys,
            enable_gemini=enable_gemini
        )

    return _enhanced_mapper
