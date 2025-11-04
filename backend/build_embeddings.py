"""
Build Embeddings Script

Pre-computes vector embeddings for all entity schemas.
Run this once after adding new schemas or updating existing ones.

Usage:
    python build_embeddings.py
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.semantic_matcher import get_semantic_matcher


def main():
    """Build embeddings for all entities"""
    print("=" * 60)
    print("Building Vector Embeddings for Schema Fields")
    print("=" * 60)
    print()

    matcher = get_semantic_matcher()

    if not matcher.model:
        print("ERROR: sentence-transformers not available!")
        print("Install with: pip install sentence-transformers")
        return 1

    print(f"Using model: {matcher.model_name}")
    print()

    # Rebuild all embeddings
    matcher.rebuild_all_embeddings()

    print()
    print("=" * 60)
    print("Embeddings built successfully!")
    print(f"Stored in: {matcher.embeddings_dir}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
