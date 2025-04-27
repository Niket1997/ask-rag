import os
from typing import Any, Dict

from app.core.constants import (
    create_collection_if_not_exists,
    get_vector_store,
    text_splitter,
    info_logger,
)
from langchain_community.document_loaders import PyPDFLoader


def ingest_pdf(file_path: str, user_email: str) -> Dict[str, Any]:
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
        create_collection_if_not_exists(user_email)
        vector_store = get_vector_store(user_email)
        vector_store.add_documents(chunks)

        return {
            "pages": len(docs),
            "chunks": len(chunks),
            "size": os.path.getsize(file_path),
        }
    except Exception as e:
        raise Exception(f"Error ingesting PDF file: {str(e)}")
