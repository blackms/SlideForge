"""
Pydantic schemas for job data.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from slideforge.db.models.job import JobStatus


class JobBase(BaseModel):
    """Base schema for job data."""
    document_id: int


class JobCreate(JobBase):
    """Schema for job creation."""
    settings: Optional[Dict[str, Any]] = None


class JobUpdate(BaseModel):
    """Schema for job update."""
    status: Optional[JobStatus] = None
    settings: Optional[Dict[str, Any]] = None
    presentation_id: Optional[int] = None
    error_message: Optional[str] = None


class JobInDBBase(JobBase):
    """Base schema for job in database."""
    id: int
    user_id: int
    presentation_id: Optional[int] = None
    status: JobStatus
    settings: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Timing information
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    extraction_started_at: Optional[datetime] = None
    extraction_completed_at: Optional[datetime] = None
    generation_started_at: Optional[datetime] = None
    generation_completed_at: Optional[datetime] = None
    styling_started_at: Optional[datetime] = None
    styling_completed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Job(JobInDBBase):
    """Schema for job response."""
    pass


class JobWithCount(BaseModel):
    """Schema for pagination response with jobs."""
    total: int
    jobs: List[Job]


class JobStatusUpdate(BaseModel):
    """Schema for updating job status."""
    status: JobStatus
    error_message: Optional[str] = None