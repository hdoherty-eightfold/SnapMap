# Field Mapping Feature Specification

## Overview
AI-powered semantic field mapping with drag-and-drop interface for mapping source fields to Eightfold target schema.

## Components
- `frontend/src/components/mapping/FieldMapping.tsx`
- `frontend/src/components/mapping/ConnectionLines.tsx`
- `backend/app/api/endpoints/mapping.py`
- `backend/app/services/semantic_matching.py`

## Key Functionality
1. **Semantic Matching**: Vector-based similarity using sentence transformers
2. **Confidence Scoring**: 0-100% confidence scores for each mapping
3. **Manual Override**: Drag-and-drop interface for corrections
4. **Synonym Recognition**: Built-in alias dictionary (300+ HR field variations)
5. **Multi-Value Field Support**: Handles `||` separator (Siemens standard)
6. **Connection Visualization**: Visual lines showing field mappings

## AI/ML Components
- ChromaDB vector database for semantic embeddings
- Sentence transformer models for field similarity
- Confidence threshold algorithms

## API Endpoints
- `POST /mapping/auto-map` - Generate automatic field mappings
- `POST /mapping/manual` - Save manual mapping adjustments
- `GET /mapping/confidence/{field_id}` - Get confidence score for specific mapping

## Dependencies
- ChromaDB for vector storage
- Sentence-transformers for embeddings
- React DnD for drag-and-drop functionality
- SVG for connection line rendering

## Testing
**Location:** `backend/tests/features/mapping/`

**Test Files:**
- `test_field_mapping_accuracy.py` - Tests semantic matching accuracy (target: >75%)
- `test_enhanced_mapping.py` - Tests vector-based similarity algorithms
- `test_enhanced_mapper.py` - Tests confidence scoring and manual override functionality

**Test Coverage:**
- Semantic similarity accuracy (ChromaDB + sentence transformers)
- Confidence score validation (0-100% range)
- Manual mapping override functionality
- Synonym recognition (300+ HR field variations)
- Multi-value field detection and handling
- Connection line visualization

**Accuracy Metrics:**
- Target mapping accuracy: 75%+ (baseline: 13.64%)
- Confidence threshold: 70% for auto-mapping
- Manual correction rate: <25% of total mappings
- Processing time: <2 seconds for typical datasets

**Integration Tests:**
- End-to-end mapping workflow validation
- Vector database connectivity testing
- Performance testing with large schemas

## Performance Metrics
- Target accuracy: 75%+ automatic mapping success rate
- Processing time: <2 seconds for typical files
- Memory usage: Optimized for large datasets

## Error Handling
- Missing vector database
- Low confidence mappings
- Circular mapping detection
- Invalid field type mismatches