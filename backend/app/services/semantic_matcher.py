"""
Semantic Field Matcher using Vector Embeddings
Uses sentence transformers and cosine similarity for fast, accurate field matching
No external API calls needed - all done locally
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from functools import lru_cache
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")

from app.services.schema_manager import get_schema_manager


class SemanticMatcher:
    """
    Vector-based semantic field matcher

    Uses pre-computed embeddings and cosine similarity for fast semantic search.
    Much faster and more accurate than fuzzy string matching or AI calls.
    """

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.embeddings_dir = Path(__file__).parent.parent / "embeddings"
        self.embeddings_dir.mkdir(exist_ok=True)

        # Use a lightweight model that works offline
        self.model_name = "all-MiniLM-L6-v2"  # Fast, 384-dim embeddings
        self.model = None
        self._load_model()

        # Cache for entity embeddings
        self.entity_embeddings_cache: Dict[str, Dict] = {}

    def _load_model(self):
        """Load the sentence transformer model"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return

        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def _get_cache_path(self, entity_name: str) -> Path:
        """Get path to cached embeddings for an entity"""
        return self.embeddings_dir / f"{entity_name}_embeddings.pkl"

    def _create_field_text(self, field_name: str, field_obj: any) -> List[str]:
        """
        Create multiple text representations of a field for embedding

        Returns list of texts to improve matching:
        - Field name
        - Display name
        - Description
        - Field name with underscores as spaces
        - Field name in camelCase split
        """
        texts = []

        # Original field name
        texts.append(field_name)

        # Display name if available
        if hasattr(field_obj, 'display_name'):
            texts.append(field_obj.display_name)

        # Description if available
        if hasattr(field_obj, 'description') and field_obj.description:
            texts.append(field_obj.description)

        # Field name variations
        # Underscore to spaces: "first_name" -> "first name"
        texts.append(field_name.replace('_', ' '))

        # Split camelCase: "firstName" -> "first name"
        import re
        camel_split = re.sub('([A-Z])', r' \1', field_name).strip()
        if camel_split != field_name:
            texts.append(camel_split)

        # Combine for rich context
        combined = f"{field_name} {getattr(field_obj, 'display_name', '')} {getattr(field_obj, 'description', '')}"
        texts.append(combined.strip())

        return texts

    def _compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for a list of texts"""
        if not self.model:
            # Fallback: return random embeddings (for testing without model)
            return np.random.randn(len(texts), 384)

        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings

    def build_entity_embeddings(self, entity_name: str, force_rebuild: bool = False) -> Dict:
        """
        Build and cache embeddings for all fields in an entity schema

        Returns:
            Dict with field_name -> embedding mapping
        """
        cache_path = self._get_cache_path(entity_name)

        # Check cache first
        if not force_rebuild and cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cached = pickle.load(f)
                    print(f"Loaded cached embeddings for {entity_name}")
                    return cached
            except Exception as e:
                print(f"Error loading cache: {e}, rebuilding...")

        # Build embeddings
        schema = self.schema_manager.get_schema(entity_name)
        embeddings_data = {
            'entity_name': entity_name,
            'model_name': self.model_name,
            'fields': {}
        }

        all_texts = []
        field_text_map = {}  # Maps text index to (field_name, text_type)

        for field in schema.fields:
            field_texts = self._create_field_text(field.name, field)
            field_text_map[field.name] = field_texts
            all_texts.extend(field_texts)

        # Compute all embeddings at once (much faster)
        if all_texts:
            all_embeddings = self._compute_embeddings(all_texts)

            # Map embeddings back to fields
            idx = 0
            for field in schema.fields:
                num_texts = len(field_text_map[field.name])
                field_embeddings = all_embeddings[idx:idx + num_texts]

                # Average the embeddings for this field
                avg_embedding = np.mean(field_embeddings, axis=0)

                embeddings_data['fields'][field.name] = {
                    'embedding': avg_embedding,
                    'display_name': field.display_name,
                    'description': field.description if hasattr(field, 'description') else '',
                    'required': field.required,
                    'type': field.type
                }

                idx += num_texts

        # Save to cache
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(embeddings_data, f)
            print(f"Cached embeddings for {entity_name}")
        except Exception as e:
            print(f"Error saving cache: {e}")

        return embeddings_data

    def load_entity_embeddings(self, entity_name: str) -> Dict:
        """Load or build embeddings for an entity"""
        if entity_name in self.entity_embeddings_cache:
            return self.entity_embeddings_cache[entity_name]

        embeddings = self.build_entity_embeddings(entity_name)
        self.entity_embeddings_cache[entity_name] = embeddings
        return embeddings

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def find_best_match(
        self,
        source_field: str,
        entity_name: str,
        top_k: int = 3,
        min_similarity: float = 0.3
    ) -> List[Dict]:
        """
        Find best matching target fields using semantic similarity

        Args:
            source_field: Source field name to match
            entity_name: Target entity type
            top_k: Number of top matches to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of matches sorted by similarity, each with:
            - target_field: Field name
            - similarity: Similarity score (0-1)
            - display_name: Human-readable name
            - description: Field description
            - required: Whether field is required
        """
        # Load entity embeddings
        entity_embeddings = self.load_entity_embeddings(entity_name)

        # Create source field texts
        source_texts = [
            source_field,
            source_field.replace('_', ' '),
            source_field.replace('-', ' '),
        ]

        # Compute source embedding
        source_embeddings = self._compute_embeddings(source_texts)
        source_embedding = np.mean(source_embeddings, axis=0)

        # Compute similarities with all target fields
        similarities = []
        for field_name, field_data in entity_embeddings['fields'].items():
            target_embedding = field_data['embedding']
            similarity = self.cosine_similarity(source_embedding, target_embedding)

            if similarity >= min_similarity:
                similarities.append({
                    'target_field': field_name,
                    'similarity': float(similarity),
                    'display_name': field_data['display_name'],
                    'description': field_data['description'],
                    'required': field_data['required'],
                    'type': field_data['type']
                })

        # Sort by similarity descending
        similarities.sort(key=lambda x: x['similarity'], reverse=True)

        return similarities[:top_k]

    def map_fields_batch(
        self,
        source_fields: List[str],
        entity_name: str,
        min_confidence: float = 0.5
    ) -> List[Dict]:
        """
        Map multiple source fields to target fields at once

        Args:
            source_fields: List of source field names
            entity_name: Target entity type
            min_confidence: Minimum confidence threshold

        Returns:
            List of mappings with best matches for each source field
        """
        mappings = []

        for source_field in source_fields:
            matches = self.find_best_match(
                source_field,
                entity_name,
                top_k=3,
                min_similarity=min_confidence
            )

            if matches:
                best_match = matches[0]
                mapping = {
                    'source_field': source_field,
                    'target_field': best_match['target_field'],
                    'confidence': best_match['similarity'],
                    'alternatives': matches[1:] if len(matches) > 1 else [],
                    'match_method': 'semantic'
                }
                mappings.append(mapping)
            else:
                # No good match found
                mappings.append({
                    'source_field': source_field,
                    'target_field': None,
                    'confidence': 0.0,
                    'alternatives': [],
                    'match_method': 'none'
                })

        return mappings

    def rebuild_all_embeddings(self):
        """Rebuild embeddings for all available entities"""
        entities = self.schema_manager.get_available_entities()

        print(f"Rebuilding embeddings for {len(entities)} entities...")
        for entity in entities:
            entity_id = entity['id']
            if self.schema_manager.entity_exists(entity_id):
                try:
                    self.build_entity_embeddings(entity_id, force_rebuild=True)
                    print(f"✓ Built embeddings for {entity_id}")
                except Exception as e:
                    print(f"✗ Error building embeddings for {entity_id}: {e}")

        print("Done rebuilding embeddings!")


# Singleton instance
_semantic_matcher = None


def get_semantic_matcher() -> SemanticMatcher:
    """Get singleton SemanticMatcher instance"""
    global _semantic_matcher
    if _semantic_matcher is None:
        _semantic_matcher = SemanticMatcher()
    return _semantic_matcher


# Initialize embeddings on first import (in background)
def initialize_embeddings():
    """Pre-build embeddings for common entities"""
    import threading

    def _build():
        try:
            matcher = get_semantic_matcher()
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                # Build embeddings for common entities
                common_entities = ['employee', 'user', 'position', 'candidate']
                for entity in common_entities:
                    if matcher.schema_manager.entity_exists(entity):
                        matcher.load_entity_embeddings(entity)
        except Exception as e:
            print(f"Background embedding initialization failed: {e}")

    # Run in background thread
    thread = threading.Thread(target=_build, daemon=True)
    thread.start()


# Auto-initialize on import
initialize_embeddings()
