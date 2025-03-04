"""
CRUD operations for documents.
"""
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from slideforge.core.config import settings
from slideforge.db.models.document import Document, DocumentStatus
from slideforge.schemas.document import DocumentUpdate


async def create_document(
    db: Session, user_id: int, file: UploadFile
) -> Document:
    """
    Create a new document from an uploaded file.
    
    Args:
        db: Database session
        user_id: ID of the user uploading the document
        file: Uploaded file
    
    Returns:
        Document: Created document object
    """
    # Extract file info
    filename = file.filename
    file_type = filename.split(".")[-1].lower()
    
    # Create unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4().hex}.{file_type}"
    
    # Create user directory if it doesn't exist
    user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Define file path
    file_path = os.path.join(user_upload_dir, unique_filename)
    
    # Read and save the file
    contents = await file.read()
    file_size = len(contents)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create document in database
    db_obj = Document(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        status=DocumentStatus.UPLOADED,
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """
    Get a document by ID.
    
    Args:
        db: Database session
        document_id: ID of the document to retrieve
    
    Returns:
        Optional[Document]: The document if found, None otherwise
    """
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    status_filter: Optional[str] = None,
) -> Tuple[List[Document], int]:
    """
    Get documents for a user with optional filters.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status_filter: Optional status to filter by
    
    Returns:
        Tuple[List[Document], int]: List of documents and total count
    """
    query = db.query(Document).filter(Document.user_id == user_id)
    
    # Apply status filter if provided
    if status_filter:
        try:
            status = DocumentStatus(status_filter)
            query = query.filter(Document.status == status)
        except ValueError:
            # Invalid status, ignore the filter
            pass
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    return documents, total


def update_document(
    db: Session, document: Document, obj_in: DocumentUpdate
) -> Document:
    """
    Update a document.
    
    Args:
        db: Database session
        document: Document to update
        obj_in: Update data
    
    Returns:
        Document: Updated document
    """
    update_data = obj_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, document_id: int) -> Document:
    """
    Delete a document.
    
    Args:
        db: Database session
        document_id: ID of the document to delete
    
    Returns:
        Document: Deleted document
    """
    document = get_document(db, document_id=document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Delete the file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log the error but continue with database deletion
        print(f"Error deleting file {document.file_path}: {str(e)}")
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return document
