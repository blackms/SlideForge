"""
Extraction Agent for processing documents and extracting content.
"""
import logging
import os
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from slideforge.db.models.document import Document
from slideforge.db.models.extracted_content import ExtractedContent
from slideforge.db.models.job import Job
from slideforge.core.exceptions import ProcessingError
from slideforge.agents.extraction.document_parser import DocumentParser
from slideforge.agents.extraction.llm_interface import LLMInterface

# Setup logging
logger = logging.getLogger(__name__)


class ExtractionAgent:
    """
    Agent responsible for extracting and synthesizing content from documents.
    Uses document parsing and LLM analysis to extract structured content.
    """
    
    def __init__(self):
        """Initialize the extraction agent with document parser and LLM interface."""
        self.document_parser = DocumentParser()
        self.llm_interface = LLMInterface()
    
    async def process(self, job: Job) -> ExtractedContent:
        """
        Process a document and extract content.
        
        Args:
            job: The job containing the document to process
        
        Returns:
            ExtractedContent: The extracted content
        
        Raises:
            Exception: If there is an error during extraction
        """
        logger.info(f"Extracting content for job {job.id}, document {job.document_id}")
        
        db = job._sa_instance_state.session
        
        # Get the document
        document = db.query(Document).filter(Document.id == job.document_id).first()
        if not document:
            raise ProcessingError(f"Document {job.document_id} not found")
        
        # Check if file exists
        if not os.path.exists(document.file_path):
            raise ProcessingError(f"Document file not found at {document.file_path}")
        
        # Extract content based on document type
        try:
            # Step 1: Parse the document
            parsed_document = self.document_parser.parse(document.file_path, document.file_type)
            
            # Log document statistics
            logger.info(f"Document parsed successfully. Text length: {len(parsed_document['text'])} characters")
            
            # Step 2: Extract metadata from the parsed document
            metadata = parsed_document.get('metadata', {})
            # Add document properties to metadata
            metadata['file_type'] = document.file_type
            metadata['file_size'] = document.file_size
            
            # Step 3: Generate summary using LLM
            summary = self.llm_interface.generate_summary(parsed_document['text'], metadata)
            logger.info(f"Summary generated: {len(summary)} characters")
            
            # Step 4: Extract keywords using LLM
            keywords = self.llm_interface.extract_keywords(parsed_document['text'], metadata)
            logger.info(f"Keywords extracted: {keywords}")
            
            # Step 5: Structure content using LLM
            structured_content = self.llm_interface.structure_content(
                parsed_document['text'], summary, keywords, metadata
            )
            logger.info(f"Content structured with {len(structured_content.get('sections', []))} sections")
            
            # Step 6: Create extracted content record
            extracted_content = ExtractedContent(
                document_id=document.id,
                content_text=parsed_document['text'],
                content_json=structured_content,
                summary=summary,
                keywords=keywords,
            )
            
            db.add(extracted_content)
            db.commit()
            db.refresh(extracted_content)
            
            return extracted_content
            
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            raise
    
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """
        Legacy method: Extract text from a document file.
        Now delegated to DocumentParser.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the document (pdf, docx, txt)
        
        Returns:
            str: Extracted text
        """
        # Use the document parser for extraction
        parsed_document = self.document_parser.parse(file_path, file_type)
        return parsed_document['text']
    
    def _generate_summary(self, content: str) -> str:
        """
        Legacy method: Generate a summary of the content.
        Now delegated to LLMInterface.
        
        Args:
            content: The extracted text content
        
        Returns:
            str: Summary of the content
        """
        # Use the LLM interface for summarization
        return self.llm_interface.generate_summary(content)
    
    def _extract_keywords(self, content: str) -> str:
        """
        Legacy method: Extract keywords from the content.
        Now delegated to LLMInterface.
        
        Args:
            content: The extracted text content
        
        Returns:
            str: Comma-separated keywords
        """
        # Use the LLM interface for keyword extraction
        return self.llm_interface.extract_keywords(content)
    
    def _structure_content(self, content: str) -> Dict[str, Any]:
        """
        Legacy method: Structure the content into sections and points.
        Now delegated to LLMInterface.
        
        Args:
            content: The extracted text content
        
        Returns:
            dict: Structured content as JSON
        """
        # Use the LLM interface for content structuring
        summary = self.llm_interface.generate_summary(content)
        keywords = self.llm_interface.extract_keywords(content)
        return self.llm_interface.structure_content(content, summary, keywords)