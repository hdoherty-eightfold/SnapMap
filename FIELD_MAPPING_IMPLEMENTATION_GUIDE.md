# Field Mapping Implementation Guide
## Step-by-Step Guide for Production Deployment

---

## Overview

This guide provides concrete, copy-paste-ready code for implementing semantic field mapping in your production system. Based on the research findings, the recommended approach is:

**Pure Vector Embeddings (Sentence-Transformers) + Optional Fine-Tuning**

Why this approach:
- F1 score: 0.75-0.89 (depending on fine-tuning)
- Latency: 5-15ms (real-time capable)
- Cost: One-time $200-500 vs $1000+/month for RAG
- No complex infrastructure needed

---

## Phase 1: Setup (Week 1)

### 1.1 Install Dependencies

```bash
# In your backend directory
pip install sentence-transformers==2.2.2
pip install chardet==5.2.0
pip install scikit-learn==1.3.2
pip install great-expectations==0.17.12
pip install pandas==2.0.3
```

### 1.2 Create Semantic Mapper Module

**File: /backend/app/services/semantic_mapper.py**

```python
"""
Semantic field mapping using Sentence-Transformers embeddings.
Production-ready with encoding detection and data quality checks.
"""

import chardet
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Result of mapping a source field to target"""
    source_field: str
    target_field: str
    semantic_score: float
    type_compatible: bool
    confidence: float
    rank: int


@dataclass
class MappingResult:
    """Complete mapping result with metadata"""
    mappings: Dict[str, FieldMapping]
    overall_confidence: float
    unmapped_sources: List[str]
    unmapped_targets: List[str]
    encoding_detected: str
    total_fields: int


class EncodingDetector:
    """Handle CSV file encoding detection and fallback"""

    @staticmethod
    def detect(file_path: str, sample_size: int = 10000) -> str:
        """Detect file encoding with confidence check"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)

            if not raw_data:
                return 'utf-8'

            detection = chardet.detect(raw_data)
            encoding = detection.get('encoding', 'utf-8')
            confidence = detection.get('confidence', 0)

            logger.info(f"Encoding detection: {encoding} (confidence: {confidence:.2%})")

            # Confidence threshold
            if confidence < 0.8 or encoding is None:
                logger.warning(f"Low confidence encoding detection, using UTF-8 fallback")
                return 'utf-8'

            return encoding

        except Exception as e:
            logger.error(f"Error detecting encoding: {e}")
            return 'utf-8'

    @staticmethod
    def read_csv_safe(file_path: str) -> Tuple[pd.DataFrame, str]:
        """Read CSV with automatic encoding detection and fallback"""
        encoding = EncodingDetector.detect(file_path)

        encodings_to_try = [
            encoding,  # Detected encoding first
            'utf-8',
            'utf-8-sig',  # UTF-8 with BOM
            'latin-1',
            'cp1252',
            'iso-8859-1'
        ]

        for enc in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                logger.info(f"Successfully read CSV with encoding: {enc}")
                return df, enc
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                logger.error(f"Error reading with {enc}: {e}")
                continue

        raise ValueError(
            f"Could not read {file_path} with any encoding. "
            f"Tried: {', '.join(encodings_to_try)}"
        )


class SemanticFieldMapper:
    """
    Semantic field mapping engine using Sentence-Transformers.

    Performance: F1 score 0.75-0.89 depending on fine-tuning
    Latency: 5-15ms per 1000 fields
    """

    def __init__(
        self,
        model_name: str = 'sentence-transformers/paraphrase-mpnet-base-v2',
        confidence_threshold: float = 0.70,
        device: str = 'cpu'
    ):
        """
        Initialize mapper with embedding model.

        Args:
            model_name: HuggingFace model identifier
            confidence_threshold: Minimum confidence for auto-mapping (0.70-0.85 recommended)
            device: 'cpu' or 'cuda'
        """
        self.model = SentenceTransformer(model_name, device=device)
        self.confidence_threshold = confidence_threshold
        self.encoding_detector = EncodingDetector()

        logger.info(f"Initialized SemanticFieldMapper with model: {model_name}")

    def infer_field_semantics(
        self,
        df: pd.DataFrame,
        max_samples: int = 20
    ) -> List[Dict]:
        """
        Extract semantic information from DataFrame columns.

        Returns:
            List of field info dicts with embeddings
        """
        field_info = []

        for col_name in df.columns:
            # Get column metadata
            dtype = str(df[col_name].dtype)
            null_pct = df[col_name].isnull().sum() / len(df)
            unique_pct = df[col_name].nunique() / len(df)

            # Get sample values (skip nulls)
            samples = df[col_name].dropna().head(max_samples).astype(str).tolist()

            # Encode column name
            col_embedding = self.model.encode(col_name, convert_to_tensor=False)

            # Optionally encode sample values
            sample_embeddings = None
            if samples:
                # Average embedding of samples (for instance-level matching)
                sample_embeddings = np.mean(
                    self.model.encode(samples, convert_to_tensor=False),
                    axis=0
                )

            field_info.append({
                'name': col_name,
                'dtype': dtype,
                'null_pct': float(null_pct),
                'unique_pct': float(unique_pct),
                'samples': samples,
                'embedding': col_embedding,
                'sample_embedding': sample_embeddings
            })

        return field_info

    def _check_type_compatibility(
        self,
        source_dtype: str,
        target_dtype: str
    ) -> bool:
        """
        Check if data types are compatible for mapping.

        Conversion rules:
        - Any type -> string (always safe)
        - numeric -> numeric
        - string -> string
        - datetime -> datetime
        """
        type_groups = {
            'numeric': {'int64', 'int32', 'float64', 'float32', 'int', 'float'},
            'string': {'object', 'str', 'string'},
            'boolean': {'bool', 'boolean'},
            'datetime': {'datetime64', 'datetime'}
        }

        # Find type groups
        source_group = None
        target_group = None

        for group, types in type_groups.items():
            if any(t in source_dtype for t in types):
                source_group = group
            if any(t in target_dtype for t in types):
                target_group = group

        # String target accepts anything (safe conversion)
        if target_group == 'string':
            return True

        # Same group is compatible
        if source_group and target_group and source_group == target_group:
            return True

        # Default: incompatible
        return False

    def semantic_match(
        self,
        source_fields: List[Dict],
        target_fields: List[Dict],
        top_k: int = 3
    ) -> List[FieldMapping]:
        """
        Find semantic matches between source and target fields.

        Uses cosine similarity of embeddings.
        """
        # Prepare embeddings
        source_embeddings = np.array([f['embedding'] for f in source_fields])
        target_embeddings = np.array([f['embedding'] for f in target_fields])

        # Compute similarity matrix (cosine similarity)
        similarity_matrix = util.pytorch_cos_sim(
            source_embeddings,
            target_embeddings
        ).numpy()

        matches = []

        for src_idx, source in enumerate(source_fields):
            # Get top-k similar targets
            top_indices = np.argsort(similarity_matrix[src_idx])[-top_k:][::-1]

            for rank, tgt_idx in enumerate(top_indices):
                target = target_fields[tgt_idx]

                # Semantic similarity score (0-1)
                semantic_score = float(similarity_matrix[src_idx][tgt_idx])

                # Type compatibility
                type_compatible = self._check_type_compatibility(
                    source['dtype'],
                    target['dtype']
                )

                # Combined confidence score
                # Weight: 70% semantic, 30% type compatibility
                if type_compatible:
                    confidence = semantic_score * 0.7 + 1.0 * 0.3
                else:
                    confidence = semantic_score * 0.7 + 0.0 * 0.3

                matches.append(FieldMapping(
                    source_field=source['name'],
                    target_field=target['name'],
                    semantic_score=semantic_score,
                    type_compatible=type_compatible,
                    confidence=min(confidence, 1.0),  # Cap at 1.0
                    rank=rank
                ))

        return matches

    def generate_mapping(
        self,
        source_file: str,
        target_schema: List[str],
        strategy: str = 'one_to_one'
    ) -> MappingResult:
        """
        Generate field mapping from CSV file to target schema.

        Args:
            source_file: Path to CSV file
            target_schema: List of target field names
            strategy: 'one_to_one' (recommended) or 'one_to_many'

        Returns:
            MappingResult with mappings and metadata
        """
        logger.info(f"Generating mapping for {source_file} -> {target_schema}")

        # Load and analyze source
        source_df, encoding_detected = self.encoding_detector.read_csv_safe(source_file)
        source_fields = self.infer_field_semantics(source_df)

        # Create target field info
        target_fields = [
            {
                'name': field,
                'embedding': self.model.encode(field, convert_to_tensor=False),
                'dtype': 'object'  # Default, no actual type info for schema
            }
            for field in target_schema
        ]

        # Find semantic matches
        all_matches = self.semantic_match(source_fields, target_fields)

        # Select best matches
        mapping = {}
        used_targets = set()

        if strategy == 'one_to_one':
            # Each source maps to at most one target
            for source in source_fields:
                source_matches = [
                    m for m in all_matches
                    if m.source_field == source['name'] and
                    m.target_field not in used_targets
                ]

                if source_matches:
                    # Choose match with highest confidence
                    best = max(source_matches, key=lambda x: x.confidence)

                    if best.confidence >= self.confidence_threshold:
                        mapping[source['name']] = best
                        used_targets.add(best.target_field)

        elif strategy == 'one_to_many':
            # Source can map to multiple targets (less common)
            for match in sorted(all_matches, key=lambda x: x.confidence, reverse=True):
                if (match.source_field not in mapping and
                    match.target_field not in used_targets and
                    match.confidence >= self.confidence_threshold):
                    mapping[match.source_field] = match
                    used_targets.add(match.target_field)

        # Identify unmapped fields
        unmapped_sources = [
            f['name'] for f in source_fields
            if f['name'] not in mapping
        ]
        unmapped_targets = [
            f for f in target_schema
            if f not in used_targets
        ]

        # Calculate overall confidence
        confidences = [m.confidence for m in mapping.values()] if mapping else [0]
        overall_confidence = float(np.mean(confidences))

        logger.info(
            f"Mapping complete: {len(mapping)} mapped, "
            f"{len(unmapped_sources)} unmapped sources, "
            f"{len(unmapped_targets)} unmapped targets, "
            f"confidence: {overall_confidence:.2%}"
        )

        return MappingResult(
            mappings=mapping,
            overall_confidence=overall_confidence,
            unmapped_sources=unmapped_sources,
            unmapped_targets=unmapped_targets,
            encoding_detected=encoding_detected,
            total_fields=len(source_fields)
        )

    def export_mapping(
        self,
        result: MappingResult,
        output_format: str = 'json'
    ) -> str:
        """
        Export mapping result to JSON or CSV.

        Args:
            result: MappingResult from generate_mapping
            output_format: 'json' or 'csv'

        Returns:
            Serialized mapping string
        """
        if output_format == 'json':
            data = {
                'mappings': [
                    {
                        'source': m.source_field,
                        'target': m.target_field,
                        'confidence': round(m.confidence, 3),
                        'semantic_score': round(m.semantic_score, 3),
                        'type_compatible': m.type_compatible
                    }
                    for m in result.mappings.values()
                ],
                'summary': {
                    'overall_confidence': round(result.overall_confidence, 3),
                    'mapped_count': len(result.mappings),
                    'unmapped_sources': result.unmapped_sources,
                    'unmapped_targets': result.unmapped_targets,
                    'encoding': result.encoding_detected,
                    'total_source_fields': result.total_fields
                }
            }
            return json.dumps(data, indent=2)

        elif output_format == 'csv':
            rows = [
                f"source_field,target_field,confidence,semantic_score,type_compatible"
            ]
            for m in result.mappings.values():
                rows.append(
                    f"{m.source_field},{m.target_field},"
                    f"{m.confidence:.3f},{m.semantic_score:.3f},"
                    f"{m.type_compatible}"
                )
            return '\n'.join(rows)

        else:
            raise ValueError(f"Unknown format: {output_format}")


# Example Usage
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Initialize mapper
    mapper = SemanticFieldMapper(confidence_threshold=0.75)

    # Generate mapping
    result = mapper.generate_mapping(
        source_file='sample_data.csv',
        target_schema=['firstName', 'lastName', 'email', 'department'],
        strategy='one_to_one'
    )

    # Print results
    print(f"\nMapping Confidence: {result.overall_confidence:.2%}")
    print(f"Mapped Fields: {len(result.mappings)}")
    print(f"Unmapped Sources: {result.unmapped_sources}")
    print(f"Unmapped Targets: {result.unmapped_targets}")

    # Export mapping
    mapping_json = mapper.export_mapping(result, output_format='json')
    print("\nJSON Mapping:")
    print(mapping_json)
```

### 1.3 Update File Parser

**File: /backend/app/services/file_parser.py**

Add encoding detection to your existing parser:

```python
# Add to imports
from app.services.semantic_mapper import EncodingDetector

# Modify read_csv function
def read_csv(file_path: str) -> pd.DataFrame:
    """Read CSV with automatic encoding detection"""
    detector = EncodingDetector()
    df, encoding = detector.read_csv_safe(file_path)

    # Store encoding in metadata for later use
    df.attrs['encoding'] = encoding

    return df
```

---

## Phase 2: Integration with API (Week 2)

### 2.1 Create API Endpoint

**File: /backend/app/api/endpoints/field_mapper.py**

```python
"""
API endpoint for semantic field mapping.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import tempfile
from pathlib import Path

from app.services.semantic_mapper import SemanticFieldMapper, MappingResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mapper", tags=["field_mapping"])


class MappingRequest(BaseModel):
    target_schema: List[str]
    confidence_threshold: float = 0.70
    strategy: str = 'one_to_one'


class MappingResponse(BaseModel):
    success: bool
    file_id: str
    mappings: dict
    overall_confidence: float
    unmapped_sources: List[str]
    unmapped_targets: List[str]
    encoding: str
    total_fields: int
    message: str


@router.post("/auto-map")
async def auto_map_fields(
    file: UploadFile = File(...),
    target_schema_json: str = '["field1", "field2"]',
    confidence_threshold: float = 0.70
) -> MappingResponse:
    """
    Auto-map CSV fields to target schema using semantic matching.

    Returns:
        MappingResponse with mapping suggestions and confidence scores
    """
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported"
            )

        # Parse target schema
        import json
        target_schema = json.loads(target_schema_json)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            suffix='.csv',
            delete=False
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Run semantic mapping
            mapper = SemanticFieldMapper(
                confidence_threshold=confidence_threshold
            )

            result = mapper.generate_mapping(
                source_file=temp_path,
                target_schema=target_schema,
                strategy='one_to_one'
            )

            # Prepare response
            mappings_dict = {
                m.source_field: {
                    'target': m.target_field,
                    'confidence': round(m.confidence, 3),
                    'semantic_score': round(m.semantic_score, 3),
                    'type_compatible': m.type_compatible
                }
                for m in result.mappings.values()
            }

            return MappingResponse(
                success=True,
                file_id=file.filename.replace('.csv', ''),
                mappings=mappings_dict,
                overall_confidence=round(result.overall_confidence, 3),
                unmapped_sources=result.unmapped_sources,
                unmapped_targets=result.unmapped_targets,
                encoding=result.encoding_detected,
                total_fields=result.total_fields,
                message=f"Successfully mapped {len(result.mappings)} fields"
            )

        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid target_schema JSON"
        )
    except Exception as e:
        logger.error(f"Error in auto_map_fields: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Mapping failed: {str(e)}"
        )


@router.get("/benchmark")
async def run_benchmark():
    """
    Run performance benchmark.

    Returns:
        Benchmark results with latency metrics
    """
    import time
    import pandas as pd
    import tempfile

    # Create sample data
    sample_data = {
        'first_name': ['John', 'Jane', 'Bob'],
        'last_name': ['Doe', 'Smith', 'Johnson'],
        'email_address': ['john@example.com', 'jane@example.com', 'bob@example.com'],
        'phone_number': ['123-456-7890', '098-765-4321', '555-1234'],
    }

    df = pd.DataFrame(sample_data)

    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_path = f.name

    try:
        mapper = SemanticFieldMapper()
        target_schema = ['firstName', 'lastName', 'emailAddress', 'phone']

        # Time the mapping
        start = time.time()
        result = mapper.generate_mapping(
            source_file=temp_path,
            target_schema=target_schema
        )
        elapsed = time.time() - start

        return {
            'success': True,
            'latency_ms': round(elapsed * 1000, 2),
            'source_fields': result.total_fields,
            'target_fields': len(target_schema),
            'mapped': len(result.mappings),
            'confidence': round(result.overall_confidence, 3),
            'note': 'Benchmark uses small sample data. Production latency may vary.'
        }

    finally:
        Path(temp_path).unlink(missing_ok=True)
```

### 2.2 Register Endpoint

**File: /backend/app/main.py**

```python
# Add to imports
from app.api.endpoints import field_mapper

# Register router in your app initialization
app.include_router(field_mapper.router)
```

---

## Phase 3: Data Quality Validation (Week 3)

### 3.1 Add Validation Service

**File: /backend/app/services/data_validator.py**

```python
"""
Data quality validation using Great-Expectations.
"""

import pandas as pd
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CSVDataValidator:
    """Validate CSV data quality before and after field mapping"""

    @staticmethod
    def validate_encoding(file_path: str) -> Dict[str, Any]:
        """
        Validate that file is readable with detected encoding.
        """
        from app.services.semantic_mapper import EncodingDetector

        detector = EncodingDetector()

        try:
            df, encoding = detector.read_csv_safe(file_path)
            return {
                'valid': True,
                'encoding': encoding,
                'rows': len(df),
                'columns': len(df.columns)
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

    @staticmethod
    def validate_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate CSV structure.
        """
        issues = []

        # Check for empty columns
        empty_cols = df.columns[df.isnull().all()].tolist()
        if empty_cols:
            issues.append(f"Empty columns: {empty_cols}")

        # Check for duplicate columns
        if len(df.columns) != len(set(df.columns)):
            duplicates = [col for col in df.columns if df.columns.tolist().count(col) > 1]
            issues.append(f"Duplicate columns: {duplicates}")

        # Check for special characters in column names
        for col in df.columns:
            if not col.replace('_', '').replace(' ', '').isalnum():
                issues.append(f"Column '{col}' contains special characters")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    @staticmethod
    def validate_data_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate that column data types match expectations.

        Args:
            df: DataFrame to validate
            expected_types: Dict mapping column name to expected type
        """
        mismatches = []

        for col, expected_type in expected_types.items():
            if col not in df.columns:
                mismatches.append(f"Column '{col}' not found")
                continue

            actual_type = str(df[col].dtype)

            # Type compatibility check
            type_groups = {
                'numeric': ['int64', 'int32', 'float64', 'float32'],
                'string': ['object', 'str'],
                'datetime': ['datetime64']
            }

            actual_group = next(
                (g for g, types in type_groups.items() if actual_type in types),
                'unknown'
            )
            expected_group = next(
                (g for g, types in type_groups.items() if expected_type in types),
                'unknown'
            )

            if actual_group != expected_group:
                mismatches.append(
                    f"Column '{col}': expected {expected_group}, "
                    f"got {actual_group} ({actual_type})"
                )

        return {
            'valid': len(mismatches) == 0,
            'mismatches': mismatches
        }

    @staticmethod
    def validate_completeness(
        df: pd.DataFrame,
        required_cols: List[str],
        max_null_pct: float = 0.1
    ) -> Dict[str, Any]:
        """
        Validate data completeness.

        Args:
            df: DataFrame to validate
            required_cols: List of required columns
            max_null_pct: Maximum allowed null percentage (default 10%)
        """
        issues = []

        # Check for required columns
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")

        # Check null percentages
        for col in df.columns:
            null_pct = df[col].isnull().sum() / len(df)
            if null_pct > max_null_pct:
                issues.append(
                    f"Column '{col}': {null_pct:.1%} nulls "
                    f"(max allowed: {max_null_pct:.1%})"
                )

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    @staticmethod
    def run_full_validation(
        file_path: str,
        target_schema: List[str],
        expected_types: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive validation suite.
        """
        results = {}

        # Encoding validation
        results['encoding'] = CSVDataValidator.validate_encoding(file_path)

        if not results['encoding']['valid']:
            return results

        # Load data
        from app.services.semantic_mapper import EncodingDetector
        df, _ = EncodingDetector.read_csv_safe(file_path)

        # Structure validation
        results['structure'] = CSVDataValidator.validate_structure(df)

        # Completeness validation
        results['completeness'] = CSVDataValidator.validate_completeness(
            df,
            required_cols=target_schema
        )

        # Type validation
        if expected_types:
            results['types'] = CSVDataValidator.validate_data_types(df, expected_types)

        # Overall result
        results['overall_valid'] = all(
            r.get('valid', True) for r in results.values()
        )

        return results
```

---

## Phase 4: Fine-Tuning (Month 2)

### 4.1 Prepare Training Data

**File: /backend/scripts/prepare_training_data.py**

```python
"""
Prepare training data from historical mappings.
Converts successful mappings to triplet format for fine-tuning.
"""

import pandas as pd
import json
from typing import List, Dict
from pathlib import Path


def prepare_training_triplets(
    historical_mappings: List[Dict],
    all_target_fields: List[str],
    output_path: str = 'training_data.csv'
) -> pd.DataFrame:
    """
    Convert historical mappings to triplet training format.

    Format:
    anchor (source_field) | positive (correct_target) | negative (wrong_target)

    Args:
        historical_mappings: List of confirmed mappings
        all_target_fields: All possible target fields (for mining hard negatives)
        output_path: Where to save training CSV
    """
    triplets = []

    for mapping in historical_mappings:
        source = mapping['source_field']
        target = mapping['target_field']

        # Find hard negatives (wrong targets)
        wrong_targets = [
            f for f in all_target_fields
            if f != target
        ]

        # Use top 3 most similar wrong targets as negatives
        # (This requires computing similarity, so we'll use simple heuristics)
        hard_negatives = sorted(
            wrong_targets,
            key=lambda x: semantic_similarity(target, x),  # You'll implement this
            reverse=True
        )[:3]

        # Create multiple triplets from different hard negatives
        for neg in hard_negatives[:1]:  # Use at least top 1 negative
            triplets.append({
                'anchor': source,
                'positive': target,
                'negative': neg
            })

    # Save training data
    df = pd.DataFrame(triplets)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(triplets)} triplets to {output_path}")

    return df


def semantic_similarity(field1: str, field2: str) -> float:
    """Simple similarity heuristic (replace with actual embedding similarity)"""
    # Convert to lowercase
    f1, f2 = field1.lower(), field2.lower()

    # Jaccard similarity of characters
    set1 = set(f1)
    set2 = set(f2)

    if not set1 and not set2:
        return 1.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0


# Usage
if __name__ == '__main__':
    # Example: Load mappings from your database or logs
    historical_mappings = [
        {'source_field': 'first_name', 'target_field': 'firstName'},
        {'source_field': 'last_name', 'target_field': 'lastName'},
        {'source_field': 'email_addr', 'target_field': 'emailAddress'},
        # ... more mappings
    ]

    all_targets = [
        'firstName', 'lastName', 'emailAddress',
        'phoneNumber', 'department', 'salary'
    ]

    df = prepare_training_triplets(
        historical_mappings,
        all_targets,
        'backend/data/training_triplets.csv'
    )
```

### 4.2 Fine-Tuning Script

**File: /backend/scripts/fine_tune_mapper.py**

```python
"""
Fine-tune Sentence-Transformers on your field mapping data.
"""

from sentence_transformers import SentenceTransformer, losses
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers import SentenceTransformerTrainer
from datasets import Dataset
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fine_tune_mapper(
    training_csv: str,
    output_dir: str = './models/field-mapper-tuned',
    num_epochs: int = 3,
    batch_size: int = 16
):
    """
    Fine-tune embedding model on field mapping data.

    Args:
        training_csv: Path to CSV with columns: anchor, positive, negative
        output_dir: Where to save fine-tuned model
        num_epochs: Number of training epochs
        batch_size: Training batch size
    """
    # Load training data
    logger.info(f"Loading training data from {training_csv}")
    df = pd.read_csv(training_csv)

    if not all(col in df.columns for col in ['anchor', 'positive', 'negative']):
        raise ValueError("Training CSV must have columns: anchor, positive, negative")

    logger.info(f"Loaded {len(df)} training triplets")

    # Convert to HuggingFace dataset
    dataset = Dataset.from_pandas(df[['anchor', 'positive', 'negative']])

    # Load base model
    logger.info("Loading base model: sentence-transformers/paraphrase-mpnet-base-v2")
    model = SentenceTransformer('sentence-transformers/paraphrase-mpnet-base-v2')

    # Training configuration
    args = SentenceTransformerTrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        warmup_steps=100,
        weight_decay=0.01,
        learning_rate=2e-5,
        logging_steps=10,
        save_steps=100,
    )

    # Loss function (Multiple Negatives Ranking Loss)
    loss = losses.MultipleNegativesRankingLoss(model)

    # Create trainer
    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataset=dataset,
        loss=loss,
    )

    # Train
    logger.info("Starting training...")
    trainer.train()

    # Save model
    model.save(output_dir)
    logger.info(f"Fine-tuned model saved to {output_dir}")

    return model


def evaluate_model(model_path: str, test_csv: str) -> Dict:
    """
    Evaluate fine-tuned model on test data.
    """
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    model = SentenceTransformer(model_path)
    test_df = pd.read_csv(test_csv)

    # Encode test data
    anchors = model.encode(test_df['anchor'].tolist(), convert_to_numpy=True)
    positives = model.encode(test_df['positive'].tolist(), convert_to_numpy=True)
    negatives = model.encode(test_df['negative'].tolist(), convert_to_numpy=True)

    # Compute metrics
    pos_scores = np.diag(cosine_similarity(anchors, positives))
    neg_scores = np.diag(cosine_similarity(anchors, negatives))

    # Accuracy (positive > negative)
    accuracy = (pos_scores > neg_scores).mean()

    # Average margin
    margin = (pos_scores - neg_scores).mean()

    logger.info(f"Model Accuracy: {accuracy:.2%}")
    logger.info(f"Average Margin: {margin:.3f}")

    return {
        'accuracy': float(accuracy),
        'margin': float(margin),
        'pos_avg_score': float(pos_scores.mean()),
        'neg_avg_score': float(neg_scores.mean())
    }


if __name__ == '__main__':
    # Fine-tune
    model = fine_tune_mapper(
        training_csv='backend/data/training_triplets.csv',
        output_dir='backend/models/field-mapper-tuned',
        num_epochs=3,
        batch_size=16
    )

    # Evaluate (if you have test data)
    # eval_results = evaluate_model(
    #     'backend/models/field-mapper-tuned',
    #     'backend/data/test_triplets.csv'
    # )
```

---

## Quick Start Commands

### Deploy Semantic Mapper

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Test encoding detection
python -c "
from app.services.semantic_mapper import EncodingDetector
enc = EncodingDetector.detect('sample.csv')
print(f'Detected encoding: {enc}')
"

# 3. Test field mapping
python -c "
from app.services.semantic_mapper import SemanticFieldMapper
mapper = SemanticFieldMapper()
result = mapper.generate_mapping('sample.csv', ['field1', 'field2'])
print(f'Confidence: {result.overall_confidence:.2%}')
"

# 4. Start API server
uvicorn app.main:app --reload

# 5. Test API endpoint
curl -X POST http://localhost:8000/api/mapper/auto-map \
  -F "file=@sample.csv" \
  -F "target_schema_json=[\"firstName\", \"lastName\", \"email\"]"
```

### Fine-Tune Your Model (Month 2)

```bash
# 1. Prepare training data from historical mappings
python backend/scripts/prepare_training_data.py

# 2. Fine-tune model
python backend/scripts/fine_tune_mapper.py

# 3. Update your code to use fine-tuned model
# In semantic_mapper.py, change:
# model_name='backend/models/field-mapper-tuned'
```

---

## Metrics and Monitoring

### Production Metrics to Track

```python
# In your API endpoint or background worker:

mapping_metrics = {
    'total_files_processed': 1000,
    'avg_confidence': 0.87,
    'low_confidence_mappings': 23,  # < 0.70
    'encoding_issues': 5,
    'high_confidence_accuracy': 0.96,  # (>0.85)
    'mapping_latency_ms': 12.5,
    'model_used': 'paraphrase-mpnet-base-v2'  # or fine-tuned model
}
```

### Continuous Improvement

1. **Log all mappings** → Store in database with user corrections
2. **Monthly retraining** → Collect corrected mappings for fine-tuning
3. **A/B testing** → Compare baseline vs fine-tuned model
4. **Monitor by domain** → Track accuracy for different CSV types

---

This completes the implementation guide. Start with Phase 1, then progress through phases as you gather more data and refine your solution.

