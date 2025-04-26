import os

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

# API Key Configuration
API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("BACKEND_API_KEY")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
