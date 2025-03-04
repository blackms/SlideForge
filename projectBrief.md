# SlideForge Project Brief

## Overview
SlideForge is a multi-agent Python system designed to automate the generation of PowerPoint presentations from text documents (PDF, Word, TXT). The system follows a three-step process:

1. **Extraction and Synthesis**: An AI agent using LangChain and LLM models (OpenAI, Anthropic, etc.) analyzes documents and generates summaries with key points.

2. **Raw Slide Generation**: A second agent takes synthesized data and creates a PowerPoint (PPTX) file with titles, paragraphs, and a summary.

3. **Graphic Optimization**: A third agent analyzes the context (Tech, Finance, Legal, etc.) and presentation tone to apply appropriate graphic styles, inspired by tools like Beautiful AI or Presentations.ai.

## Technical Requirements
- **Language**: Python
- **API Backend**: FastAPI
- **Agent Orchestration**: LangChain
- **Database**: SQLite with PostgreSQL support via SQLAlchemy
- **Best Practices**: SOLID principles, appropriate design patterns, modular architecture
- **Asynchronous Pipeline**: Task queues like Celery or alternatives for agent orchestration
- **Scalability**: System designed for cloud deployment
- **Logging & Monitoring**: Implementation of systems like Prometheus, ELK stack, or OpenTelemetry

## Documentation Requirements
- UML Diagrams (Component, Sequence, Deployment)
- Design choices and rationales
- Microservice/component structure
- Data flow and agent orchestration
- API interfaces and database schema

The goal is to create a modular, well-documented architecture ready for implementation according to software development best practices.