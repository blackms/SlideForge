"""
CRUD operations for presentations.
"""
import os
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from slideforge.db.models.presentation import Presentation, PresentationStatus
from slideforge.schemas.presentation import PresentationUpdate


def get_presentation(db: Session, presentation_id: int) -> Optional[Presentation]:
    """
    Get a presentation by ID.
    
    Args:
        db: Database session
        presentation_id: ID of the presentation to retrieve
    
    Returns:
        Optional[Presentation]: The presentation if found, None otherwise
    """
    return db.query(Presentation).filter(Presentation.id == presentation_id).first()


def get_presentations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
) -> Tuple[List[Presentation], int]:
    """
    Get presentations for a user with optional filters.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status_filter: Optional status to filter by
    
    Returns:
        Tuple[List[Presentation], int]: List of presentations and total count
    """
    # We need to join with document to filter by user_id
    query = (
        db.query(Presentation)
        .join(Presentation.document)
        .filter(Presentation.document.has(user_id=user_id))
    )
    
    # Apply status filter if provided
    if status_filter:
        try:
            status = PresentationStatus(status_filter)
            query = query.filter(Presentation.status == status)
        except ValueError:
            # Invalid status, ignore the filter
            pass
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    presentations = query.order_by(Presentation.created_at.desc()).offset(skip).limit(limit).all()
    
    return presentations, total


def update_presentation(
    db: Session, presentation: Presentation, obj_in: PresentationUpdate
) -> Presentation:
    """
    Update a presentation.
    
    Args:
        db: Database session
        presentation: Presentation to update
        obj_in: Update data
    
    Returns:
        Presentation: Updated presentation
    """
    update_data = obj_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(presentation, field, value)
    
    db.add(presentation)
    db.commit()
    db.refresh(presentation)
    return presentation


def delete_presentation(db: Session, presentation_id: int) -> Presentation:
    """
    Delete a presentation.
    
    Args:
        db: Database session
        presentation_id: ID of the presentation to delete
    
    Returns:
        Presentation: Deleted presentation
    """
    presentation = get_presentation(db, presentation_id=presentation_id)
    
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        )
    
    # Delete the file(s)
    try:
        # Delete presentation file
        if os.path.exists(presentation.file_path):
            os.remove(presentation.file_path)
        
        # Delete thumbnail if it exists
        if presentation.thumbnail_path and os.path.exists(presentation.thumbnail_path):
            os.remove(presentation.thumbnail_path)
    except Exception as e:
        # Log the error but continue with database deletion
        print(f"Error deleting presentation file(s): {str(e)}")
    
    # Delete from database
    db.delete(presentation)
    db.commit()
    
    return presentation