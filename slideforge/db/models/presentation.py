"""
Presentation model for storing generated presentations.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from slideforge.db.base import BaseModel, TimestampMixin


class PresentationStatus(enum.Enum):
    """Enumeration of possible presentation statuses."""
    PENDING = "pending"
    GENERATING = "generating"
    STYLING = "styling"
    COMPLETED = "completed"
    FAILED = "failed"


class Presentation(BaseModel, TimestampMixin):
    """
    Model for storing information about generated presentations.
    """
    __tablename__ = "presentations"
    
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    extracted_content_id = Column(Integer, ForeignKey("extracted_contents.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    status = Column(Enum(PresentationStatus), default=PresentationStatus.PENDING, nullable=False)
    style_applied = Column(String(100), nullable=True)
    thumbnail_path = Column(String(255), nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string with additional metadata
    
    # Relationships
    document = relationship("Document", back_populates="presentations")
    extracted_content = relationship("ExtractedContent", back_populates="presentations")
    jobs = relationship("Job", back_populates="presentation", cascade="all, delete-orphan")
