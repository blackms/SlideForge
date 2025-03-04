"""
Router for presentation operations.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from slideforge.api.auth.utils import get_current_user
from slideforge.api.presentations import crud
from slideforge.db.session import get_db
from slideforge.schemas.presentation import Presentation, PresentationUpdate, PresentationWithCount
from slideforge.schemas.user import User

router = APIRouter(prefix="/presentations", tags=["presentations"])


@router.get("", response_model=PresentationWithCount)
def read_presentations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by presentation status"),
) -> Any:
    """
    Retrieve presentations.
    """
    presentations, total = crud.get_presentations(
        db, user_id=current_user.id, skip=skip, limit=limit, status_filter=status
    )
    return {"total": total, "presentations": presentations}


@router.get("/{presentation_id}", response_model=Presentation)
def read_presentation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    presentation_id: int,
) -> Any:
    """
    Get presentation by ID.
    """
    presentation = crud.get_presentation(db, presentation_id=presentation_id)
    
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        )
    
    # Check ownership through document
    if presentation.document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return presentation


@router.get("/{presentation_id}/download")
def download_presentation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    presentation_id: int,
) -> Any:
    """
    Download a presentation file.
    """
    presentation = crud.get_presentation(db, presentation_id=presentation_id)
    
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        )
    
    # Check ownership through document
    if presentation.document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if file exists
    if not os.path.exists(presentation.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation file not found",
        )
    
    # Return file
    return FileResponse(
        path=presentation.file_path,
        filename=presentation.filename,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


@router.get("/{presentation_id}/thumbnail")
def get_presentation_thumbnail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    presentation_id: int,
) -> Any:
    """
    Get presentation thumbnail.
    """
    presentation = crud.get_presentation(db, presentation_id=presentation_id)
    
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        )
    
    # Check ownership through document
    if presentation.document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if thumbnail exists
    if not presentation.thumbnail_path or not os.path.exists(presentation.thumbnail_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found",
        )
    
    # Return thumbnail file
    return FileResponse(
        path=presentation.thumbnail_path,
        media_type="image/png",  # Assuming thumbnails are PNG format
    )


@router.put("/{presentation_id}", response_model=Presentation)
def update_presentation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    presentation_id: int,
    presentation_in: PresentationUpdate,
) -> Any:
    """
    Update a presentation.
    """
    presentation = crud.get_presentation(db, presentation_id=presentation_id)
    
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        )
    
    # Check ownership through document
    if presentation.document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    presentation = crud.update_presentation(db, presentation=presentation, obj_in=presentation_in)
    return presentation


@router.delete("/{presentation_id}", response_model=Presentation)
def delete_presentation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    presentation_id: int,
) -> Any:
    """
    Delete a presentation.
    """
    presentation = crud.get_presentation(db, presentation_id=presentation_id)
    
    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found",
        )
    
    # Check ownership through document
    if presentation.document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    presentation = crud.delete_presentation(db, presentation_id=presentation_id)
    return presentation