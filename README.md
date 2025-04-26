# Ask-RAG

A RAG (Retrieval-Augmented Generation) application that allows users to ask questions about their documents. The application uses Qdrant as a vector database and LangChain for document processing and retrieval.

## Features

- **Document Ingestion**: Upload PDF documents to create a knowledge base
- **Question Answering**: Ask questions about the ingested documents
- **Vector Search**: Efficient semantic search using Qdrant
- **LLM Integration**: Powered by LangChain for intelligent responses

## Environment Variables
- `BACKEND_URL`: URL of the backend API (default: http://localhost:8000) 
- `OPENAI_API_KEY`: OPENAI API KEY (ref)[https://medium.com/@lorenzozar/how-to-get-your-own-openai-api-key-f4d44e60c327]
- `QDRANT_URL`: URL of the QDRANT API (default: http://localhost:6333)
- `GOOGLE_CREDENTIALS_JSON`='{json_content}' (ref)[https://pypi.org/project/streamlit-google-auth/]
- `BACKEND_API_KEY`: API key for service to service communication between UI application & FastAPI backend application.

# Backend
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

2. Access the API documentation at `http://localhost:8000/docs`

# Frontend

This is a Streamlit-based chat interface for interacting with the RAG backend system.

Edit the `.env` file to configure your backend URL if needed.

## Running the Application

To start the Streamlit app:

```bash
cd frontend
streamlit run app.py
```

The application will be available at http://localhost:8501

## Features

- Clean and intuitive chat interface
- Real-time communication with the backend
- Message history persistence during the session
- Clear chat functionality
- Responsive design
- Error handling for backend communication

