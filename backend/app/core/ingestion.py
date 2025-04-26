from typing import Dict, Any
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_qdrant import QdrantVectorStore
from .constants import text_splitter, embeddings

def ingest_pdf(file_path: str) -> Dict[str, Any]:
    """
    Process and ingest a PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dict containing ingestion status and metadata
    """
    try:
        # 1. load the pdf file
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        # 2. chunk the data
        chunks = text_splitter.split_documents(docs)

        # 3. generate vector embeddings for the data & store in Qdrant
        QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            url=os.getenv("QDRANT_URL"),
            collection_name="test-stock-investing-101",
        )

        return {
            "pages": len(docs),
            "chunks": len(chunks),
            "size": os.path.getsize(file_path),
        }
    except Exception as e:
        raise Exception(f"Error ingesting PDF file: {str(e)}") 