# SnapMap Backend - Implementation Roadmap

## Executive Overview

This roadmap prioritizes architectural improvements across **3 phases** spanning **3 months**, organized by impact and effort.

---

## Phase 1: Security & Stability Hardening (Week 1-2)

### Goal
Establish secure, stable foundation for production deployment with minimal refactoring.

### 1.1 Remove Debug Code & Sensitive Data Exposure

**Files to Modify:**
- `backend/app/api/endpoints/transform.py` (lines 185-235)
- All service files with `print()` statements

**Changes:**
```python
# BEFORE: transform.py
print(f"[XML_PREVIEW_DEBUG] file_id: {request.file_id}...")
"traceback": error_traceback  # Exposes internal details

# AFTER: transform.py
logger.debug(f"XML preview requested: {request.file_id}")
logger.exception("XML preview transformation failed", exc_info=True)
# Return only error code and message to client, not traceback
```

**Effort:** 2 hours
**Impact:** High - Security/Professional appearance

---

### 1.2 Standardize Error Handling

**Files to Create:**
- `backend/app/core/exceptions.py` (new file)
- `backend/app/core/error_handlers.py` (new file)

**Files to Modify:**
- `backend/main.py`
- All files in `backend/app/api/endpoints/`
- All files in `backend/app/services/`

**Implementation:**

```python
# backend/app/core/exceptions.py
from typing import Optional, Dict, Any

class AppException(Exception):
    """Base application exception"""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationError(AppException):
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__("VALIDATION_ERROR", message, 400, details)

class NotFoundError(AppException):
    def __init__(self, resource: str):
        super().__init__(
            "NOT_FOUND",
            f"{resource} not found",
            404,
            {"resource": resource}
        )

class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__("UNAUTHORIZED", message, 401)
```

```python
# backend/app/core/error_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from app.core.exceptions import AppException
import uuid

def setup_error_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "request_id": request_id
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {} if not app.debug else {"error": str(exc)},
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "request_id": request_id
            }
        )
```

**Effort:** 4 hours
**Impact:** High - Consistency, professional error responses

---

### 1.3 Implement Structured Logging

**Files to Create:**
- `backend/app/core/logging_config.py` (new file)

**Files to Modify:**
- `backend/main.py` (add initialization)
- All service files (replace `print()` with logging)

**Implementation:**

```python
# backend/app/core/logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger
import sys

def setup_logging(debug: bool = False):
    """Setup structured JSON logging"""

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    if debug:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        level = logging.DEBUG
    else:
        formatter = jsonlogger.JsonFormatter()
        level = logging.INFO

    console_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root_logger

# Usage in services
logger = logging.getLogger(__name__)

# Example replacements
# BEFORE: print(f"Error loading metadata: {e}")
# AFTER:
logger.exception("Error loading metadata", extra={"file_id": file_id})
```

**Effort:** 3 hours
**Impact:** Medium - Debugging, monitoring

---

### 1.4 Fix CORS Configuration

**File to Modify:**
- `backend/main.py` (lines 19-31)

**Changes:**

```python
# BEFORE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AFTER
import os

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict methods
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Total-Count", "X-Request-ID"],
    max_age=3600,
)
```

**Effort:** 1 hour
**Impact:** High - Security

---

### 1.5 Add Request ID Tracking

**File to Modify:**
- `backend/main.py` (add middleware)

**Implementation:**

```python
from fastapi import Request
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

**Effort:** 30 minutes
**Impact:** Medium - Debugging, tracing

---

### Phase 1 Summary

| Task | Effort | Impact |
|------|--------|--------|
| Remove debug code | 2h | High |
| Standardize errors | 4h | High |
| Structured logging | 3h | Medium |
| Fix CORS | 1h | High |
| Request ID tracking | 0.5h | Medium |
| **Total** | **10.5h** | **High** |

---

## Phase 2: Observability & Performance (Week 3-4)

### Goal
Add monitoring, logging, and foundational performance improvements.

### 2.1 Implement Rate Limiting & Authentication

**Files to Create:**
- `backend/app/core/auth.py` (new file)
- `backend/app/core/rate_limiter.py` (new file)

**Installation:**
```bash
pip install fastapi-limiter2 python-jose[cryptography]
```

**Implementation:**

```python
# backend/app/core/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthenticationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

security = HTTPBearer()

def create_access_token(user_id: str, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthenticationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_id
```

```python
# backend/app/core/rate_limiter.py
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

async def init_rate_limiter():
    redis_client = redis.from_url("redis://localhost:6379")
    await FastAPILimiter.init(redis_client)

# Or use in-memory limiter for development
from fastapi_limiter.backends.inmemory import InMemoryBackend

async def init_rate_limiter_memory():
    await FastAPILimiter.init(InMemoryBackend())
```

**Effort:** 3 hours
**Impact:** High - Security, stability

---

### 2.2 Add Health Check Endpoints

**Files to Create:**
- `backend/app/api/endpoints/health.py` (new file)

**Implementation:**

```python
# backend/app/api/endpoints/health.py
from fastapi import APIRouter, HTTPException
from app.services.file_storage import get_file_storage
from app.services.schema_manager import get_schema_manager
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check of all components"""
    checks = {
        "api": "healthy",
        "file_storage": check_file_storage(),
        "schema_manager": check_schema_manager(),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Return 503 if any component unhealthy
    if any(v != "healthy" for v in checks.values() if isinstance(v, str)):
        raise HTTPException(status_code=503, detail=checks)

    return checks

def check_file_storage():
    try:
        storage = get_file_storage()
        stats = storage.get_stats()
        return "healthy"
    except Exception as e:
        return f"unhealthy: {str(e)}"

def check_schema_manager():
    try:
        schema_mgr = get_schema_manager()
        entities = schema_mgr.get_available_entities()
        return "healthy" if entities else "unhealthy: no entities"
    except Exception as e:
        return f"unhealthy: {str(e)}"
```

**Effort:** 2 hours
**Impact:** Medium - Monitoring

---

### 2.3 Add Prometheus Metrics

**Installation:**
```bash
pip install prometheus-client
```

**Files to Create:**
- `backend/app/core/metrics.py` (new file)

**Implementation:**

```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# Counters
uploads_total = Counter(
    'uploads_total',
    'Total number of file uploads',
    ['status']
)

transformations_total = Counter(
    'transformations_total',
    'Total number of transformations',
    ['entity', 'format']
)

validation_errors_total = Counter(
    'validation_errors_total',
    'Total validation errors',
    ['error_type']
)

# Histograms (timing)
upload_duration_seconds = Histogram(
    'upload_duration_seconds',
    'Upload processing time in seconds',
    ['file_format']
)

transformation_duration_seconds = Histogram(
    'transformation_duration_seconds',
    'Transformation processing time in seconds',
    ['format']
)

# Gauges (current state)
active_transformations = Gauge(
    'active_transformations',
    'Number of currently processing transformations'
)

temp_storage_files = Gauge(
    'temp_storage_files',
    'Number of files in temporary storage'
)

# Usage in endpoints
import contextlib

@contextlib.contextmanager
def track_upload(file_format: str):
    uploads_total.labels(status='started').inc()
    start = time.time()
    try:
        yield
        uploads_total.labels(status='success').inc()
    except Exception:
        uploads_total.labels(status='error').inc()
        raise
    finally:
        duration = time.time() - start
        upload_duration_seconds.labels(file_format=file_format).observe(duration)

# In endpoint
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with track_upload(get_file_format(file.filename)):
        # ... existing code
```

**Effort:** 2 hours
**Impact:** Medium - Monitoring, optimization

---

### 2.4 Implement Background Cleanup Task

**File to Modify:**
- `backend/main.py` (add startup events)

**Implementation:**

```python
# backend/main.py
import asyncio
from app.services.file_storage import get_file_storage

@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info("Application starting up")

    # Cleanup old files
    storage = get_file_storage()
    storage._cleanup_old_files()

    # Start background cleanup task
    asyncio.create_task(background_cleanup_task())

async def background_cleanup_task():
    """Periodically cleanup old files"""
    storage = get_file_storage()

    while True:
        try:
            # Clean every 30 minutes
            await asyncio.sleep(1800)
            logger.info("Running background cleanup of temporary files")
            storage._cleanup_old_files()
        except Exception as e:
            logger.exception("Error in background cleanup task")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutting down")
```

**Effort:** 1 hour
**Impact:** High - Stability

---

### 2.5 Add Input Validation Middleware

**Files to Modify:**
- `backend/main.py` (add middleware)

**Implementation:**

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.middleware("http")
async def validate_content_type(request: Request, call_next):
    """Validate Content-Type header for POST requests"""
    if request.method == "POST":
        content_type = request.headers.get("content-type", "")

        # Allow multipart (file uploads) and JSON
        if not any(ct in content_type for ct in ["multipart", "application/json"]):
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "INVALID_CONTENT_TYPE",
                        "message": "Content-Type must be application/json or multipart/form-data"
                    }
                }
            )

    return await call_next(request)

@app.middleware("http")
async def validate_request_size(request: Request, call_next):
    """Validate request body size"""
    MAX_REQUEST_SIZE = 100 * 1024 * 1024  # 100MB

    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413,
            content={
                "error": {
                    "code": "REQUEST_TOO_LARGE",
                    "message": f"Request exceeds maximum size of {MAX_REQUEST_SIZE / 1024 / 1024}MB"
                }
            }
        )

    return await call_next(request)
```

**Effort:** 1 hour
**Impact:** Medium - Security

---

### Phase 2 Summary

| Task | Effort | Impact |
|------|--------|--------|
| Rate limiting & auth | 3h | High |
| Health checks | 2h | Medium |
| Prometheus metrics | 2h | Medium |
| Background cleanup | 1h | High |
| Request validation | 1h | Medium |
| **Total** | **9h** | **High** |

---

## Phase 3: Scalability & Architecture (Week 5-12)

### Goal
Prepare system for horizontal scaling and high concurrency.

### 3.1 Implement Async File Storage

**File to Modify:**
- `backend/app/services/file_storage.py`

**Installation:**
```bash
pip install aiofiles
```

**Key Changes:**

```python
import aiofiles
import asyncio

class FileStorage:
    async def _load_metadata_async(self):
        """Async metadata loading"""
        if self.metadata_file.exists():
            try:
                async with aiofiles.open(self.metadata_file, 'r') as f:
                    content = await f.read()
                    # ...
            except Exception as e:
                logger.exception("Error loading metadata")
                self._metadata = {}

    async def _save_metadata_async(self):
        """Async metadata saving"""
        try:
            data = {file_id: {...} for file_id, meta in self._metadata.items()}
            async with aiofiles.open(self.metadata_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.exception("Error saving metadata")

# Update endpoints to use async
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    storage = get_file_storage()
    # ...
    await storage._save_metadata_async()
```

**Effort:** 3 hours
**Impact:** Medium - Async compliance

---

### 3.2 Implement Caching Layer with Redis

**Installation:**
```bash
pip install redis aioredis
```

**Files to Create:**
- `backend/app/core/cache.py` (new file)

**Implementation:**

```python
# backend/app/core/cache.py
import redis.asyncio as redis
import json
from typing import Any, Optional
import os

class CacheManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = None

    async def connect(self):
        self.redis = await redis.from_url(self.redis_url, encoding="utf8")

    async def disconnect(self):
        await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key)

# Usage in schema_manager
cache = CacheManager()

async def get_schema_cached(entity_name: str):
    cache_key = f"schema:{entity_name}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return EntitySchema(**cached)

    # Load from file
    schema = load_schema_from_file(entity_name)

    # Cache for 1 hour
    await cache.set(cache_key, schema.dict(), ttl=3600)

    return schema
```

**Effort:** 3 hours
**Impact:** High - Performance

---

### 3.3 Move to Object Storage (S3)

**Installation:**
```bash
pip install boto3
```

**Files to Create:**
- `backend/app/services/s3_storage.py` (new file)

**Implementation:**

```python
# backend/app/services/s3_storage.py
import boto3
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET", "snapmap-uploads")
        self.region = os.getenv("AWS_REGION", "us-east-1")

        self.s3_client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    async def upload_file(self, file_id: str, data: bytes) -> bool:
        """Upload file to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=f"uploads/{file_id}.parquet",
                Body=data,
                ServerSideEncryption='AES256'
            )
            logger.info(f"Uploaded file {file_id} to S3")
            return True
        except ClientError as e:
            logger.exception(f"Error uploading to S3: {e}")
            return False

    async def download_file(self, file_id: str) -> Optional[bytes]:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=f"uploads/{file_id}.parquet"
            )
            return response['Body'].read()
        except ClientError as e:
            logger.exception(f"Error downloading from S3: {e}")
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=f"uploads/{file_id}.parquet"
            )
            return True
        except ClientError as e:
            logger.exception(f"Error deleting from S3: {e}")
            return False
```

**Effort:** 4 hours
**Impact:** High - Scalability

---

### 3.4 Implement Message Queue for Async Tasks

**Installation:**
```bash
pip install celery redis
```

**Files to Create:**
- `backend/app/celery_app.py` (new file)
- `backend/app/tasks/transform.py` (new file)
- `backend/app/tasks/notify.py` (new file)

**Implementation:**

```python
# backend/app/celery_app.py
from celery import Celery
import os

celery_app = Celery(
    'snapmap',
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# backend/app/tasks/transform.py
from app.celery_app import celery_app
from app.services.transformer import get_transformation_engine
from app.services.schema_manager import get_schema_manager
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def transform_file_async(self, file_id: str, entity_name: str, output_format: str):
    """
    Asynchronous file transformation

    Args:
        file_id: ID of uploaded file
        entity_name: Target entity type
        output_format: 'csv' or 'xml'
    """
    try:
        # Get file from storage
        storage = get_file_storage()
        df = storage.retrieve_dataframe(file_id)

        if df is None:
            raise FileNotFoundError(f"File {file_id} not found")

        # Get schema and transformer
        schema_mgr = get_schema_manager()
        schema = schema_mgr.get_schema(entity_name)
        transformer = get_transformation_engine()

        # Transform
        transformed_df, _ = transformer.transform_data(
            df.to_dict('records'),
            [],  # mappings
            schema
        )

        # Save result
        result_file_id = f"{file_id}_result_{output_format}"
        storage.store_dataframe(transformed_df, f"result_{result_file_id}.parquet")

        logger.info(f"Transformation completed for file {file_id}")
        return {
            "status": "success",
            "file_id": result_file_id,
            "rows": len(transformed_df)
        }

    except Exception as e:
        logger.exception(f"Transformation failed for {file_id}")

        # Retry with exponential backoff
        raise self.retry(
            exc=e,
            countdown=2 ** self.request.retries
        )

# Usage in endpoint
@router.post("/transform/export-async")
async def export_csv_async(request: ExportRequest):
    """Queue transformation task"""
    task = transform_file_async.delay(
        file_id=request.file_id,
        entity_name=request.entity_name,
        output_format="csv"
    )

    return {
        "task_id": task.id,
        "status": "queued",
        "check_url": f"/tasks/{task.id}/status"
    }

@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get status of async task"""
    task = celery_app.AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

**Effort:** 5 hours
**Impact:** High - Scalability, responsiveness

---

### 3.5 Implement Distributed Tracing

**Installation:**
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger
```

**Files to Create:**
- `backend/app/core/tracing.py` (new file)

**Implementation:**

```python
# backend/app/core/tracing.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import os

def init_tracing():
    """Initialize distributed tracing with Jaeger"""

    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_PORT", 6831)),
    )

    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

    # Instrument FastAPI
    FastAPIInstrumentor().instrument()

# Usage in main.py
@app.on_event("startup")
async def startup():
    if os.getenv("TRACING_ENABLED", "false") == "true":
        init_tracing()
```

**Effort:** 2 hours
**Impact:** Medium - Debugging, monitoring

---

### 3.6 Add Dependency Injection Pattern

**Installation:**
```bash
pip install dependency-injector
```

**Files to Create:**
- `backend/app/core/container.py` (new file)

**Implementation:**

```python
# backend/app/core/container.py
from dependency_injector import containers, providers
from app.services.file_parser import FileParser
from app.services.file_storage import FileStorage
from app.services.validator import ValidationEngine
from app.services.transformer import Transformer

class Container(containers.DeclarativeContainer):
    """Dependency injection container"""

    config = providers.Configuration()

    # Services
    file_parser = providers.Singleton(FileParser)
    file_storage = providers.Singleton(FileStorage)
    validator = providers.Singleton(ValidationEngine)
    transformer = providers.Singleton(Transformer)

# Usage in endpoints
container = Container()

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    parser: FileParser = Depends(container.file_parser),
    storage: FileStorage = Depends(container.file_storage)
):
    # Better testability
    df = parser.parse_file(content, file.filename)
    file_id = storage.store_dataframe(df, file.filename)
```

**Effort:** 3 hours
**Impact:** High - Testability, maintainability

---

### Phase 3 Summary

| Task | Effort | Impact |
|------|--------|--------|
| Async file storage | 3h | Medium |
| Redis caching | 3h | High |
| S3 object storage | 4h | High |
| Message queue | 5h | High |
| Distributed tracing | 2h | Medium |
| Dependency injection | 3h | High |
| **Total** | **20h** | **Very High** |

---

## Implementation Timeline

```
Week 1-2 (Phase 1): 10.5 hours
├── Mon-Tue: Remove debug code, standardize errors
├── Wed: Structured logging
└── Thu-Fri: CORS, request tracking

Week 3-4 (Phase 2): 9 hours
├── Mon: Rate limiting & auth
├── Tue-Wed: Health checks, metrics
├── Thu: Background cleanup
└── Fri: Request validation

Week 5-12 (Phase 3): 20 hours (distributed)
├── Week 5-6: Async file storage, caching
├── Week 7-8: S3 integration, message queue
├── Week 9-10: Distributed tracing
├── Week 11: Dependency injection
└── Week 12: Testing & stabilization
```

---

## Success Metrics

### Phase 1 (Security)
- [ ] All debug code removed
- [ ] No raw tracebacks in error responses
- [ ] Consistent error format across all endpoints
- [ ] CORS configuration environment-based
- [ ] All errors logged with context

### Phase 2 (Observability)
- [ ] 100% of requests have request IDs
- [ ] All errors logged to structured logger
- [ ] Prometheus metrics collected
- [ ] Health check endpoints returning < 100ms
- [ ] No temporary files older than 1 hour
- [ ] Temp file growth bounded

### Phase 3 (Scalability)
- [ ] Horizontal scaling support (multiple instances)
- [ ] Sub-100ms p95 latency for small files
- [ ] Support for 10x concurrent users
- [ ] Async task queuing for large transformations
- [ ] Distributed tracing shows service dependencies
- [ ] 90% test coverage

---

## Risk Mitigation

### High-Risk Items

1. **Database Migration** (if adding PostgreSQL)
   - Mitigate: Start with SQLite, migrate later
   - Timeline: Phase 4 (future)

2. **Breaking API Changes**
   - Mitigate: Implement versioning (v1, v2)
   - Timeline: Phase 2

3. **Redis Dependency**
   - Mitigate: Fall back to in-memory cache
   - Timeline: Phase 3, optional

4. **File Storage Changes**
   - Mitigate: Abstract storage layer first
   - Timeline: Phase 3, optional

---

## Resource Requirements

### Team
- 1 Backend Engineer: 40 hours (10 weeks, 4 hours/week average)
- 1 DevOps Engineer: 15 hours (for deployment, monitoring)
- 1 QA Engineer: 10 hours (testing, validation)

### Infrastructure
- Development: Laptop/Desktop
- Testing: Docker environment
- Production: Kubernetes cluster (Phase 3)
- Monitoring: Prometheus + Grafana (Phase 2)
- Tracing: Jaeger (Phase 3)

### Tools & Services
- GitHub/GitLab for version control
- Docker for containerization
- AWS/GCP for cloud services
- Redis for caching/sessions
- PostgreSQL for data (future)
- Celery for task queue

---

## Next Steps

1. **Immediately:**
   - Review this roadmap with team
   - Set up GitHub issues for each task
   - Create feature branches for Phase 1

2. **This Week:**
   - Begin Phase 1 implementation
   - Set up development environment
   - Create test cases for current behavior

3. **Planning:**
   - Estimate additional resources needed
   - Identify infrastructure requirements
   - Plan deployment strategy

---

## Appendix: Quick Start Commands

```bash
# Phase 1 Setup
pip install -r requirements.txt
pip install python-jose[cryptography]

# Phase 2 Setup
pip install fastapi-limiter2 prometheus-client aiofiles
pip install pythonjsonlogger

# Phase 3 Setup
pip install redis celery boto3 opentelemetry-api
pip install opentelemetry-exporter-jaeger dependency-injector

# Testing
pytest tests/ --cov=app

# Local Development
docker-compose up -d
uvicorn main:app --reload

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

This roadmap provides a structured path to production-ready backend while maintaining stability and minimizing disruption. Execute Phase 1 immediately for quick security wins, then plan longer-term scaling improvements.
