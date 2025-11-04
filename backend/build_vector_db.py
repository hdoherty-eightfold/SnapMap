"""
Build Vector Database Script

Builds ChromaDB collections for all entity schemas.
Run this once after adding new schemas or updating existing ones.

Usage:
    python build_vector_db.py [--rebuild]

Options:
    --rebuild    Force rebuild all collections even if they exist
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.vector_db import get_vector_db


def main():
    """Build vector database collections for all entities"""
    print("=" * 70)
    print("Building Vector Database Collections for Schema Fields")
    print("=" * 70)
    print()

    # Check for rebuild flag
    force_rebuild = '--rebuild' in sys.argv or '-r' in sys.argv

    vdb = get_vector_db()

    if not vdb.client:
        print("ERROR: ChromaDB not available!")
        print("Install with: pip install chromadb")
        return 1

    if not vdb.model:
        print("ERROR: sentence-transformers not available!")
        print("Install with: pip install sentence-transformers")
        return 1

    print(f"Using model: {vdb.model_name}")
    print(f"Database path: {vdb.db_path}")
    print(f"Force rebuild: {force_rebuild}")
    print()

    # Build all collections
    vdb.build_all_collections(force_rebuild=force_rebuild)

    # Show stats
    stats = vdb.get_stats()
    print("\n" + "=" * 70)
    print("Vector Database Statistics")
    print("=" * 70)
    print(f"Status: {stats['status']}")
    print(f"Total collections: {stats.get('total_collections', 0)}")
    print()

    if stats.get('collections'):
        print("Collections:")
        for col in stats['collections']:
            print(f"  - {col['name']}: {col['count']} fields")

    print()
    print("=" * 70)
    print("[SUCCESS] Vector database ready!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
