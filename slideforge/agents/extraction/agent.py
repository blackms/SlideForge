"""
Extraction Agent for processing documents and extracting content.
Optimized for handling large documents (100+ pages).
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
    Optimized for both small and large documents.
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
            text_length = len(parsed_document['text'])
            logger.info(f"Document parsed successfully. Text length: {text_length} characters")
            
            # Check if this is a large document
            is_large_document = parsed_document.get('is_large_document', False)
            if is_large_document:
                logger.info(f"Processing large document with optimized extraction")
                
                # Log what sections were extracted
                extracted_sections = parsed_document.get('extracted_sections', {})
                logger.info(f"Extracted sections: {extracted_sections}")
            
            # Step 2: Extract metadata from the parsed document
            metadata = parsed_document.get('metadata', {})
            # Add document properties to metadata
            metadata['file_type'] = document.file_type
            metadata['file_size'] = document.file_size
            if is_large_document:
                metadata['is_large_document'] = True
                # Add information about document size
                if 'pages' in parsed_document:
                    metadata['total_pages'] = parsed_document['pages']
                elif 'paragraphs' in parsed_document:
                    metadata['total_paragraphs'] = parsed_document['paragraphs']
                elif 'lines' in parsed_document:
                    metadata['total_lines'] = parsed_document['lines']
            
            # Step 3: Generate summary using LLM
            # For large documents, we use a special prompt that acknowledges the document's size
            # and works with the extracted representative portions
            summary = self._generate_summary_for_document(parsed_document['text'], metadata, is_large_document)
            logger.info(f"Summary generated: {len(summary)} characters")
            
            # Step 4: Extract keywords using LLM
            keywords = self._extract_keywords_for_document(parsed_document['text'], metadata, is_large_document)
            logger.info(f"Keywords extracted: {keywords}")
            
            # Step 5: Structure content using LLM
            structured_content = self._structure_content_for_document(
                parsed_document['text'], summary, keywords, metadata, is_large_document
            )
            logger.info(f"Content structured with {len(structured_content.get('sections', []))} sections")
            
            # Step 6: Create extracted content record
            extracted_content = ExtractedContent(
                document_id=document.id,
                content_text=parsed_document['text'][:100000],  # Limit stored text to reasonable size
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
    
    def _generate_summary_for_document(self, text: str, metadata: Dict[str, Any], is_large_document: bool) -> str:
        """
        Generate a summary of the document content, with special handling for large documents.
        
        Args:
            text: The document text
            metadata: Document metadata
            is_large_document: Whether this is a large document
            
        Returns:
            str: The generated summary
        """
        if is_large_document:
            # For large documents, add a note in the metadata to inform the LLM
            enhanced_metadata = metadata.copy()
            enhanced_metadata['document_note'] = (
                "This is a large document that has been processed by extracting key sections including "
                "table of contents, introduction, conclusion, and representative samples from throughout "
                "the document. The text provided is not the complete document, but a strategic selection "
                "designed to represent the overall content."
            )
            
            # The text we received already contains the most important parts
            return self.llm_interface.generate_summary(text, enhanced_metadata)
        else:
            # For regular documents, use standard summarization
            return self.llm_interface.generate_summary(text, metadata)
    
    def _extract_keywords_for_document(self, text: str, metadata: Dict[str, Any], is_large_document: bool) -> str:
        """
        Extract keywords from the document content, with special handling for large documents.
        
        Args:
            text: The document text
            metadata: Document metadata
            is_large_document: Whether this is a large document
            
        Returns:
            str: Comma-separated keywords
        """
        if is_large_document:
            # For large documents, add a note in the metadata
            enhanced_metadata = metadata.copy()
            enhanced_metadata['document_note'] = (
                "This is a large document that has been processed by extracting key sections. "
                "Please focus on identifying the most significant keywords from the provided excerpts."
            )
            
            return self.llm_interface.extract_keywords(text, enhanced_metadata)
        else:
            # For regular documents, use standard keyword extraction
            return self.llm_interface.extract_keywords(text, metadata)
    
    def _structure_content_for_document(
        self, text: str, summary: str, keywords: str, metadata: Dict[str, Any], is_large_document: bool
    ) -> Dict[str, Any]:
        """
        Structure the document content, with special handling for large documents.
        
        Args:
            text: The document text
            summary: The generated summary
            keywords: The extracted keywords
            metadata: Document metadata
            is_large_document: Whether this is a large document
            
        Returns:
            dict: Structured content as JSON
        """
        if is_large_document:
            # For large documents, add a note in the metadata
            enhanced_metadata = metadata.copy()
            enhanced_metadata['document_note'] = (
                "This is a large document that has been processed by extracting key sections. "
                "When structuring the content, focus on creating a coherent presentation structure "
                "based on the provided excerpts, summary, and keywords."
            )
            
            return self.llm_interface.structure_content(text, summary, keywords, enhanced_metadata)
        else:
            # For regular documents, use standard content structuring
            return self.llm_interface.structure_content(text, summary, keywords, metadata)