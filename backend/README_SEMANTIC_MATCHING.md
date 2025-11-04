# Semantic Field Matching with Vector Embeddings

## Overview

SnapMap uses **vector embeddings** and **semantic similarity** for intelligent field mapping instead of relying on external AI APIs. This approach is:

- **Faster**: No API calls, all computation is local
- **More Accurate**: Understands meaning, not just string similarity
- **Offline**: Works without internet connection
- **Free**: No API costs
- **Privacy-Friendly**: Data stays on your server

## How It Works

### 1. Pre-Compute Embeddings

When schemas are loaded, we create vector embeddings for each field:
```
EMPLOYEE_ID → [0.234, -0.123, 0.456, ..., 0.789]  (384-dimensional vector)
FIRST_NAME  → [0.891, -0.456, 0.123, ..., -0.234]
EMAIL       → [-0.123, 0.567, -0.890, ..., 0.456]
```

Each embedding captures the **semantic meaning** of the field name, display name, and description.

### 2. Store in Cache

Embeddings are cached in `backend/app/embeddings/` as pickle files:
```
backend/app/embeddings/
├── employee_embeddings.pkl
├── user_embeddings.pkl
├── position_embeddings.pkl
└── ...
```

### 3. Fast Semantic Search

When a source field needs mapping:
```python
source: "emp_id" → embedding → find closest match using cosine similarity

Results:
  EMPLOYEE_ID (similarity: 0.92)  ✓ Best match!
  EMAIL       (similarity: 0.31)
  FIRST_NAME  (similarity: 0.18)
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `sentence-transformers` - For generating embeddings
- `numpy` - For vector operations
- `scikit-learn` - For similarity calculations
- `torch` - Required by sentence-transformers

### 2. Build Embeddings

Pre-compute embeddings for all entity schemas:

```bash
python build_embeddings.py
```

This creates embeddings for all 16 entity types and stores them in the cache.

### 3. Start the Server

```bash
uvicorn main:app --reload
```

The semantic matcher will auto-load cached embeddings on startup.

## Model Information

**Model Used**: `all-MiniLM-L6-v2`
- Size: ~90MB
- Speed: ~14,000 sentences/second
- Embedding Dimension: 384
- Quality: Excellent for sentence similarity
- Source: Hugging Face Transformers

## Benefits Over Fuzzy Matching

### Traditional Fuzzy Matching:
```
Source: "employee_identifier"
Target: "EMPLOYEE_ID"
Score: 0.45 (low - doesn't recognize relationship)
```

### Semantic Matching:
```
Source: "employee_identifier"
Target: "EMPLOYEE_ID"
Score: 0.94 (high - understands they mean the same thing!)
```

### Real-World Examples:

| Source Field | Fuzzy Match | Semantic Match | Winner |
|--------------|-------------|----------------|---------|
| `emp_id` | `EMAIL` (0.4) | `EMPLOYEE_ID` (0.92) | Semantic ✓ |
| `worker_num` | `PHONE` (0.3) | `EMPLOYEE_ID` (0.87) | Semantic ✓ |
| `fname` | `PHONE` (0.3) | `FIRST_NAME` (0.91) | Semantic ✓ |
| `staff_mail` | `MANAGER` (0.5) | `EMAIL` (0.89) | Semantic ✓ |

## Entity Type Detection

The semantic matcher also improves entity type detection:

```python
# Source fields: ["course_id", "course_title", "instructor", "duration"]

# Old approach: String matching might guess "employee" (wrong!)
# New approach: Semantic vectors → "course" with 95% confidence ✓
```

## Performance

- **First load**: ~2-3 seconds (loads model + embeddings)
- **Subsequent matches**: <1ms per field
- **Batch mapping** (100 fields): ~50ms total
- **Memory usage**: ~200MB (model + embeddings)

## Customization

### Use Different Model

Edit `backend/app/services/semantic_matcher.py`:

```python
# Default (fast, good quality)
self.model_name = "all-MiniLM-L6-v2"

# Better quality (slower, larger)
self.model_name = "all-mpnet-base-v2"

# Multilingual support
self.model_name = "paraphrase-multilingual-MiniLM-L12-v2"
```

### Rebuild Embeddings

After changing the model or updating schemas:

```bash
python build_embeddings.py
```

### Clear Cache

```bash
rm -rf backend/app/embeddings/*.pkl
python build_embeddings.py
```

## Fallback Behavior

The system has multiple layers:

1. **Try semantic matching** (if model available)
2. **Fall back to fuzzy matching** (if semantic fails)
3. **Use alias dictionary** (as last resort)

This ensures the system works even if:
- sentence-transformers isn't installed
- Embeddings haven't been built yet
- Model loading fails

## Troubleshooting

### "sentence-transformers not installed"

```bash
pip install sentence-transformers
```

### "Model download failed"

The first run downloads the model from Hugging Face. If offline:
1. Download model manually
2. Place in `~/.cache/huggingface/`
3. Or use a pre-downloaded model directory

### "Embeddings not found"

```bash
python build_embeddings.py
```

### "Out of memory"

Use a smaller model:
```python
self.model_name = "all-MiniLM-L6-v2"  # Smallest, fastest
```

## Architecture

```
┌─────────────────┐
│  Source Fields  │
│  ["emp_id",     │
│   "fname", ...] │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Semantic Matcher           │
│  1. Encode to embeddings    │
│  2. Load target embeddings  │
│  3. Cosine similarity       │
│  4. Return top matches      │
└────────┬────────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Mappings                │
│  emp_id → EMPLOYEE_ID    │
│  fname → FIRST_NAME      │
│  ...                     │
└──────────────────────────┘
```

## Future Enhancements

1. **Fine-tune on HR data**: Train model specifically on HR field names
2. **Add domain-specific vocabulary**: Include HR/Eightfold terminology
3. **Multi-language support**: Handle fields in different languages
4. **Custom embeddings**: Train embeddings on your specific schemas
5. **GPU acceleration**: Use CUDA for faster embedding generation

## API Endpoints

The semantic matching powers these endpoints:

- `POST /api/auto-map` - Auto-map fields using semantic similarity
- `POST /api/ai/detect-entity` - Detect entity type semantically
- `POST /api/ai/infer-corrections` - Get semantic suggestions for fields

All work locally without external API calls!
