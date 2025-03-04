"""
Document parser for extracting text from various file formats.
"""
import logging
import os
from typing import Dict, Any, List, Optional
import io

# PDF extraction
from pypdf import PdfReader

# DOCX extraction
import docx

# For error handling
from slideforge.core.exceptions import ProcessingError

# Setup logging
logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Parser for extracting text and metadata from different document formats.
    Supports PDF, DOCX, and TXT files.
    """

    @staticmethod
    def parse(file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Parse a document file and extract text and metadata.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the document file (pdf, docx, txt)
            
        Returns:
            Dict containing extracted text and metadata
            
        Raises:
            ProcessingError: If there is an error during extraction
        """
        file_type = file_type.lower()
        
        try:
            if file_type == "pdf":
                return DocumentParser._parse_pdf(file_path)
            elif file_type == "docx":
                return DocumentParser._parse_docx(file_path)
            elif file_type == "txt":
                return DocumentParser._parse_txt(file_path)
            else:
                raise ProcessingError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {str(e)}")
            raise ProcessingError(f"Failed to parse {file_type} file: {str(e)}")

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        """
        Parse a PDF file and extract text and metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict containing extracted text and metadata
        """
        logger.info(f"Parsing PDF file: {file_path}")
        
        try:
            reader = PdfReader(file_path)
            
            # Extract metadata
            metadata = reader.metadata
            if metadata:
                metadata_dict = {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "keywords": metadata.get("/Keywords", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "creation_date": str(metadata.get("/CreationDate", "")),
                }
            else:
                metadata_dict = {}
            
            # Extract text from each page
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"Page {page_num + 1}:\n{page_text}\n\n"
            
            # If text extraction failed, report it
            if not text.strip():
                logger.warning(f"Failed to extract text from PDF: {file_path}")
                text = "[No extractable text found in the PDF document]"
            
            return {
                "text": text,
                "metadata": metadata_dict,
                "pages": len(reader.pages),
                "file_path": file_path,
                "file_type": "pdf"
            }
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise ProcessingError(f"Failed to parse PDF file: {str(e)}")

    @staticmethod
    def _parse_docx(file_path: str) -> Dict[str, Any]:
        """
        Parse a DOCX file and extract text and metadata.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Dict containing extracted text and metadata
        """
        logger.info(f"Parsing DOCX file: {file_path}")
        
        try:
            doc = docx.Document(file_path)
            
            # Extract metadata
            prop = doc.core_properties
            metadata_dict = {
                "title": prop.title or "",
                "author": prop.author or "",
                "subject": prop.subject or "",
                "keywords": prop.keywords or "",
                "category": prop.category or "",
                "comments": prop.comments or "",
                "created": str(prop.created) if prop.created else "",
                "modified": str(prop.modified) if prop.modified else "",
            }
            
            # Extract paragraphs
            text = ""
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
            
            # Extract tables
            for table in doc.tables:
                text += "\nTable:\n"
                for row in table.rows:
                    row_text = " | ".join(cell.text for cell in row.cells)
                    text += row_text + "\n"
                text += "\n"
            
            # If text extraction failed, report it
            if not text.strip():
                logger.warning(f"Failed to extract text from DOCX: {file_path}")
                text = "[No extractable text found in the DOCX document]"
            
            return {
                "text": text,
                "metadata": metadata_dict,
                "paragraphs": len(doc.paragraphs),
                "file_path": file_path,
                "file_type": "docx"
            }
            
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path}: {str(e)}")
            raise ProcessingError(f"Failed to parse DOCX file: {str(e)}")

    @staticmethod
    def _parse_txt(file_path: str) -> Dict[str, Any]:
        """
        Parse a TXT file and extract text.
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            Dict containing extracted text
        """
        logger.info(f"Parsing TXT file: {file_path}")
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
            text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                # If all encodings fail, use binary and decode with replacement
                with open(file_path, 'rb') as f:
                    content = f.read()
                    text = content.decode('utf-8', errors='replace')
            
            # Split into lines for basic structure
            lines = text.splitlines()
            
            # Extract basic metadata (if available in a structured format)
            metadata_dict = {}
            
            # Try to get title from first non-empty line
            for line in lines:
                if line.strip():
                    metadata_dict["title"] = line.strip()
                    break
            
            return {
                "text": text,
                "metadata": metadata_dict,
                "lines": len(lines),
                "file_path": file_path,
                "file_type": "txt"
            }
            
        except Exception as e:
            logger.error(f"Error parsing TXT {file_path}: {str(e)}")
            raise ProcessingError(f"Failed to parse TXT file: {str(e)}")