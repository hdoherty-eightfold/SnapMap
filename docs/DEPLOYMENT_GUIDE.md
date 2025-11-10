# SnapMap Deployment Guide

**Version:** 2.0.0
**Last Updated:** November 7, 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Security Configuration](#security-configuration)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Storage: 10 GB
- OS: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)

**Recommended** (Production):
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB (SSD)
- OS: Linux (Ubuntu 22.04 LTS)

### Software Requirements

**Backend**:
- Python 3.11+ (tested with 3.11 and 3.12)
- pip 23.0+
- Virtual environment tool (venv or virtualenv)

**Frontend**:
- Node.js 18.0+ (LTS recommended)
- npm 9.0+ or yarn 1.22+

**Database**:
- ChromaDB (installed via pip, no separate server needed)

**Optional**:
- Docker 24.0+ (for containerized deployment)
- nginx 1.18+ (for reverse proxy)
- PostgreSQL 14+ (for future persistent storage)

---

## Development Deployment

### Quick Start (5 minutes)

**1. Clone Repository**
```bash
git clone https://github.com/your-org/snapmap.git
cd snapmap
```

**2. Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build vector database (CRITICAL!)
python build_vector_db.py

# Start backend server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**3. Frontend Setup** (new terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**4. Access Application**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

### Development Environment Variables

Create `backend/.env`:
```bash
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# Optional: Encryption key for SFTP credentials
ENCRYPTION_KEY=your-generated-key-here

# Optional: Rate limiting
RATE_LIMIT_PER_MINUTE=100
```

**Generate Encryption Key**:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## Production Deployment

### Method 1: Traditional Deployment

#### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install nginx
sudo apt install nginx -y

# Create application user
sudo useradd -m -s /bin/bash snapmap
sudo su - snapmap
```

#### Step 2: Deploy Backend

```bash
cd /home/snapmap
git clone https://github.com/your-org/snapmap.git
cd snapmap/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build vector database
python build_vector_db.py

# Create .env file
cat > .env << EOF
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
RATE_LIMIT_PER_MINUTE=100
EOF
```

#### Step 3: Create Systemd Service

**Create** `/etc/systemd/system/snapmap-backend.service`:
```ini
[Unit]
Description=SnapMap Backend API
After=network.target

[Service]
Type=simple
User=snapmap
WorkingDirectory=/home/snapmap/snapmap/backend
Environment="PATH=/home/snapmap/snapmap/backend/venv/bin"
ExecStart=/home/snapmap/snapmap/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable snapmap-backend
sudo systemctl start snapmap-backend
sudo systemctl status snapmap-backend
```

#### Step 4: Build Frontend

```bash
cd /home/snapmap/snapmap/frontend

# Install dependencies
npm ci --production

# Build for production
npm run build

# Output is in: dist/
```

#### Step 5: Configure nginx

**Create** `/etc/nginx/sites-available/snapmap`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration (using Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend (React SPA)
    location / {
        root /home/snapmap/snapmap/frontend/dist;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for large file uploads
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        client_max_body_size 100M;
    }

    # API Documentation (optional - disable in production)
    location /api/docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
```

**Enable and Reload**:
```bash
sudo ln -s /etc/nginx/sites-available/snapmap /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 6: SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

---

### Method 2: Docker Deployment

#### Docker Compose Configuration

**Create** `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: snapmap-backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - CORS_ORIGINS=${CORS_ORIGINS}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - ./backend/chroma_db:/app/chroma_db
      - ./backend/app/schemas:/app/app/schemas
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: snapmap-frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./ssl:/etc/nginx/ssl

volumes:
  chroma_db:
```

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Build vector database
RUN python build_vector_db.py

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Deploy**:
```bash
# Create .env file
cat > .env << EOF
CORS_ORIGINS=https://yourdomain.com
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EOF

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

---

## Environment Configuration

### Backend Environment Variables

**File**: `backend/.env`

```bash
# Environment (development | production)
ENVIRONMENT=production

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
ENCRYPTION_KEY=your-fernet-key-here

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# File Upload Limits
MAX_FILE_SIZE_MB=100
MAX_ROW_COUNT=100000

# Session Configuration
SESSION_TIMEOUT_MINUTES=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/snapmap/backend.log

# Optional: External Services
# GEMINI_API_KEY=your-api-key  # For future AI features
```

### Frontend Environment Variables

**File**: `frontend/.env.production`

```bash
VITE_API_BASE_URL=https://yourdomain.com
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
```

---

## Security Configuration

### 1. Firewall Rules

```bash
# Allow SSH (if managing remotely)
sudo ufw allow 22/tcp

# Allow HTTP (will redirect to HTTPS)
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 2. Security Headers

Security headers are configured in `backend/app/middleware/security_headers.py`:

```python
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; ...",
}
```

### 3. HTTPS/TLS

**Recommended**: Use Let's Encrypt (free, automated)

**Manual Certificate**:
```bash
# Generate self-signed (development only)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/snapmap.key \
  -out /etc/ssl/certs/snapmap.crt
```

### 4. Credential Encryption

SFTP credentials are encrypted with AES-256 (Fernet):

```python
from cryptography.fernet import Fernet

# Generate key (do this once)
key = Fernet.generate_key()
print(key.decode())  # Add to .env as ENCRYPTION_KEY

# Encryption/Decryption is handled automatically
```

---

## Performance Tuning

### Backend (Uvicorn)

**Workers**: Set based on CPU cores
```bash
# Formula: (2 x CPU_CORES) + 1
# For 4-core server: 9 workers
uvicorn main:app --workers 9 --host 0.0.0.0 --port 8000
```

**Timeouts**:
```python
# In main.py
app = FastAPI(timeout=300)  # 5 minutes for large files
```

### nginx

**Connection Tuning** (`/etc/nginx/nginx.conf`):
```nginx
worker_processes auto;
worker_connections 1024;

http {
    # Keep-alive
    keepalive_timeout 65;
    keepalive_requests 100;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 100M;

    # Caching
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;
}
```

### Database (ChromaDB)

**Persist to Disk** (default):
```python
# ChromaDB automatically persists to disk
# Location: backend/chroma_db/
# No configuration needed
```

**Memory Optimization**:
- Vector DB loads on startup (~50MB)
- Query cache improves performance
- No ongoing memory growth

---

## Monitoring & Logging

### Application Logging

**Configure Logging** (`backend/main.py`):
```python
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory
os.makedirs("/var/log/snapmap", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            "/var/log/snapmap/backend.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
```

### System Monitoring

**Install Prometheus + Grafana** (optional):
```bash
# Install Prometheus
sudo apt install prometheus -y

# Install Grafana
sudo apt install grafana -y

# Start services
sudo systemctl start prometheus grafana-server
sudo systemctl enable prometheus grafana-server
```

**Add Metrics Endpoint** (`backend/main.py`):
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### Health Checks

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime_seconds": 86400,
  "vector_db_loaded": true
}
```

**Monitor with cron**:
```bash
# Add to crontab
*/5 * * * * curl -f http://localhost:8000/health || systemctl restart snapmap-backend
```

---

## Backup & Recovery

### What to Backup

1. **Vector Database**: `backend/chroma_db/`
2. **Schema Definitions**: `backend/app/schemas/`
3. **SFTP Credentials**: `backend/sftp_credentials.json` (encrypted)
4. **Environment Config**: `backend/.env`

### Backup Script

**Create** `/home/snapmap/backup.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/backups/snapmap"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/snapmap/snapmap"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup vector database
tar -czf "$BACKUP_DIR/chroma_db_$DATE.tar.gz" "$APP_DIR/backend/chroma_db"

# Backup schemas
tar -czf "$BACKUP_DIR/schemas_$DATE.tar.gz" "$APP_DIR/backend/app/schemas"

# Backup SFTP credentials (already encrypted)
if [ -f "$APP_DIR/backend/sftp_credentials.json" ]; then
  cp "$APP_DIR/backend/sftp_credentials.json" "$BACKUP_DIR/sftp_credentials_$DATE.json"
fi

# Backup .env (WARNING: Contains sensitive data)
cp "$APP_DIR/backend/.env" "$BACKUP_DIR/env_$DATE.txt"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Schedule Daily Backups**:
```bash
# Add to crontab
0 2 * * * /home/snapmap/backup.sh >> /var/log/snapmap/backup.log 2>&1
```

### Recovery

```bash
# Stop services
sudo systemctl stop snapmap-backend

# Restore vector database
cd /home/snapmap/snapmap/backend
tar -xzf /backups/snapmap/chroma_db_20251107.tar.gz

# Restore schemas
tar -xzf /backups/snapmap/schemas_20251107.tar.gz

# Restore credentials
cp /backups/snapmap/sftp_credentials_20251107.json ./sftp_credentials.json

# Restart services
sudo systemctl start snapmap-backend
```

---

## Scaling

### Vertical Scaling (Single Server)

**Increase Resources**:
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: SSD with 100+ GB

**Optimize Uvicorn**:
```bash
# More workers
uvicorn main:app --workers 17 --host 0.0.0.0 --port 8000
```

### Horizontal Scaling (Multiple Servers)

**Load Balancer** (nginx):
```nginx
upstream snapmap_backend {
    least_conn;
    server 10.0.1.10:8000;
    server 10.0.1.11:8000;
    server 10.0.1.12:8000;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://snapmap_backend;
    }
}
```

**Shared Storage**:
- Use NFS for shared vector database
- Redis for session management (future)
- PostgreSQL for persistent data (future)

---

## Troubleshooting

### Backend Won't Start

**Check Logs**:
```bash
sudo journalctl -u snapmap-backend -n 50 -f
```

**Common Issues**:
1. **Port already in use**: Change port or kill conflicting process
2. **Vector DB not built**: Run `python build_vector_db.py`
3. **Import errors**: Activate virtual environment and reinstall dependencies

### High Memory Usage

**Check Process**:
```bash
ps aux | grep python
```

**Solutions**:
- Reduce number of workers
- Implement request queuing
- Add swap space (temporary)

### Slow Performance

**Check Metrics**:
```bash
# CPU usage
top

# Disk I/O
iostat -x 1

# Network
iftop
```

**Solutions**:
- Enable nginx caching
- Increase worker count
- Use SSD storage

---

## Deployment Checklist

### Pre-Deployment
- [ ] Server meets system requirements
- [ ] Python 3.11+ and Node.js 18+ installed
- [ ] SSL certificate obtained
- [ ] Environment variables configured
- [ ] Firewall rules applied

### Deployment
- [ ] Backend dependencies installed
- [ ] Vector database built
- [ ] Frontend built for production
- [ ] nginx configured
- [ ] Systemd service created
- [ ] Services started and enabled

### Post-Deployment
- [ ] Health endpoint returns 200 OK
- [ ] Test file upload
- [ ] Test auto-mapping
- [ ] Test CSV export
- [ ] Test XML export
- [ ] Test SFTP upload
- [ ] Review logs for errors
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Document deployment

### Security Checklist
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Firewall configured
- [ ] Credentials encrypted
- [ ] API docs disabled in production

---

*Deployment Guide Version: 2.0.0*
*Last Updated: November 7, 2025*
*Author: SnapMap Operations Team*
