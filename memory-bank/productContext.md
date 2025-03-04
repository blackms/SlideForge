# SlideForge Product Context

## Project Overview
SlideForge is a multi-agent Python system designed to automate the generation of PowerPoint presentations from text documents (PDF, Word, TXT). The system employs artificial intelligence to extract key information, generate slide content, and apply appropriate visual styling.

## Core Value Proposition
- **Time Efficiency**: Automate the tedious process of creating presentations from documents
- **Intelligent Synthesis**: Extract and highlight the most important information
- **Professional Styling**: Apply context-appropriate visual designs automatically
- **Consistency**: Generate presentations with consistent formatting and style

## System Architecture - High Level

### Multi-Agent Design
The system follows a modular, multi-agent architecture with three primary agents:

1. **Extraction & Synthesis Agent**
   - Processes input documents (PDF, Word, TXT)
   - Uses LangChain and LLM models (OpenAI, Anthropic)
   - Extracts key points and generates summaries
   - Identifies document structure and important themes

2. **Slide Generation Agent**
   - Transforms synthesized data into slide structures
   - Creates PPTX files with appropriate sections
   - Generates titles, content blocks, and summaries
   - Organizes information in a presentation-friendly format

3. **Graphic Optimization Agent**
   - Analyzes presentation context and content
   - Determines appropriate visual style based on industry/purpose
   - Applies design templates and styling
   - Optimizes visual elements for readability and impact

### Technical Foundation
- **Backend**: FastAPI for high-performance API services
- **Database**: SQLAlchemy ORM with SQLite (development) and PostgreSQL (production) support
- **Task Processing**: Asynchronous task queue (Celery or similar) for agent orchestration
- **AI Integration**: LangChain for LLM integration and agent coordination
- **Cloud Readiness**: Architecture designed for cloud deployment and scaling

## Memory Bank Structure
This Memory Bank contains the following core files:

- **productContext.md** (this file): Overall project description and high-level architecture
- **activeContext.md**: Tracks the current development session's context and focus
- **progress.md**: Documents development progress and manages tasks
- **decisionLog.md**: Records architectural decisions and their rationales

Additional documentation will be added as the project evolves.