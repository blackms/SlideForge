"""
Pydantic schemas for presentation data.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from slideforge.db.models.presentation import PresentationStatus


class PresentationBase(BaseModel):
    """Base schema for presentation data."""
    filename: str


class PresentationCreate(PresentationBase):
    """Schema for presentation creation."""
    document_id: int
    extracted_content_id: int


class PresentationUpdate(BaseModel):
    """Schema for presentation update."""
    filename: Optional[str] = None
    status: Optional[PresentationStatus] = None
    style_applied: Optional[str] = None
    metadata: Optional[str] = None


class PresentationInDBBase(PresentationBase):
    """Base schema for presentation in database."""
    id: int
    document_id: int
    extracted_content_id: int
    file_path: str
    status: PresentationStatus
    style_applied: Optional[str] = None
    thumbnail_path: Optional[str] = None
    metadata: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Presentation(PresentationInDBBase):
    """Schema for presentation response."""
    pass


class PresentationWithCount(BaseModel):
    """Schema for pagination response with presentations."""
    total: int
    presentations: List[Presentation]