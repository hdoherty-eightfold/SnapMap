"""
ETL UI Backend - Main Application
FastAPI server for HR data transformation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="ETL UI Backend",
    description="HR Data Transformation API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api.endpoints import schema, automapping, upload, transform, validate, ai_inference, sftp, config, review

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(schema.router, prefix="/api", tags=["schema"])
app.include_router(automapping.router, prefix="/api", tags=["automapping"])
app.include_router(transform.router, prefix="/api", tags=["transform"])
app.include_router(validate.router, prefix="/api", tags=["validate"])
app.include_router(ai_inference.router, prefix="/api/ai", tags=["ai-inference"])
app.include_router(sftp.router, prefix="/api/sftp", tags=["sftp"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(review.router, prefix="/api", tags=["review"])


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "ETL UI Backend API",
        "version": "1.0.0",
        "status": "running",
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
