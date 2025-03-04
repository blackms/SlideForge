"""
ExtractedContent model for storing extracted information from documents.
"""
from sqlalchemy import Column, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from slideforge.db.base import BaseModel, TimestampMixin


class ExtractedContent(BaseModel, TimestampMixin):
    """
    Model for storing content extracted and processed from documents.
    Stores both the raw extracted text and the structured content.
    """
    __tablename__ = "extracted_contents"
    
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content_text = Column(Text, nullable=True)  # Raw extracted text
    content_json = Column(JSON, nullable=True)  # Structured content as JSON
    summary = Column(Text, nullable=True)  # Summary of the document
    keywords = Column(Text, nullable=True)  # Comma-separated keywords
    
    # Relationships
    document = relationship("Document", back_populates="extracted_contents")
    presentations = relationship("Presentation", back_populates="extracted_content", cascade="all, delete-orphan")
