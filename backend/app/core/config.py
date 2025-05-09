# File type configurations
ALLOWED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "application/json": ".json",
    "text/csv": ".csv",
}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

# Chunk size for file reading
CHUNK_SIZE = 8192  # 8KB chunks

# API Configuration
API_PREFIX = "/api/v1"
API_TITLE = "Ask-RAG API"
API_DESCRIPTION = "API for the Ask-RAG application"
API_VERSION = "1.0.0"


# File Processing Configuration
TEMP_FILE_PREFIX = "ask_rag_"
TEMP_FILE_SUFFIX = "_temp"

# Rate Limiting Configuration
RATE_LIMIT_MAX_REQUESTS_INGESTION_API = 5
RATE_LIMIT_WINDOW_SECONDS_INGESTION_API = 86400
RATE_LIMIT_MAX_REQUESTS_ASK_API = 20
RATE_LIMIT_WINDOW_SECONDS_ASK_API = 86400
