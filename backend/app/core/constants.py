# Constants for the ask-rag application
import logging
import os

import redis
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient

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

# create qrant client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# create LLM
llm = ChatOpenAI(
    model="gpt-4.1",
)

# create redis client
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
)
