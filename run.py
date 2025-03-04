"""
Entry point for running the SlideForge application.
"""
import uvicorn
import os
import sys

from slideforge.core.config import settings


def main():
    """
    Main entry point for the application.
    """
    # Ensure required directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "slideforge.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()