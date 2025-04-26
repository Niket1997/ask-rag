# Ask-RAG

A RAG (Retrieval-Augmented Generation) application that allows users to ask questions about their documents. The application uses Qdrant as a vector database and LangChain for document processing and retrieval.

## Features

- **Document Ingestion**: Upload PDF documents to create a knowledge base
- **Question Answering**: Ask questions about the ingested documents
- **Vector Search**: Efficient semantic search using Qdrant
- **LLM Integration**: Powered by LangChain for intelligent responses

## API Endpoints

- `POST /ingest`: Upload and process PDF documents
- `POST /ask`: Ask questions about the ingested documents

## Technical Stack

- FastAPI for the backend API
- Qdrant for vector storage
- LangChain for document processing and LLM integration
- HuggingFace embeddings for semantic search

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the application:
```bash
cd backend
uvicorn main:app --reload
```

3. Access the API documentation at `http://localhost:8000/docs`
