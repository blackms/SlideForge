"""
Import all models to make them available from the models module.
This is useful for SQLAlchemy to discover all models.
"""
from slideforge.db.base import Base
from slideforge.db.models.user import User
from slideforge.db.models.document import Document, DocumentStatus
from slideforge.db.models.extracted_content import ExtractedContent
from slideforge.db.models.presentation import Presentation, PresentationStatus
from slideforge.db.models.job import Job, JobStatus

# List of all models for easy access
__all__ = [
    "Base",
    "User",
    "Document",
    "DocumentStatus",
    "ExtractedContent",
    "Presentation",
    "PresentationStatus",
    "Job",
    "JobStatus",
]