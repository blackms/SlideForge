"""
Job model for tracking processing tasks.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from slideforge.db.base import BaseModel, TimestampMixin


class JobStatus(enum.Enum):
    """Enumeration of possible job statuses."""
    PENDING = "pending"
    EXTRACTING = "extracting"
    GENERATING = "generating"
    STYLING = "styling"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(BaseModel, TimestampMixin):
    """
    Model for tracking processing jobs through the system.
    A job represents the entire process from document upload to final presentation.
    """
    __tablename__ = "jobs"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    presentation_id = Column(Integer, ForeignKey("presentations.id"), nullable=True)
    
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    settings = Column(JSON, nullable=True)  # Job-specific settings
    error_message = Column(Text, nullable=True)
    
    # Timing information
    started_at = Column(DateTime, nullable=True)
    extraction_started_at = Column(DateTime, nullable=True)
    extraction_completed_at = Column(DateTime, nullable=True)
    generation_started_at = Column(DateTime, nullable=True)
    generation_completed_at = Column(DateTime, nullable=True)
    styling_started_at = Column(DateTime, nullable=True)
    styling_completed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    document = relationship("Document", back_populates="jobs")
    presentation = relationship("Presentation", back_populates="jobs")
    
    def start_job(self):
        """Mark the job as started."""
        self.status = JobStatus.EXTRACTING
        self.started_at = datetime.utcnow()
    
    def start_extraction(self):
        """Mark extraction as started."""
        self.status = JobStatus.EXTRACTING
        self.extraction_started_at = datetime.utcnow()
    
    def complete_extraction(self):
        """Mark extraction as completed."""
        self.extraction_completed_at = datetime.utcnow()
        self.status = JobStatus.GENERATING
    
    def start_generation(self):
        """Mark generation as started."""
        self.status = JobStatus.GENERATING
        self.generation_started_at = datetime.utcnow()
    
    def complete_generation(self):
        """Mark generation as completed."""
        self.generation_completed_at = datetime.utcnow()
        self.status = JobStatus.STYLING
    
    def start_styling(self):
        """Mark styling as started."""
        self.status = JobStatus.STYLING
        self.styling_started_at = datetime.utcnow()
    
    def complete_styling(self):
        """Mark styling as completed."""
        self.styling_completed_at = datetime.utcnow()
        self.complete_job()
    
    def complete_job(self):
        """Mark the job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def fail_job(self, error_message):
        """Mark the job as failed with an error message."""
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
    
    def cancel_job(self):
        """Mark the job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()