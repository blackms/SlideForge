# 🎯 SlideForge

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.10+-brightgreen)

> 🚀 **Automagically transform your documents into beautiful PowerPoint presentations using AI**

SlideForge is a multi-agent AI system that automatically generates professional PowerPoint presentations from various document formats (PDF, Word, TXT). It analyzes your documents, extracts key information, creates well-structured slides, and applies appropriate styling - all without manual intervention.

## ✨ Features

- 📄 **Multi-format Support**: Process PDF, DOCX, and TXT files
- 🧠 **AI-Powered Content Extraction**: Intelligently extract and synthesize key information
- 📊 **Smart Slide Generation**: Create well-structured slides with proper hierarchy
- 🎨 **Automatic Styling**: Apply context-appropriate visual designs
- 🔄 **Processing Pipeline**: Track job status from upload to completion
- 🔒 **User Authentication**: Secure access with JWT authentication
- 📱 **RESTful API**: Clean API for integration with any client

## 🏗️ Architecture

SlideForge uses a modular, multi-agent architecture:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Extraction   │     │  Generation   │     │ Optimization  │
│     Agent     │────►│     Agent     │────►│     Agent     │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────┬──────┴─────────────┬───────┘
                      ▼                    ▼
              ┌───────────────┐    ┌───────────────┐
              │   Database    │    │  File Storage │
              └───────────────┘    └───────────────┘
                      ▲
                      │
              ┌───────────────┐
              │  FastAPI      │
              │  Backend      │
              └───────────────┘
                      ▲
                      │
              ┌───────────────┐
              │    Client     │
              │  Application  │
              └───────────────┘
```

### Three-Agent System

1. **🔍 Extraction & Synthesis Agent**
   - Processes uploaded documents
   - Extracts text and structure
   - Analyzes content using LLMs
   - Identifies key points and themes

2. **📝 Slide Generation Agent**
   - Creates slide structure
   - Organizes content hierarchically
   - Generates PPTX files
   - Creates appropriate sections and summaries

3. **✨ Graphic Optimization Agent**
   - Analyzes content context
   - Selects appropriate visual styles
   - Enhances typography and layout
   - Applies consistent design principles

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Authentication**: JWT
- **AI/ML**: LangChain, OpenAI/Anthropic
- **Document Processing**: python-docx, PyPDF2
- **Presentation Generation**: python-pptx
- **Task Processing**: Async processing
- **Storage**: Local filesystem (expandable to S3)

## 📋 Prerequisites

- Python 3.10+
- OpenAI API key (for production use)
- PostgreSQL (optional, for production)

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/slideforge.git
cd slideforge
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the project root:

```
DEBUG=true
SECRET_KEY=your_secret_key
# Uncomment for PostgreSQL
# DATABASE_URI=postgresql://postgres:postgres@localhost/slideforge
# Add your OpenAI API key
# OPENAI_API_KEY=your_openai_api_key
```

4. **Initialize the database and create a superuser**

```bash
python setup.py
```

## 🏃‍♂️ Running the Application

Start the development server:

```bash
python run.py
```

The API will be available at `http://localhost:8000`.

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📘 Usage

### 1. Register and get a token

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "SecurePassword123", "full_name": "John Doe"}'
```

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "user@example.com", "password": "SecurePassword123"}'
```

### 2. Upload a document

```bash
curl -X POST "http://localhost:8000/api/documents" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@path/to/your/document.pdf"
```

### 3. Create a presentation job

```bash
curl -X POST "http://localhost:8000/api/jobs" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"document_id": 1, "settings": {"style": "corporate"}}'
```

### 4. Check job status

```bash
curl -X GET "http://localhost:8000/api/jobs/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Download the presentation

```bash
curl -X GET "http://localhost:8000/api/presentations/1/download" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     --output presentation.pptx
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Log in and get JWT token
- `GET /api/auth/me` - Get current user info

### Documents
- `POST /api/documents` - Upload a document
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete a document

### Jobs
- `POST /api/jobs` - Create a presentation job
- `GET /api/jobs` - List jobs
- `GET /api/jobs/{id}` - Get job status
- `DELETE /api/jobs/{id}` - Cancel a job

### Presentations
- `GET /api/presentations` - List presentations
- `GET /api/presentations/{id}` - Get presentation details
- `GET /api/presentations/{id}/download` - Download presentation
- `GET /api/presentations/{id}/thumbnail` - Get presentation thumbnail
- `DELETE /api/presentations/{id}` - Delete a presentation

## 🔭 Future Development

- 🖥️ Web-based user interface
- 📱 Mobile app integration
- 🧩 Custom template system
- 🔗 Integration with cloud storage services
- 📊 More chart and diagram types
- 🧠 Enhanced AI content extraction
- 🔄 Real-time collaboration
- 🌐 Multi-language support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [LangChain](https://github.com/hwchase17/langchain) for AI orchestration
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [python-pptx](https://python-pptx.readthedocs.io/) for presentation generation
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM