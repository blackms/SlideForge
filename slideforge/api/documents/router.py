"""
Router for document operations.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session

from slideforge.api.auth.utils import get_current_user
from slideforge.api.documents import crud
from slideforge.db.session import get_db
from slideforge.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentWithCount
from slideforge.schemas.user import User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=Document)
async def create_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
) -> Any:
    """
    Upload a new document.
    """
    # Validate file type
    file_type = file.filename.split(".")[-1].lower()
    supported_types = ["pdf", "docx", "txt"]
    
    if file_type not in supported_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_type}. Supported types: {', '.join(supported_types)}",
        )
    
    # Create document
    document = await crud.create_document(db, current_user.id, file)
    return document


@router.get("", response_model=DocumentWithCount)
def read_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by document status"),
) -> Any:
    """
    Retrieve documents.
    """
    documents, total = crud.get_documents(
        db, user_id=current_user.id, skip=skip, limit=limit, status_filter=status
    )
    return {"total": total, "documents": documents}


@router.get("/{document_id}", response_model=Document)
def read_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_id: int,
) -> Any:
    """
    Get document by ID.
    """
    document = crud.get_document(db, document_id=document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check ownership
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return document


@router.put("/{document_id}", response_model=Document)
def update_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_id: int,
    document_in: DocumentUpdate,
) -> Any:
    """
    Update a document.
    """
    document = crud.get_document(db, document_id=document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check ownership
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    document = crud.update_document(db, document=document, obj_in=document_in)
    return document


@router.delete("/{document_id}", response_model=Document)
def delete_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_id: int,
) -> Any:
    """
    Delete a document.
    """
    document = crud.get_document(db, document_id=document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check ownership
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    document = crud.delete_document(db, document_id=document_id)
    return document