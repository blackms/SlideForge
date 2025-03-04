"""
LLM interface for content analysis, summarization, and structuring.
Uses OpenAI and Anthropic models via LangChain.
"""
import logging
import os
from typing import Dict, Any, List, Optional, Tuple

# LangChain imports
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.output_parsers.json import SimplePydanticOutputParser
from pydantic import BaseModel, Field

# For error handling
from slideforge.core.exceptions import ProcessingError
from slideforge.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Define Pydantic models for structured output
class ContentPoint(BaseModel):
    """A single point or bullet point in the content."""
    text: str = Field(description="The text content of the point")
    importance: int = Field(description="Importance score from 1 (low) to 5 (high)")

class ContentSection(BaseModel):
    """A section of the structured content."""
    heading: str = Field(description="Section heading")
    content: str = Field(description="Main content of the section")
    points: List[ContentPoint] = Field(description="Key points in this section")

class StructuredContent(BaseModel):
    """Complete structured content of a document."""
    title: str = Field(description="Document title")
    summary: str = Field(description="Executive summary of the document")
    keywords: List[str] = Field(description="Keywords or key phrases from the document")
    sections: List[ContentSection] = Field(description="Content sections")


class LLMInterface:
    """
    Interface for LLM operations including summarization, keyword extraction,
    and content structuring using OpenAI and Anthropic models.
    """
    
    def __init__(self):
        """Initialize the LLM interface with API keys and model configurations."""
        # Set up OpenAI
        self.openai_api_key = settings.OPENAI_API_KEY
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found, some features may be limited")
        
        # Set up Anthropic
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        if not self.anthropic_api_key:
            logger.warning("Anthropic API key not found, some features may be limited")
        
        # Initialize models
        self.openai_model = None
        self.anthropic_model = None
        
        try:
            if self.openai_api_key:
                # Use GPT-4o-mini as specified
                self.openai_model = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.2,
                    api_key=self.openai_api_key,
                    max_tokens=4000
                )
                logger.info("OpenAI GPT-4o-mini model initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI model: {str(e)}")
        
        try:
            if self.anthropic_api_key:
                # Configure Claude 3 Sonnet with thinking
                self.anthropic_model = ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    temperature=0.2,
                    api_key=self.anthropic_api_key,
                    max_tokens=4000,
                    system_prompt=(
                        "You are an intelligent AI assistant that helps extract and structure content from documents. "
                        "When analyzing documents, take time to think step by step. "
                        "First think through your reasoning process in detail, considering the document structure, "
                        "key themes, and relationships between ideas. "
                        "Then organize your thoughts into a clear structure. "
                        "Finally, present your results in the requested format."
                    )
                )
                logger.info("Anthropic Claude 3 Sonnet model with thinking initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic model: {str(e)}")
            
        # Ensure at least one model is available
        if not self.openai_model and not self.anthropic_model:
            raise ProcessingError("No LLM models available. Please check your API keys.")
    
    def generate_summary(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Generate a summary of the document content.
        
        Args:
            text: The document text to summarize
            metadata: Optional document metadata
            
        Returns:
            str: The generated summary
        """
        logger.info("Generating document summary")
        
        # Prepare context from metadata
        context = ""
        if metadata:
            title = metadata.get("title", "")
            author = metadata.get("author", "")
            subject = metadata.get("subject", "")
            
            if title:
                context += f"Title: {title}\n"
            if author:
                context += f"Author: {author}\n"
            if subject:
                context += f"Subject: {subject}\n"
        
        # Adjust text length to avoid token limits
        max_chars = 15000  # Approximate character limit
        if len(text) > max_chars:
            truncated_text = text[:max_chars] + "...[text truncated]..."
            logger.info(f"Text truncated from {len(text)} to {len(truncated_text)} characters for summarization")
            text = truncated_text
        
        # Create prompt
        prompt_template = """
        You are an AI assistant tasked with summarizing documents for presentation creation.
        
        {context}
        
        DOCUMENT TEXT:
        {text}
        
        Please provide a concise executive summary (200-300 words) that captures the key points and main message of this document.
        Focus on the most important information that should be highlighted in a presentation.
        
        EXECUTIVE SUMMARY:
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text", "context"]
        )
        
        # Use Anthropic model for summarization (better reasoning)
        model = self.anthropic_model if self.anthropic_model else self.openai_model
        
        try:
            chain = LLMChain(llm=model, prompt=prompt)
            summary = chain.run(text=text, context=context)
            return summary.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise ProcessingError(f"Failed to generate summary: {str(e)}")
    
    def extract_keywords(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Extract keywords from the document content.
        
        Args:
            text: The document text
            metadata: Optional document metadata
            
        Returns:
            str: Comma-separated keywords
        """
        logger.info("Extracting keywords from document")
        
        # Adjust text length to avoid token limits
        max_chars = 15000
        if len(text) > max_chars:
            truncated_text = text[:max_chars] + "...[text truncated]..."
            logger.info(f"Text truncated from {len(text)} to {len(truncated_text)} characters for keyword extraction")
            text = truncated_text
        
        # Create prompt
        prompt_template = """
        You are an AI assistant tasked with extracting relevant keywords from documents for presentation creation.
        
        DOCUMENT TEXT:
        {text}
        
        Please identify 10-15 key terms, concepts, or phrases that best represent the main topics and themes of this document.
        These keywords will be used for tagging and retrieval of the presentation.
        
        Return the keywords as a comma-separated list.
        
        KEYWORDS:
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text"]
        )
        
        # Use OpenAI model for keyword extraction (faster)
        model = self.openai_model if self.openai_model else self.anthropic_model
        
        try:
            chain = LLMChain(llm=model, prompt=prompt)
            keywords = chain.run(text=text)
            return keywords.strip()
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            raise ProcessingError(f"Failed to extract keywords: {str(e)}")
    
    def structure_content(self, text: str, summary: str, keywords: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Structure the document content into a presentation-friendly format.
        
        Args:
            text: The document text
            summary: The generated summary
            keywords: The extracted keywords
            metadata: Optional document metadata
            
        Returns:
            Dict: Structured content in a format suitable for presentation generation
        """
        logger.info("Structuring document content")
        
        # Prepare title from metadata or generate a placeholder
        title = "Untitled Document"
        if metadata and metadata.get("title"):
            title = metadata.get("title")
        
        # Adjust text length to avoid token limits
        max_chars = 15000
        if len(text) > max_chars:
            truncated_text = text[:max_chars] + "...[text truncated]..."
            logger.info(f"Text truncated from {len(text)} to {len(truncated_text)} characters for content structuring")
            text = truncated_text
        
        # Convert keywords string to list
        keyword_list = [k.strip() for k in keywords.split(',')]
        
        parser = PydanticOutputParser(pydantic_object=StructuredContent)
        
        # Create prompt
        prompt_template = """
        You are an AI assistant tasked with structuring document content for presentation creation.
        
        DOCUMENT TEXT:
        {text}
        
        SUMMARY:
        {summary}
        
        KEYWORDS:
        {keywords}
        
        Please analyze this document and structure it into a presentation-friendly format.
        
        Your task is to:
        1. Identify the main sections of the document (3-5 sections)
        2. For each section, provide a clear heading, a brief descriptive paragraph, and 3-5 key points
        3. Consider what information would be most impactful in a presentation setting
        4. Ensure the structure tells a coherent story from beginning to end
        
        The output should follow this JSON schema:
        {format_instructions}
        
        Only include information that is explicitly stated or strongly implied in the document.
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["text", "summary", "keywords"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Use Anthropic model for content structuring (better reasoning)
        model = self.anthropic_model if self.anthropic_model else self.openai_model
        
        try:
            chain = LLMChain(llm=model, prompt=prompt)
            result = chain.run(
                text=text,
                summary=summary,
                keywords=keywords
            )
            
            # Parse the result using the Pydantic model
            try:
                parsed_result = parser.parse(result)
                
                # Convert to dict for storage
                structured_content = parsed_result.dict()
                
                # Ensure title is set
                if not structured_content.get("title") or structured_content.get("title") == "Document Title":
                    structured_content["title"] = title
                
                return structured_content
                
            except Exception as parsing_error:
                logger.error(f"Error parsing LLM output: {str(parsing_error)}")
                
                # Fallback to a simple structure if parsing fails
                return {
                    "title": title,
                    "summary": summary,
                    "keywords": keyword_list,
                    "sections": [
                        {
                            "heading": "Introduction",
                            "content": summary[:200] if len(summary) > 200 else summary,
                            "points": [{"text": kw, "importance": 3} for kw in keyword_list[:3]]
                        },
                        {
                            "heading": "Key Findings",
                            "content": "Main findings from the document.",
                            "points": [{"text": kw, "importance": 4} for kw in keyword_list[3:6] if len(keyword_list) > 3]
                        },
                        {
                            "heading": "Conclusion",
                            "content": "Summary of conclusions.",
                            "points": [{"text": kw, "importance": 3} for kw in keyword_list[6:9] if len(keyword_list) > 6]
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error structuring content: {str(e)}")
            raise ProcessingError(f"Failed to structure content: {str(e)}")