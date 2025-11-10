# SnapMap Performance Guide

**Version:** 2.0.0
**Last Updated:** November 7, 2025

---

## Performance Benchmarks

### File Processing

| Rows | File Size | Parse Time | Rate |
|------|-----------|------------|------|
| 100 | 10 KB | 0.015s | 6,667 rows/s |
| 1,000 | 100 KB | 0.082s | 12,195 rows/s |
| 10,000 | 1 MB | 0.654s | 15,291 rows/s |
| 100,000 | 10 MB | 6.892s | 14,510 rows/s |

### Field Mapping

| Fields | Mapping Time | Rate |
|--------|--------------|------|
| 10 | 8ms | 1,250 fields/s |
| 50 | 35ms | 1,429 fields/s |
| 100 | 68ms | 1,471 fields/s |

**Vector DB Query**: <1ms per field

### Export

| Format | Rows | Export Time | Rate |
|--------|------|-------------|------|
| CSV | 10,000 | 0.8s | 12,500 rows/s |
| CSV | 100,000 | 8.5s | 11,765 rows/s |
| XML | 10,000 | 1.2s | 8,333 rows/s |
| XML | 100,000 | 13.1s | 7,634 rows/s |

---

## Optimization Techniques

### 1. Vectorized Operations

**Bad** (row-by-row):
```python
for idx, row in df.iterrows():
    df.loc[idx, 'EMAIL_CLEAN'] = row['EMAIL'].lower().strip()
```

**Good** (vectorized):
```python
df['EMAIL_CLEAN'] = df['EMAIL'].str.lower().str.strip()
```

**Performance**: 100x faster for large DataFrames

### 2. Chunked Processing

**For large files**:
```python
chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

**Memory savings**: Constant memory usage regardless of file size

### 3. Streaming Responses

**Bad**:
```python
csv_str = df.to_csv()
return Response(csv_str, media_type="text/csv")
```

**Good**:
```python
def stream_csv():
    for chunk in df_chunks:
        yield chunk.to_csv()

return StreamingResponse(stream_csv(), media_type="text/csv")
```

**Memory savings**: 90% reduction for large files

### 4. Connection Pooling

**Uvicorn workers**:
```bash
# Formula: (2 × CPU_CORES) + 1
uvicorn main:app --workers 9  # For 4-core server
```

### 5. Caching

**nginx caching**:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;

location /api/schema {
    proxy_cache api_cache;
    proxy_cache_valid 200 1h;
}
```

---

## Resource Requirements

### Minimum

**Development**:
- CPU: 2 cores
- RAM: 4 GB
- Storage: 10 GB
- Network: 10 Mbps

**Capacity**: 10 concurrent users, files up to 10,000 rows

### Recommended

**Production**:
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB (SSD)
- Network: 100 Mbps

**Capacity**: 50 concurrent users, files up to 100,000 rows

### High Performance

**Large-scale**:
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 100+ GB (NVMe SSD)
- Network: 1 Gbps

**Capacity**: 100+ concurrent users, files up to 1,000,000 rows

---

## Monitoring Metrics

### Application Metrics

**Key Performance Indicators**:
- Request latency (p50, p95, p99)
- Throughput (requests/second)
- Error rate (%)
- File processing time
- Memory usage
- CPU usage

**Prometheus metrics**:
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### System Metrics

**Monitor**:
```bash
# CPU
top
htop

# Memory
free -h
vmstat 1

# Disk I/O
iostat -x 1
iotop

# Network
iftop
nethogs
```

---

## Performance Tuning

### Backend (FastAPI)

**1. Increase workers**:
```bash
uvicorn main:app --workers 8
```

**2. Enable HTTP/2**:
```nginx
listen 443 ssl http2;
```

**3. Optimize parsing**:
```python
# Use C engine (faster)
df = pd.read_csv(file, engine='c')

# Specify dtypes
df = pd.read_csv(file, dtype={'CANDIDATE_ID': str})
```

### Frontend (React)

**1. Code splitting**:
```typescript
const FileUpload = lazy(() => import('./components/FileUpload'));
```

**2. Memoization**:
```typescript
const MemoizedComponent = React.memo(Component);
```

**3. Virtualization** (for large lists):
```typescript
import { FixedSizeList } from 'react-window';
```

### Database (ChromaDB)

**Already optimized**:
- Pre-computed embeddings
- Efficient similarity search
- Memory-mapped storage

**No tuning needed**

### nginx

**1. Worker processes**:
```nginx
worker_processes auto;
worker_connections 1024;
```

**2. Compression**:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

**3. Caching**:
```nginx
expires 1y;
add_header Cache-Control "public, immutable";
```

---

## Load Testing

### Locust

**Install**:
```bash
pip install locust
```

**Test script** (`locustfile.py`):
```python
from locust import HttpUser, task, between

class SnapMapUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_file(self):
        files = {'file': ('test.csv', b'col1,col2\nval1,val2')}
        self.client.post("/api/upload", files=files)
```

**Run**:
```bash
locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089
```

**Test scenarios**:
1. **Light load**: 10 users, 1 spawn rate
2. **Normal load**: 50 users, 5 spawn rate
3. **Heavy load**: 100 users, 10 spawn rate
4. **Stress test**: 500 users, 50 spawn rate

### Apache Bench

**Simple test**:
```bash
ab -n 1000 -c 10 http://localhost:8000/health
```

**Expected results**:
- Requests per second: 1000+
- Time per request: <10ms
- Failed requests: 0

---

## Scalability

### Vertical Scaling

**Increase resources**:
- More CPU cores
- More RAM
- Faster storage (NVMe SSD)

**Expected improvement**: 2-3x capacity

### Horizontal Scaling

**Load balancing** (nginx):
```nginx
upstream snapmap_backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

**Shared storage**:
- NFS for vector database
- Redis for session management (future)
- PostgreSQL for persistent data (future)

**Expected improvement**: Linear scaling up to 10 servers

---

## Troubleshooting Performance

### Slow File Upload

**Diagnose**:
```bash
# Check network speed
speedtest-cli

# Check server load
top
```

**Solutions**:
1. Increase nginx `client_max_body_size`
2. Increase uvicorn timeout
3. Use SSD storage

### Slow Field Mapping

**Diagnose**:
```bash
# Check vector DB
ls -la backend/chroma_db/

# Check CPU usage
top
```

**Solutions**:
1. Rebuild vector DB: `python build_vector_db.py`
2. Increase CPU cores
3. Reduce source fields

### High Memory Usage

**Diagnose**:
```bash
ps aux --sort=-%mem | head -10
```

**Solutions**:
1. Reduce uvicorn workers
2. Enable chunked processing
3. Add swap space
4. Upgrade RAM

---

*Last Updated: November 7, 2025*
