# Constants for the ask-rag application
import base64
import hashlib
import logging
import os

import redis
from dotenv import load_dotenv
from langchain_astradb import AstraDBVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from astrapy import DataAPIClient

# hash the user email using base64 encoding
def md5_b64(s: str) -> str:
    d = hashlib.md5(s.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(d).rstrip(b"=").decode("ascii")

# load the environment variables
load_dotenv()

# Initialize the logging
error_logger = logging.getLogger("uvicorn.error")
info_logger = logging.getLogger("uvicorn.info")

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Initialize the embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# create LLM
llm = ChatOpenAI(
    model="gpt-4.1",
)

# create qrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
)

# create astradb keyspace
astradb_keyspace = DataAPIClient().get_database(
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
)

# create redis client
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
)

# vector db to use
vector_db = os.getenv("VECTOR_DB", "QDRANT")

# check if collection exists in vector db
def collection_exists(user_email: str):
    collection_name = md5_b64(user_email)
    if vector_db == "ASTRADB":
        collections = astradb_keyspace.list_collections() 
        for collection in collections:
            if collection.name == collection_name:
                return True
        return False
    elif vector_db == "QDRANT":
        return qdrant_client.collection_exists(collection_name)
    else:
        raise ValueError(f"Invalid vector db: {vector_db}")
    

# create collection if it doesn't exist
def create_collection_if_not_exists(user_email: str):
    if collection_exists(user_email):
        return
    collection_name = md5_b64(user_email)
    if vector_db == "ASTRADB":
        astradb_keyspace.create_collection(collection_name)
    elif vector_db == "QDRANT":
        qdrant_client.create_collection(collection_name)
    else:
        raise ValueError(f"Invalid vector db: {vector_db}")


# get vector store for collection
def get_vector_store(user_email: str):
    collection_name = md5_b64(user_email)
    if vector_db == "ASTRADB":
        return AstraDBVectorStore(
            collection_name=collection_name,
            embedding=embeddings,
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        )
    elif vector_db == "QDRANT":
        return QdrantVectorStore(
            client=qdrant_client,
            collection_name=collection_name,
            embedding=embeddings,
        )
    else:
        raise ValueError(f"Invalid vector db: {vector_db}")
