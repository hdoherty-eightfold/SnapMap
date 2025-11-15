"""
ETL UI Backend - Main Application
FastAPI server for HR data transformation
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import security middleware
from app.middleware import SecurityHeadersMiddleware, RateLimitMiddleware

# Determine environment
ENV = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENV == "production"

# Create FastAPI app
app = FastAPI(
    title="Proficiency Studio API",
    description="AI-Powered Skills Proficiency Assessment & HR Data Transformation",
    version="2.0.0",
    # Disable docs in production for security
    docs_url="/api/docs" if not IS_PRODUCTION else None,
    redoc_url="/api/redoc" if not IS_PRODUCTION else None
)

# Configure CORS based on environment
if IS_PRODUCTION:
    # Production: Use environment variable for allowed origins
    allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
else:
    # Development: Allow localhost origins
    allowed_origins = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server (alternative port)
        "http://localhost:5175",  # Vite dev server (alternative port)
        "http://localhost:3000",  # Alternative port
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    # Restrict methods to only what's needed
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # Specify allowed headers explicitly
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Import routers
from app.api.endpoints import (
    schema, automapping, upload, transform, validate,
    ai_inference, sftp, config, review,
    # New Proficiency Studio endpoints
    rag, roles, export, auth, environments, skills, proficiency, llm
)

# Include existing routers (SnapMap functionality)
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(schema.router, prefix="/api", tags=["schema"])
app.include_router(automapping.router, prefix="/api", tags=["automapping"])
app.include_router(transform.router, prefix="/api", tags=["transform"])
app.include_router(validate.router, prefix="/api", tags=["validate"])
app.include_router(ai_inference.router, prefix="/api/ai", tags=["ai-inference"])
app.include_router(sftp.router, prefix="/api/sftp", tags=["sftp"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(review.router, prefix="/api", tags=["review"])

# Include new Proficiency Studio routers
app.include_router(auth.router, tags=["auth"])  # Authentication
app.include_router(environments.router, tags=["environments"])  # Environment Management
app.include_router(skills.router, tags=["skills"])  # Skills Extraction
app.include_router(proficiency.router, tags=["proficiency"])  # Proficiency Assessment
app.include_router(llm.router, tags=["llm"])  # LLM Management and Key Testing
app.include_router(rag.router, tags=["rag"])  # RAG Pipeline
app.include_router(roles.router, tags=["roles"])  # Role CRUD
app.include_router(export.router, tags=["export"])  # Export & History


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Proficiency Studio API",
        "description": "AI-Powered Skills Proficiency Assessment & HR Data Transformation",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "RAG-enhanced skill assessment (90-95% accuracy)",
            "Multi-LLM support (OpenAI, Gemini, Claude, Grok)",
            "Role CRUD operations",
            "Export & History management",
            "HR data transformation"
        ],
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "The requested resource was not found"
            },
            "status": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred"
            },
            "status": 500
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Security: Don't bind to 0.0.0.0 in development, use 127.0.0.1
    # Only bind to 0.0.0.0 in production when behind reverse proxy
    host = "0.0.0.0" if IS_PRODUCTION else "127.0.0.1"

    # Security: Disable auto-reload in production
    reload = not IS_PRODUCTION

    uvicorn.run(app, host=host, port=8000, reload=reload)
