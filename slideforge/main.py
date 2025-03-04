"""
Main FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from slideforge.core.config import settings
from slideforge.api.auth import router as auth_router
from slideforge.api.documents import router as documents_router
from slideforge.api.jobs import router as jobs_router
from slideforge.api.presentations import router as presentations_router


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A multi-agent system for automated PowerPoint presentation generation",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload and temporary directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)

# Mount static files directories
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Include API routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(documents_router.router, prefix=settings.API_V1_STR)
app.include_router(jobs_router.router, prefix=settings.API_V1_STR)
app.include_router(presentations_router.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": "0.1.0",
        "message": "Welcome to SlideForge API",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "slideforge.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )