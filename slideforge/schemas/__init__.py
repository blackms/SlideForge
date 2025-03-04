"""
Import all schemas to make them available from the schemas module.
"""
from slideforge.schemas.user import User, UserCreate, UserUpdate, Token
from slideforge.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentWithCount
from slideforge.schemas.extracted_content import ExtractedContent, ExtractedContentCreate, ExtractedContentUpdate
from slideforge.schemas.presentation import Presentation, PresentationCreate, PresentationUpdate
from slideforge.schemas.job import Job, JobCreate, JobUpdate, JobStatusUpdate, JobWithCount

# List of all schemas for easy access
__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "Token",
    "Document",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentWithCount",
    "ExtractedContent",
    "ExtractedContentCreate",
    "ExtractedContentUpdate",
    "Presentation",
    "PresentationCreate",
    "PresentationUpdate",
    "Job",
    "JobCreate",
    "JobUpdate",
    "JobStatusUpdate",
    "JobWithCount",
]