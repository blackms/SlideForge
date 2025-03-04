"""
Pydantic schemas for extracted content data.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ExtractedContentBase(BaseModel):
    """Base schema for extracted content data."""
    document_id: int


class ExtractedContentCreate(ExtractedContentBase):
    """Schema for extracted content creation."""
    content_text: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None


class ExtractedContentUpdate(BaseModel):
    """Schema for extracted content update."""
    content_text: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None


class ExtractedContentInDBBase(ExtractedContentBase):
    """Base schema for extracted content in database."""
    id: int
    content_text: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ExtractedContent(ExtractedContentInDBBase):
    """Schema for extracted content response."""
    pass


class ExtractedContentWithCount(BaseModel):
    """Schema for pagination response with extracted contents."""
    total: int
    extracted_contents: List[ExtractedContent]