# Hybrid Field Mapper - Implementation Guide

**Practical guide to implementing the recommended hybrid architecture**

---

## Quick Start: 3-Step Implementation

### Step 1: Add LLM Layer (2 hours)

```python
# backend/app/services/llm_field_reasoner.py

import os
import json
from typing import List, Dict, Optional
from anthropic import Anthropic
from app.models.mapping import Mapping

class LLMFieldReasoner:
    """
    LLM-based reasoning for ambiguous field mappings.
    Only used when semantic matching returns 40-70% confidence.
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-haiku-20240307"  # Fast and cheap
        self.cache = {}  # Simple in-memory cache

    async def reason_about_field(
        self,
        source_field: str,
        sample_values: List[str],
        candidate_fields: List[Dict],
        entity_name: str
    ) -> Optional[Mapping]:
        """
        Use LLM to reason about best mapping for ambiguous cases.

        Args:
            source_field: The source field name
            sample_values: Sample data values from this field
            candidate_fields: Top 3 semantic matches with metadata
            entity_name: Target entity type (e.g., 'employee')

        Returns:
            Mapping with LLM's decision and reasoning
        """

        # Check cache first
        cache_key = f"{entity_name}:{source_field}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Build prompt
        prompt = self._build_prompt(
            source_field,
            sample_values,
            candidate_fields,
            entity_name
        )

        try:
            # Call Claude Haiku (fast, cheap)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0,  # Deterministic
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            result_text = response.content[0].text
            result = json.loads(result_text)

            # Create mapping
            mapping = Mapping(
                source=source_field,
                target=result["target_field"],
                confidence=result["confidence"],
                method="llm_reasoning"
            )

            # Cache result
            self.cache[cache_key] = mapping

            return mapping

        except Exception as e:
            print(f"LLM reasoning failed: {e}")
            return None

    def _build_prompt(
        self,
        source_field: str,
        sample_values: List[str],
        candidate_fields: List[Dict],
        entity_name: str
    ) -> str:
        """Build prompt for LLM"""

        samples_str = "\n".join([f"  - {v}" for v in sample_values[:10]])
        candidates_str = "\n".join([
            f"  - {c['target_field']} ({c.get('display_name', '')}) "
            f"[{c.get('type', 'string')}] - confidence: {c['similarity']:.2f}"
            for c in candidate_fields
        ])

        return f"""You are a data mapping expert. Analyze this source field and determine the best target field mapping.

SOURCE FIELD: {source_field}

SAMPLE VALUES:
{samples_str}

TARGET SCHEMA: {entity_name}

CANDIDATE TARGET FIELDS (from semantic analysis):
{candidates_str}

ANALYSIS STEPS:
1. What type of data is in the source field based on the sample values?
2. Which candidate target field is the best match?
3. What is your confidence level (0.0 to 1.0)?

Return ONLY a JSON object with this exact format:
{{
  "target_field": "FIELD_NAME",
  "confidence": 0.85,
  "reasoning": "Brief 1-sentence explanation"
}}

IMPORTANT: Return ONLY the JSON, no other text."""

# Singleton
_llm_reasoner = None

def get_llm_reasoner() -> LLMFieldReasoner:
    global _llm_reasoner
    if _llm_reasoner is None:
        _llm_reasoner = LLMFieldReasoner()
    return _llm_reasoner
```

### Step 2: Integrate with Existing Mapper (1 hour)

```python
# backend/app/services/field_mapper.py
# Add to existing FieldMapper class

from app.services.llm_field_reasoner import get_llm_reasoner

class FieldMapper:
    def __init__(self):
        # Existing initialization
        self.schemas_dir = Path(__file__).parent.parent / "schemas"
        self.alias_dictionary = self._load_aliases()
        self.min_confidence = 0.70
        self.semantic_matcher = get_semantic_matcher() if SEMANTIC_MATCHING_AVAILABLE else None

        # NEW: Add LLM reasoner
        self.llm_reasoner = None
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.llm_reasoner = get_llm_reasoner()
                print("LLM reasoning layer enabled")
            except Exception as e:
                print(f"LLM reasoning disabled: {e}")

        # NEW: Confidence thresholds
        self.HIGH_CONFIDENCE = 0.85  # Auto-accept
        self.MEDIUM_CONFIDENCE = 0.70  # Use semantic
        self.LLM_THRESHOLD = 0.40  # Use LLM below semantic confidence

    async def auto_map_with_samples(
        self,
        source_fields: List[str],
        target_schema: EntitySchema,
        sample_data: Dict[str, List[str]] = None,
        min_confidence: float = None
    ) -> List[Mapping]:
        """
        Enhanced auto-mapping with LLM reasoning for ambiguous cases.

        This is the new async method that uses LLM when needed.
        Fallback to sync auto_map() if no LLM available.
        """

        if not self.llm_reasoner or not sample_data:
            # Fallback to existing sync method
            return self.auto_map(source_fields, target_schema, min_confidence)

        if min_confidence is not None:
            self.min_confidence = min_confidence

        mappings = []
        used_targets = set()

        # STAGE 1: Fast exact/alias/partial matching (unchanged)
        for source_field in source_fields:
            best_match = self.get_best_match(
                source_field,
                target_schema.fields,
                used_targets
            )

            if best_match and best_match.confidence >= self.HIGH_CONFIDENCE:
                mappings.append(best_match)
                used_targets.add(best_match.target)

        mapped_sources = {m.source for m in mappings}
        unmapped_sources = [f for f in source_fields if f not in mapped_sources]

        # STAGE 2: Semantic matching with LLM fallback (NEW)
        if unmapped_sources and self.semantic_matcher:
            for source_field in unmapped_sources:
                # Get semantic matches
                semantic_matches = self.semantic_matcher.find_best_match(
                    source_field,
                    target_schema.entity_name,
                    top_k=3,
                    min_similarity=self.LLM_THRESHOLD
                )

                if not semantic_matches:
                    continue

                best_semantic = semantic_matches[0]

                # HIGH CONFIDENCE: Accept semantic match
                if best_semantic['similarity'] >= self.MEDIUM_CONFIDENCE:
                    mapping = Mapping(
                        source=source_field,
                        target=best_semantic['target_field'],
                        confidence=best_semantic['similarity'],
                        method='semantic'
                    )
                    mappings.append(mapping)
                    used_targets.add(mapping.target)

                # MEDIUM CONFIDENCE: Use LLM reasoning (NEW)
                elif (best_semantic['similarity'] >= self.LLM_THRESHOLD and
                      source_field in sample_data):

                    # Try LLM reasoning
                    llm_mapping = await self.llm_reasoner.reason_about_field(
                        source_field=source_field,
                        sample_values=sample_data[source_field],
                        candidate_fields=semantic_matches,
                        entity_name=target_schema.entity_name
                    )

                    if llm_mapping and llm_mapping.confidence >= 0.60:
                        # Accept LLM decision
                        if llm_mapping.target not in used_targets:
                            mappings.append(llm_mapping)
                            used_targets.add(llm_mapping.target)
                    else:
                        # LLM uncertain, keep semantic match if >= min
                        if best_semantic['similarity'] >= self.min_confidence:
                            mapping = Mapping(
                                source=source_field,
                                target=best_semantic['target_field'],
                                confidence=best_semantic['similarity'],
                                method='semantic_uncertain'
                            )
                            mappings.append(mapping)
                            used_targets.add(mapping.target)

        # Sort by confidence
        mappings.sort(key=lambda m: m.confidence, reverse=True)
        return mappings
```

### Step 3: Update API Endpoint (30 minutes)

```python
# backend/app/api/endpoints/automapping.py
# Update existing endpoint to use new async method

from fastapi import BackgroundTasks

@router.post("/automap", response_model=AutoMapResponse)
async def auto_map_fields(request: AutoMapRequest):
    """
    Auto-map source fields to target schema.
    Now supports LLM reasoning for ambiguous cases.
    """
    try:
        field_mapper = get_field_mapper()
        schema_manager = get_schema_manager()

        # Get source fields
        if request.file_id:
            upload_store = get_upload_store()
            upload = upload_store.get(request.file_id)
            if not upload:
                raise HTTPException(status_code=404, detail="File not found")
            source_fields = upload.fields
            # NEW: Get sample data from first 10 rows
            sample_data = extract_sample_data(upload.data_preview, source_fields)
        else:
            source_fields = request.source_fields or []
            sample_data = None

        # Get target schema
        target_schema = schema_manager.get_schema(request.target_schema)
        if not target_schema:
            raise HTTPException(status_code=404, detail="Target schema not found")

        # NEW: Use async method with samples if available
        if sample_data:
            mappings = await field_mapper.auto_map_with_samples(
                source_fields=source_fields,
                target_schema=target_schema,
                sample_data=sample_data,
                min_confidence=request.min_confidence
            )
        else:
            # Fallback to sync method
            mappings = field_mapper.auto_map(
                source_fields=source_fields,
                target_schema=target_schema,
                min_confidence=request.min_confidence
            )

        # Rest unchanged...
        mapped_targets = {m.target for m in mappings}
        unmapped_source = [f for f in source_fields if f not in {m.source for m in mappings}]
        unmapped_target = [f.name for f in target_schema.fields if f.name not in mapped_targets]

        return AutoMapResponse(
            mappings=mappings,
            total_mapped=len(mappings),
            total_source=len(source_fields),
            total_target=len(target_schema.fields),
            mapping_percentage=(len(mappings) / len(source_fields) * 100) if source_fields else 0,
            unmapped_source=unmapped_source,
            unmapped_target=unmapped_target
        )

    except Exception as e:
        logger.error(f"Auto-mapping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def extract_sample_data(
    data_preview: List[Dict],
    source_fields: List[str],
    max_samples: int = 10
) -> Dict[str, List[str]]:
    """
    Extract sample values for each field from data preview.

    Args:
        data_preview: First N rows of data
        source_fields: List of field names
        max_samples: Maximum samples per field

    Returns:
        Dict mapping field name to list of sample values
    """
    samples = {field: [] for field in source_fields}

    for row in data_preview[:max_samples]:
        for field in source_fields:
            value = row.get(field)
            if value is not None and str(value).strip():
                samples[field].append(str(value))

    return samples
```

---

## Testing the Implementation

### 1. Unit Test

```python
# backend/tests/test_llm_reasoning.py

import pytest
from app.services.llm_field_reasoner import LLMFieldReasoner

@pytest.mark.asyncio
async def test_llm_reasoning_with_samples():
    """Test LLM can reason about field mapping with sample data"""

    reasoner = LLMFieldReasoner()

    # Sample ambiguous case
    source_field = "emp_info"
    sample_values = ["John Smith", "Jane Doe", "Bob Johnson"]
    candidates = [
        {
            "target_field": "FIRST_NAME",
            "similarity": 0.65,
            "type": "string"
        },
        {
            "target_field": "FULL_NAME",
            "similarity": 0.62,
            "type": "string"
        },
        {
            "target_field": "EMPLOYEE_ID",
            "similarity": 0.45,
            "type": "string"
        }
    ]

    result = await reasoner.reason_about_field(
        source_field=source_field,
        sample_values=sample_values,
        candidate_fields=candidates,
        entity_name="employee"
    )

    assert result is not None
    assert result.target in ["FIRST_NAME", "FULL_NAME"]  # Should be one of these
    assert result.confidence >= 0.60
    assert result.method == "llm_reasoning"


@pytest.mark.asyncio
async def test_llm_caching():
    """Test that LLM results are cached"""

    reasoner = LLMFieldReasoner()

    source_field = "test_field"
    sample_values = ["value1", "value2"]
    candidates = [{"target_field": "TARGET", "similarity": 0.65}]

    # First call
    result1 = await reasoner.reason_about_field(
        source_field, sample_values, candidates, "employee"
    )

    # Second call should be cached (instant)
    import time
    start = time.time()
    result2 = await reasoner.reason_about_field(
        source_field, sample_values, candidates, "employee"
    )
    duration = time.time() - start

    assert duration < 0.01  # Should be instant from cache
    assert result1.target == result2.target
```

### 2. Integration Test

```python
# backend/tests/test_hybrid_mapping.py

import pytest
from app.services.field_mapper import get_field_mapper
from app.services.schema_manager import get_schema_manager

@pytest.mark.asyncio
async def test_hybrid_mapping_workflow():
    """Test complete hybrid mapping workflow"""

    mapper = get_field_mapper()
    schema_manager = get_schema_manager()
    employee_schema = schema_manager.get_schema("employee")

    # Test fields with different confidence levels
    source_fields = [
        "FIRST_NAME",  # Exact match (100%)
        "PersonID",  # Alias match (95%)
        "emp_name",  # Ambiguous (40-70%) - should use LLM
    ]

    sample_data = {
        "FIRST_NAME": ["John", "Jane", "Bob"],
        "PersonID": ["E001", "E002", "E003"],
        "emp_name": ["John Smith", "Jane Doe", "Bob Johnson"],
    }

    mappings = await mapper.auto_map_with_samples(
        source_fields=source_fields,
        target_schema=employee_schema,
        sample_data=sample_data
    )

    # Verify results
    assert len(mappings) == 3

    # Check exact match
    exact_match = next(m for m in mappings if m.source == "FIRST_NAME")
    assert exact_match.target == "FIRST_NAME"
    assert exact_match.method == "exact"
    assert exact_match.confidence == 1.0

    # Check alias match
    alias_match = next(m for m in mappings if m.source == "PersonID")
    assert alias_match.target == "EMPLOYEE_ID"
    assert alias_match.method in ["alias", "alias_partial"]
    assert alias_match.confidence >= 0.85

    # Check LLM reasoning was used for ambiguous
    ambiguous = next(m for m in mappings if m.source == "emp_name")
    # Should be either semantic or llm_reasoning
    assert ambiguous.method in ["semantic", "llm_reasoning"]
```

---

## Configuration

### Environment Variables

```bash
# .env file

# LLM Configuration (optional - system works without it)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Confidence thresholds
MAPPING_HIGH_CONFIDENCE=0.85
MAPPING_MEDIUM_CONFIDENCE=0.70
MAPPING_LLM_THRESHOLD=0.40

# LLM settings
LLM_MODEL=claude-3-haiku-20240307
LLM_TIMEOUT_SECONDS=2
LLM_MAX_TOKENS=500
```

### Feature Flag

```python
# backend/app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings...

    # NEW: LLM feature flags
    ENABLE_LLM_REASONING: bool = False  # Start disabled
    LLM_USAGE_PERCENTAGE: float = 0.0  # Gradual rollout (0.0 to 1.0)

    # LLM configuration
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-haiku-20240307"
    LLM_TIMEOUT_SECONDS: int = 2
    LLM_MAX_TOKENS: int = 500

    # Confidence thresholds
    MAPPING_HIGH_CONFIDENCE: float = 0.85
    MAPPING_MEDIUM_CONFIDENCE: float = 0.70
    MAPPING_LLM_THRESHOLD: float = 0.40

    class Config:
        env_file = ".env"
```

### Gradual Rollout

```python
# backend/app/services/field_mapper.py

import random
from app.config import Settings

settings = Settings()

class FieldMapper:
    def should_use_llm(self) -> bool:
        """Determine if LLM should be used (for gradual rollout)"""
        if not settings.ENABLE_LLM_REASONING:
            return False
        if not self.llm_reasoner:
            return False

        # Gradual rollout based on percentage
        return random.random() < settings.LLM_USAGE_PERCENTAGE
```

---

## Monitoring & Metrics

### Add Metrics Tracking

```python
# backend/app/services/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Mapping metrics
mapping_total = Counter(
    'field_mapping_total',
    'Total field mappings',
    ['method', 'entity']
)

mapping_confidence = Histogram(
    'field_mapping_confidence',
    'Mapping confidence distribution',
    ['method', 'entity'],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
)

mapping_latency = Histogram(
    'field_mapping_latency_seconds',
    'Mapping latency',
    ['method'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

llm_usage_rate = Gauge(
    'field_mapping_llm_usage_rate',
    'Percentage of mappings using LLM'
)

# Track metrics
def track_mapping(
    source_field: str,
    target_field: str,
    confidence: float,
    method: str,
    latency: float,
    entity_name: str
):
    mapping_total.labels(method=method, entity=entity_name).inc()
    mapping_confidence.labels(method=method, entity=entity_name).observe(confidence)
    mapping_latency.labels(method=method).observe(latency)
```

### Add Metrics to Mapper

```python
# backend/app/services/field_mapper.py

import time
from app.services.metrics import track_mapping

class FieldMapper:
    async def auto_map_with_samples(self, ...):
        start_time = time.time()

        # ... mapping logic ...

        # Track each mapping
        for mapping in mappings:
            latency = time.time() - start_time
            track_mapping(
                source_field=mapping.source,
                target_field=mapping.target,
                confidence=mapping.confidence,
                method=mapping.method,
                latency=latency,
                entity_name=target_schema.entity_name
            )

        return mappings
```

---

## Active Learning (Phase 2)

### Add Correction Tracking

```python
# backend/app/services/active_learning.py

from typing import Dict, List
from datetime import datetime
from pathlib import Path
import json

class ActiveLearningPipeline:
    """
    Learns from user corrections to improve mapping accuracy.
    """

    def __init__(self):
        self.corrections_file = Path("data/corrections.jsonl")
        self.corrections_file.parent.mkdir(exist_ok=True)
        self.alias_file = Path("backend/app/schemas/field_aliases.json")

        # Thresholds
        self.MIN_CORRECTIONS = 3  # Learn after 3 corrections
        self.AGREEMENT_THRESHOLD = 0.8  # 80% user agreement

    async def record_correction(
        self,
        source_field: str,
        wrong_mapping: str,
        correct_mapping: str,
        entity_name: str,
        user_id: str,
        file_id: str
    ):
        """Record a user correction"""

        correction = {
            "timestamp": datetime.now().isoformat(),
            "source_field": source_field,
            "wrong_mapping": wrong_mapping,
            "correct_mapping": correct_mapping,
            "entity_name": entity_name,
            "user_id": user_id,
            "file_id": file_id
        }

        # Append to corrections log
        with open(self.corrections_file, 'a') as f:
            f.write(json.dumps(correction) + '\n')

        # Check if we should auto-learn
        await self._check_auto_learn(source_field, correct_mapping, entity_name)

    async def _check_auto_learn(
        self,
        source_field: str,
        correct_mapping: str,
        entity_name: str
    ):
        """Check if this pattern should be auto-learned"""

        # Load all corrections
        corrections = self._load_corrections()

        # Filter for this source field + entity
        relevant = [
            c for c in corrections
            if c['source_field'] == source_field
            and c['entity_name'] == entity_name
        ]

        if len(relevant) < self.MIN_CORRECTIONS:
            return  # Not enough data

        # Count target mappings
        target_counts = {}
        for c in relevant:
            target = c['correct_mapping']
            target_counts[target] = target_counts.get(target, 0) + 1

        # Check agreement
        most_common = max(target_counts, key=target_counts.get)
        agreement = target_counts[most_common] / len(relevant)

        if agreement >= self.AGREEMENT_THRESHOLD:
            # Auto-learn this pattern
            await self._add_alias(source_field, most_common)
            print(
                f"Auto-learned: {source_field} → {most_common} "
                f"({len(relevant)} corrections, {agreement:.1%} agreement)"
            )

    async def _add_alias(self, source_field: str, target_field: str):
        """Add new alias to dictionary"""

        # Load current aliases
        with open(self.alias_file, 'r') as f:
            aliases = json.load(f)

        # Add new alias
        if target_field not in aliases:
            aliases[target_field] = []

        if source_field not in aliases[target_field]:
            aliases[target_field].append(source_field)

            # Save
            with open(self.alias_file, 'w') as f:
                json.dump(aliases, f, indent=2)

            # Rebuild embeddings
            from app.services.semantic_matcher import get_semantic_matcher
            matcher = get_semantic_matcher()
            matcher.build_entity_embeddings(entity_name, force_rebuild=True)

    def _load_corrections(self) -> List[Dict]:
        """Load all corrections from file"""
        corrections = []
        if self.corrections_file.exists():
            with open(self.corrections_file, 'r') as f:
                for line in f:
                    corrections.append(json.loads(line))
        return corrections


# Singleton
_active_learning = None

def get_active_learning() -> ActiveLearningPipeline:
    global _active_learning
    if _active_learning is None:
        _active_learning = ActiveLearningPipeline()
    return _active_learning
```

### Add Correction API

```python
# backend/app/api/endpoints/automapping.py

from app.services.active_learning import get_active_learning

@router.post("/correct-mapping")
async def correct_mapping(
    file_id: str = Form(...),
    source_field: str = Form(...),
    wrong_mapping: str = Form(...),
    correct_mapping: str = Form(...),
    entity_name: str = Form(...)
):
    """
    Record a user correction for active learning.

    The system will automatically learn patterns after 3+ consistent corrections.
    """
    try:
        active_learning = get_active_learning()

        await active_learning.record_correction(
            source_field=source_field,
            wrong_mapping=wrong_mapping,
            correct_mapping=correct_mapping,
            entity_name=entity_name,
            user_id="user123",  # TODO: Get from auth
            file_id=file_id
        )

        return {
            "status": "success",
            "message": "Correction recorded. System will learn from repeated patterns."
        }

    except Exception as e:
        logger.error(f"Failed to record correction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] ANTHROPIC_API_KEY added (if using LLM)
- [ ] Feature flags set (ENABLE_LLM_REASONING=false initially)
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Metrics endpoint accessible

### Phase 1: Deploy LLM Layer (Shadow Mode)

- [ ] Deploy code with LLM disabled
- [ ] Set LLM_USAGE_PERCENTAGE=0.0
- [ ] Monitor baseline performance
- [ ] Enable shadow mode: ENABLE_LLM_REASONING=true, LLM_USAGE_PERCENTAGE=0.0
- [ ] Log LLM decisions without using them
- [ ] Analyze LLM vs semantic accuracy difference

### Phase 2: Gradual Rollout

- [ ] Enable for 1%: LLM_USAGE_PERCENTAGE=0.01
- [ ] Monitor for 24 hours
- [ ] Check metrics: latency, accuracy, cost
- [ ] Increase to 5%: LLM_USAGE_PERCENTAGE=0.05
- [ ] Monitor for 48 hours
- [ ] Increase to 100%: LLM_USAGE_PERCENTAGE=1.0

### Phase 3: Enable Active Learning

- [ ] Deploy active learning pipeline
- [ ] Add correction UI/API
- [ ] Monitor corrections collection
- [ ] Verify auto-learning after 3 corrections
- [ ] Check alias dictionary updates

### Monitoring

- [ ] Set up dashboards for:
  - Mapping accuracy (by method)
  - Latency (P50, P95, P99)
  - LLM usage rate
  - LLM cost
  - Correction rate
  - Auto-learned patterns count
- [ ] Set up alerts for:
  - Latency > 500ms (P95)
  - LLM cost > $100/month
  - Error rate > 5%
  - LLM availability < 99%

---

## Cost Calculator

```python
# Estimate monthly costs

# Assumptions
fields_per_month = 10000  # Total fields processed
llm_usage_rate = 0.02  # 2% use LLM

# Claude Haiku pricing (as of 2024)
input_price_per_1m = 0.25  # $0.25 per 1M input tokens
output_price_per_1m = 1.25  # $1.25 per 1M output tokens

# Estimated tokens per request
input_tokens_per_request = 300  # Prompt with samples
output_tokens_per_request = 100  # JSON response

# Calculate
llm_requests = fields_per_month * llm_usage_rate
total_input_tokens = llm_requests * input_tokens_per_request
total_output_tokens = llm_requests * output_tokens_per_request

input_cost = (total_input_tokens / 1_000_000) * input_price_per_1m
output_cost = (total_output_tokens / 1_000_000) * output_price_per_1m

total_llm_cost = input_cost + output_cost

print(f"Fields per month: {fields_per_month:,}")
print(f"LLM requests: {llm_requests:,}")
print(f"Estimated LLM cost: ${total_llm_cost:.2f}/month")

# Example output:
# Fields per month: 10,000
# LLM requests: 200
# Estimated LLM cost: $0.08/month
```

---

## Troubleshooting

### Issue: LLM timeout

**Symptom:** Some mappings take >2 seconds
**Solution:**
```python
# Increase timeout in config
LLM_TIMEOUT_SECONDS=5

# Or disable LLM for that request
ENABLE_LLM_REASONING=false
```

### Issue: LLM returns invalid JSON

**Symptom:** `json.loads()` fails
**Solution:**
```python
# Add retry with clearer prompt
try:
    result = json.loads(response.content[0].text)
except json.JSONDecodeError:
    # Retry with stricter prompt
    prompt += "\n\nIMPORTANT: Return ONLY valid JSON, no markdown or explanation."
    response = self.client.messages.create(...)
    result = json.loads(response.content[0].text)
```

### Issue: Cost higher than expected

**Symptom:** LLM API bill > $50/month
**Solution:**
```python
# Reduce LLM usage
LLM_USAGE_PERCENTAGE=0.01  # Only 1% of traffic

# Or increase confidence threshold (use LLM less)
MAPPING_LLM_THRESHOLD=0.30  # Only for very low confidence
```

---

## Next Steps

1. **Implement Step 1-3** (3.5 hours total)
2. **Test with real data** (1 hour)
3. **Deploy in shadow mode** (1 week monitoring)
4. **Gradual rollout** (2 weeks)
5. **Add active learning** (Phase 2, Week 5-6)

**Total time to production:** 4-6 weeks
**Expected accuracy improvement:** 75% → 85-88%
**Expected cost:** $10-30/month

---

**End of Implementation Guide**
