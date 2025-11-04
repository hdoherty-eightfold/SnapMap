"""
Vector Database for Semantic Field Matching
Uses ChromaDB for efficient vector storage and similarity search

Much better than pickle files:
- Faster similarity search with built-in indexing
- Easy to update/add new schemas
- Persistent storage
- Production-ready
- No manual cache management
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")

from app.services.schema_manager import get_schema_manager


class VectorDatabase:
    """
    Vector database for semantic field matching using ChromaDB

    ChromaDB provides:
    - Automatic indexing for fast similarity search
    - Persistent storage (no manual caching)
    - Easy updates and queries
    - Production-ready performance
    """

    def __init__(self):
        self.schema_manager = get_schema_manager()
        self.db_path = Path(__file__).parent.parent.parent / "vector_db"
        self.db_path.mkdir(exist_ok=True)

        # Use lightweight model
        self.model_name = "all-MiniLM-L6-v2"
        self.model = None
        self._load_model()

        # Initialize ChromaDB
        self.client = None
        self._init_chromadb()

    def _load_model(self):
        """Load sentence transformer model"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return

        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"[OK] Loaded embedding model: {self.model_name}")
        except Exception as e:
            print(f"[ERROR] Error loading model: {e}")
            self.model = None

    def _init_chromadb(self):
        """Initialize ChromaDB client"""
        if not CHROMADB_AVAILABLE:
            print("ChromaDB not available, using fallback")
            return

        try:
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            print(f"[OK] ChromaDB initialized at {self.db_path}")
        except Exception as e:
            print(f"[ERROR] Error initializing ChromaDB: {e}")
            self.client = None

    def _get_collection_name(self, entity_name: str) -> str:
        """Get collection name for an entity"""
        return f"schema_{entity_name}"

    def _create_field_metadata(self, field_name: str, field_obj: any) -> Dict:
        """Create metadata for a field"""
        return {
            "field_name": field_name,
            "display_name": getattr(field_obj, 'display_name', field_name),
            "description": getattr(field_obj, 'description', ''),
            "required": str(getattr(field_obj, 'required', False)),
            "type": getattr(field_obj, 'type', 'string')
        }

    def _create_field_text(self, field_name: str, field_obj: any) -> str:
        """
        Create rich text representation of a field for embedding

        Combines field name, display name, and description for better matching
        """
        parts = [field_name]

        if hasattr(field_obj, 'display_name'):
            parts.append(field_obj.display_name)

        if hasattr(field_obj, 'description') and field_obj.description:
            parts.append(field_obj.description)

        # Add variations
        parts.append(field_name.replace('_', ' '))

        import re
        camel_split = re.sub('([A-Z])', r' \1', field_name).strip()
        if camel_split != field_name:
            parts.append(camel_split)

        return " | ".join(parts)

    def build_entity_collection(self, entity_name: str, force_rebuild: bool = False):
        """
        Build vector collection for an entity schema

        Args:
            entity_name: Entity name (e.g., 'employee', 'user')
            force_rebuild: Force rebuild even if collection exists
        """
        if not self.client or not self.model:
            print(f"[ERROR] Cannot build collection: ChromaDB or model not available")
            return

        collection_name = self._get_collection_name(entity_name)

        # Check if collection exists
        try:
            existing_collections = self.client.list_collections()
            collection_exists = any(c.name == collection_name for c in existing_collections)

            if collection_exists and not force_rebuild:
                print(f"[OK] Collection '{collection_name}' already exists")
                return

            if collection_exists and force_rebuild:
                self.client.delete_collection(collection_name)
                print(f"[OK] Deleted existing collection '{collection_name}'")

        except Exception as e:
            print(f"Warning: {e}")

        # Get schema
        try:
            schema = self.schema_manager.get_schema(entity_name)
        except Exception as e:
            print(f"[ERROR] Error loading schema for {entity_name}: {e}")
            return

        # Create collection
        collection = self.client.create_collection(
            name=collection_name,
            metadata={"entity_name": entity_name, "model": self.model_name}
        )

        # Prepare data for insertion
        documents = []
        metadatas = []
        ids = []

        for field in schema.fields:
            field_text = self._create_field_text(field.name, field)
            field_metadata = self._create_field_metadata(field.name, field)

            documents.append(field_text)
            metadatas.append(field_metadata)
            ids.append(f"{entity_name}_{field.name}")

        # Compute embeddings
        embeddings = self.model.encode(documents, show_progress_bar=False)

        # Add to collection
        collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"[OK] Built collection '{collection_name}' with {len(documents)} fields")

    def find_similar_fields(
        self,
        source_field: str,
        entity_name: str,
        top_k: int = 3,
        min_similarity: float = 0.3
    ) -> List[Dict]:
        """
        Find similar fields using vector similarity search

        Args:
            source_field: Source field name to match
            entity_name: Target entity type
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of matches with field info and similarity scores
        """
        if not self.client or not self.model:
            return []

        collection_name = self._get_collection_name(entity_name)

        try:
            collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"Collection '{collection_name}' not found: {e}")
            return []

        # Create source field text variations
        source_texts = [
            source_field,
            source_field.replace('_', ' '),
            source_field.replace('-', ' '),
        ]

        # Compute embedding for source field
        source_embedding = self.model.encode(source_texts, show_progress_bar=False)
        query_embedding = np.mean(source_embedding, axis=0)

        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        # Parse results
        matches = []
        if results['metadatas'] and results['distances']:
            for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0])):
                # Convert distance to similarity (ChromaDB uses L2 distance)
                # Normalize to 0-1 range (1 = identical, 0 = very different)
                similarity = 1 / (1 + distance)

                if similarity >= min_similarity:
                    matches.append({
                        'target_field': metadata['field_name'],
                        'similarity': float(similarity),
                        'display_name': metadata['display_name'],
                        'description': metadata['description'],
                        'required': metadata['required'] == 'True',
                        'type': metadata['type']
                    })

        return matches

    def map_fields_batch(
        self,
        source_fields: List[str],
        entity_name: str,
        min_confidence: float = 0.5
    ) -> List[Dict]:
        """
        Map multiple source fields to target fields

        Args:
            source_fields: List of source field names
            entity_name: Target entity type
            min_confidence: Minimum confidence threshold

        Returns:
            List of mappings with source, target, and confidence
        """
        mappings = []

        for source_field in source_fields:
            matches = self.find_similar_fields(
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
                    'match_method': 'vector_db'
                }
                mappings.append(mapping)
            else:
                mappings.append({
                    'source_field': source_field,
                    'target_field': None,
                    'confidence': 0.0,
                    'alternatives': [],
                    'match_method': 'none'
                })

        return mappings

    def build_all_collections(self, force_rebuild: bool = False):
        """Build collections for all available entities"""
        if not self.client or not self.model:
            print("[ERROR] Cannot build collections: ChromaDB or model not available")
            return

        entities = self.schema_manager.get_available_entities()
        print(f"\nBuilding vector collections for {len(entities)} entities...")
        print("=" * 60)

        for entity in entities:
            entity_id = entity['id']
            if self.schema_manager.entity_exists(entity_id):
                try:
                    self.build_entity_collection(entity_id, force_rebuild)
                except Exception as e:
                    print(f"[ERROR] Error building {entity_id}: {e}")

        print("=" * 60)
        print("[OK] Done building all collections!\n")

    def get_stats(self) -> Dict:
        """Get statistics about the vector database"""
        if not self.client:
            return {"status": "unavailable"}

        try:
            collections = self.client.list_collections()
            stats = {
                "status": "active",
                "total_collections": len(collections),
                "collections": []
            }

            for collection in collections:
                col_obj = self.client.get_collection(collection.name)
                count = col_obj.count()
                stats["collections"].append({
                    "name": collection.name,
                    "count": count,
                    "metadata": collection.metadata
                })

            return stats
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance
_vector_db = None


def get_vector_db() -> VectorDatabase:
    """Get singleton VectorDatabase instance"""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDatabase()
    return _vector_db


# Auto-initialize collections on first import
def initialize_vector_db():
    """Pre-build collections for common entities"""
    import threading

    def _build():
        try:
            vdb = get_vector_db()
            if vdb.client and vdb.model:
                # Check if any collections exist
                collections = vdb.client.list_collections()
                if len(collections) == 0:
                    print("No collections found, building...")
                    # Build for common entities
                    common_entities = ['employee', 'user', 'position', 'candidate']
                    for entity in common_entities:
                        if vdb.schema_manager.entity_exists(entity):
                            vdb.build_entity_collection(entity)
        except Exception as e:
            print(f"Background vector DB initialization: {e}")

    thread = threading.Thread(target=_build, daemon=True)
    thread.start()


# Auto-initialize
if CHROMADB_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE:
    initialize_vector_db()
