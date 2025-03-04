"""
Document model for storing uploaded files information.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from slideforge.db.base import BaseModel, TimestampMixin


class DocumentStatus(enum.Enum):
    """Enumeration of possible document processing statuses."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    FAILED = "failed"


class Document(BaseModel, TimestampMixin):
    """
    Document model for storing information about uploaded files.
    """
    __tablename__ = "documents"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # PDF, DOCX, TXT, etc.
    file_size = Column(Integer, nullable=False)  # Size in bytes
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON string with additional metadata
    
    # Relationships
    user = relationship("User", back_populates="documents")
    extracted_contents = relationship("ExtractedContent", back_populates="document", cascade="all, delete-orphan")
    presentations = relationship("Presentation", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="document", cascade="all, delete-orphan")
