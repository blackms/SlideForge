"""
Task orchestrator for job processing.
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from slideforge.db.models.job import Job, JobStatus
from slideforge.db.session import SessionLocal
from slideforge.agents.extraction.agent import ExtractionAgent
from slideforge.agents.generation.agent import GenerationAgent
from slideforge.agents.optimization.agent import OptimizationAgent

# Setup logging
logger = logging.getLogger(__name__)


def get_job(db: Session, job_id: int) -> Optional[Job]:
    """
    Get a job by ID.
    """
    return db.query(Job).filter(Job.id == job_id).first()


def update_job_status(db: Session, job: Job, status: JobStatus, error_message: Optional[str] = None) -> Job:
    """
    Update a job's status.
    """
    job.status = status
    
    if error_message:
        job.error_message = error_message
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


async def start_job_processing(job_id: int) -> None:
    """
    Start processing a job.
    
    Args:
        job_id: ID of the job to process
    """
    # Create a new database session
    db = SessionLocal()
    
    try:
        # Get the job
        job = get_job(db, job_id=job_id)
        
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Start the job
        job.start_job()
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Process the job
        try:
            # 1. Extraction
            logger.info(f"Starting extraction for job {job_id}")
            job.start_extraction()
            db.add(job)
            db.commit()
            
            extraction_agent = ExtractionAgent()
            extracted_content = await extraction_agent.process(job)
            
            job.complete_extraction()
            db.add(job)
            db.commit()
            
            # 2. Generation
            logger.info(f"Starting generation for job {job_id}")
            job.start_generation()
            db.add(job)
            db.commit()
            
            generation_agent = GenerationAgent()
            presentation = await generation_agent.process(job, extracted_content)
            
            job.complete_generation()
            db.add(job)
            db.commit()
            
            # 3. Optimization
            logger.info(f"Starting optimization for job {job_id}")
            job.start_styling()
            db.add(job)
            db.commit()
            
            optimization_agent = OptimizationAgent()
            final_presentation = await optimization_agent.process(job, presentation)
            
            # Complete the job
            job.complete_styling()
            job.presentation_id = final_presentation.id
            db.add(job)
            db.commit()
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            # Handle any errors in processing
            error_message = f"Error processing job: {str(e)}"
            logger.error(error_message)
            job.fail_job(error_message)
            db.add(job)
            db.commit()
    
    finally:
        # Close the database session
        db.close()