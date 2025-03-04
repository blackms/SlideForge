"""
Configuration settings for the SlideForge application.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with defaults.
    """
    # Base
    APP_NAME: str = "SlideForge"
    API_V1_STR: str = "/api"
    DEBUG: bool = True
    
    # Project directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    TEMP_DIR: Path = BASE_DIR / "temp"
    
    # Security
    SECRET_KEY: str = "development_secret_key_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # Database
    SQLITE_DATABASE_URI: str = f"sqlite:///{BASE_DIR}/slideforge.db"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "slideforge"
    DATABASE_URI: Optional[str] = None
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "gpt-4"
    EXTRACTION_PROMPT_TEMPLATE: str = "Extract key information from the following document: {document_text}"
    
    # Storage
    STORAGE_TYPE: str = "local"  # Options: local, s3
    S3_BUCKET_NAME: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def database_uri(self) -> str:
        """
        Get database URI based on configuration.
        For development, use SQLite. For production, use PostgreSQL.
        """
        if self.DATABASE_URI:
            return self.DATABASE_URI
        
        if self.DEBUG:
            # Create uploads and temp directories if they don't exist
            self.UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
            self.TEMP_DIR.mkdir(exist_ok=True, parents=True)
            return self.SQLITE_DATABASE_URI
        
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

# Create global settings instance
settings = Settings()