## Ingestion script for the Qdrant vector database
# Steps:
# 1. Load the data
# 2. Chunk the data
# 3. Generate vector embeddings for the data
# 4. Store the data in Qdrant

## version 1 will support only pdf file ingestion
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_qdrant import QdrantVectorStore
from constants import text_splitter, embeddings


def ingest_pdf(pdf_path: str):
    # 1. load the pdf file
    loader = PyPDFLoader(pdf_path)
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

    response = f"Successfully ingested {len(chunks)} chunks"

    return response

