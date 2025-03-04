"""
Pydantic schemas for document data.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from slideforge.db.models.document import DocumentStatus


class DocumentBase(BaseModel):
    """Base schema for document data."""
    filename: str
    file_type: str


class DocumentCreate(DocumentBase):
    """Schema for document creation."""
    pass


class DocumentUpdate(BaseModel):
    """Schema for document update."""
    filename: Optional[str] = None
    status: Optional[DocumentStatus] = None
    metadata: Optional[str] = None


class DocumentInDBBase(DocumentBase):
    """Base schema for document in database."""
    id: int
    user_id: int
    file_path: str
    file_size: int
    status: DocumentStatus
    metadata: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Document(DocumentInDBBase):
    """Schema for document response."""
    pass


class DocumentWithCount(BaseModel):
    """Schema for pagination response with documents."""
    total: int
    documents: List[Document]
