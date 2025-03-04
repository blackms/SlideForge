"""
Router for job operations.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from slideforge.api.auth.utils import get_current_user
from slideforge.api.jobs import crud
from slideforge.db.session import get_db
from slideforge.schemas.job import Job, JobCreate, JobUpdate, JobStatusUpdate, JobWithCount
from slideforge.schemas.user import User
from slideforge.tasks.orchestrator import start_job_processing

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=Job)
def create_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    job_in: JobCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create a new job for document processing.
    """
    # Check if the document exists and belongs to the user
    document = crud.get_document_for_user(db, document_id=job_in.document_id, user_id=current_user.id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or doesn't belong to you",
        )
    
    # Create job
    job = crud.create_job(db, obj_in=job_in, user_id=current_user.id)
    
    # Start job processing in background
    background_tasks.add_task(start_job_processing, job.id)
    
    return job


@router.get("", response_model=JobWithCount)
def read_jobs(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by job status"),
) -> Any:
    """
    Retrieve jobs.
    """
    jobs, total = crud.get_jobs(
        db, user_id=current_user.id, skip=skip, limit=limit, status_filter=status
    )
    return {"total": total, "jobs": jobs}


@router.get("/{job_id}", response_model=Job)
def read_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    job_id: int,
) -> Any:
    """
    Get job by ID.
    """
    job = crud.get_job(db, job_id=job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Check ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return job


@router.put("/{job_id}", response_model=Job)
def update_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    job_id: int,
    job_in: JobUpdate,
) -> Any:
    """
    Update a job.
    """
    job = crud.get_job(db, job_id=job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Check ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    job = crud.update_job(db, job=job, obj_in=job_in)
    return job


@router.delete("/{job_id}", response_model=Job)
def cancel_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    job_id: int,
) -> Any:
    """
    Cancel a job.
    """
    job = crud.get_job(db, job_id=job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Check ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    job = crud.cancel_job(db, job_id=job_id)
    return job