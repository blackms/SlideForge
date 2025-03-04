"""
CRUD operations for jobs.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from slideforge.db.models.document import Document
from slideforge.db.models.job import Job, JobStatus
from slideforge.schemas.job import JobCreate, JobUpdate


def get_document_for_user(db: Session, document_id: int, user_id: int) -> Optional[Document]:
    """
    Get a document that belongs to a specific user.
    
    Args:
        db: Database session
        document_id: ID of the document
        user_id: ID of the user
    
    Returns:
        Optional[Document]: The document if found and belongs to the user, None otherwise
    """
    return db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()


def get_job(db: Session, job_id: int) -> Optional[Job]:
    """
    Get a job by ID.
    
    Args:
        db: Database session
        job_id: ID of the job
    
    Returns:
        Optional[Job]: The job if found, None otherwise
    """
    return db.query(Job).filter(Job.id == job_id).first()


def get_jobs(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
) -> Tuple[List[Job], int]:
    """
    Get jobs for a user with optional filters.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status_filter: Optional status to filter by
    
    Returns:
        Tuple[List[Job], int]: List of jobs and total count
    """
    query = db.query(Job).filter(Job.user_id == user_id)
    
    # Apply status filter if provided
    if status_filter:
        try:
            status = JobStatus(status_filter)
            query = query.filter(Job.status == status)
        except ValueError:
            # Invalid status, ignore the filter
            pass
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
    
    return jobs, total


def create_job(db: Session, obj_in: JobCreate, user_id: int) -> Job:
    """
    Create a new job.
    
    Args:
        db: Database session
        obj_in: Job creation data
        user_id: ID of the user creating the job
    
    Returns:
        Job: Created job object
    """
    # Create job in database
    db_obj = Job(
        user_id=user_id,
        document_id=obj_in.document_id,
        status=JobStatus.PENDING,
        settings=obj_in.settings,
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


def update_job(db: Session, job: Job, obj_in: JobUpdate) -> Job:
    """
    Update a job.
    
    Args:
        db: Database session
        job: Job to update
        obj_in: Update data
    
    Returns:
        Job: Updated job
    """
    update_data = obj_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(job, field, value)
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def cancel_job(db: Session, job_id: int) -> Job:
    """
    Cancel a job.
    
    Args:
        db: Database session
        job_id: ID of the job to cancel
    
    Returns:
        Job: Cancelled job
    """
    job = get_job(db, job_id=job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    
    # Check if job can be cancelled
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status {job.status.value}",
        )
    
    # Cancel the job
    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow()
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job