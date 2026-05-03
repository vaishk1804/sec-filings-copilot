# SEC Filings Copilot

SEC Filings Copilot is a full-stack AI-assisted research tool for exploring company filings and extracting useful insights from financial documents.

The project is designed around a practical finance workflow: ingest filings, search or retrieve relevant sections, and provide a cleaner interface for analyzing dense SEC documents.

## Why I Built This

SEC filings contain valuable information, but they are long, text-heavy, and difficult to review quickly. Analysts, investors, and researchers often need to locate specific sections such as risk factors, business descriptions, and management discussion. This project explores how software engineering and AI-assisted search can make filings easier to query, summarize, and compare.

## Features

- Full-stack project structure with backend, frontend, and infrastructure layers
- Backend service for filing-related API workflows
- Frontend interface for searching and reviewing filing content
- Infrastructure folder for deployment or service configuration
- Foundation for AI-assisted document retrieval and financial research
- Designed for SEC filings, long-form financial documents, and analyst-style workflows

## Tech Stack

**Backend:** Python  
**Frontend:** React / JavaScript  
**Infrastructure:** Docker or deployment configuration  
**Domain:** SEC filings, financial documents, AI-assisted research  
**Potential AI Workflow:** Document chunking, search, retrieval, summarization, and source-aware answers

## Repository Structure

    sec-filings-copilot/
    ├── backend/      # Backend services and APIs
    ├── frontend/     # User interface
    ├── infra/        # Infrastructure/deployment configuration
    ├── .gitignore
    └── README.md

## Example Use Cases

- Search for specific SEC filing sections
- Extract risk factors, business descriptions, or financial discussion sections
- Compare filing language across companies or time periods
- Support faster first-pass review of long financial documents
- Build a foundation for retrieval-augmented financial research workflows

## Local Setup

### Backend

    cd backend
    python -m venv .venv
    .venv\Scripts\activate   # Windows
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload

### Frontend

    cd frontend
    npm install
    npm run dev

## Environment Variables

Create a `.env` file if required by the backend.

    API_KEY=your_key_here
    DATABASE_URL=your_database_url
    FRONTEND_URL=http://localhost:5173

Update these values based on the actual backend configuration.

## What I Focused On

- Structuring a production-style full-stack application
- Connecting financial-domain document workflows to a usable interface
- Separating backend, frontend, and infrastructure concerns
- Designing toward AI-assisted financial document search and analysis
- Building a project that combines finance, software engineering, and applied AI

## Highlights

- Built a finance-focused full-stack application with backend, frontend, and infrastructure layers
- Designed around SEC filings, long-form documents, and analyst research workflows
- Created a foundation for document retrieval, search, and AI-assisted summarization
- Demonstrated ability to structure a domain-specific AI product rather than a generic chatbot
- Applied software engineering thinking to a real financial-document analysis problem

## Responsible Use Note

This project is intended for educational and research purposes. It should not be treated as financial advice. Any generated summaries or extracted insights should be verified against the original SEC filing text.

## Future Improvements

- Add SEC filing ingestion pipeline
- Add document chunking and vector search
- Add source citations for generated answers
- Add filing comparison view across companies or years
- Add screenshots and a demo video
- Add tests for backend APIs and frontend components
- Add deployment instructions for the full stack

## Status

In-progress portfolio project. Built to demonstrate AI-assisted financial research, full-stack development, document-analysis workflows, and production-style project structure.
