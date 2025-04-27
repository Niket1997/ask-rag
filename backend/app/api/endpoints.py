import os
import re
import tempfile

from app.core.auth import verify_api_key
from app.core.config import (
    ALLOWED_FILE_TYPES,
    RATE_LIMIT_MAX_REQUESTS_ASK_API,
    RATE_LIMIT_MAX_REQUESTS_INGESTION_API,
    RATE_LIMIT_WINDOW_SECONDS_ASK_API,
    RATE_LIMIT_WINDOW_SECONDS_INGESTION_API,
    TEMP_FILE_PREFIX,
    TEMP_FILE_SUFFIX,
)
from app.core.constants import error_logger, info_logger
from app.core.ingestion import ingest_pdf
from app.core.retrieval import retrieve_answer
from app.core.validation import (
    FileValidationError,
    check_rate_limit,
    validate_file_content,
    validate_file_headers,
)
from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, UploadFile
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


# Query request
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    user_email: EmailStr = Field(..., description="Valid email address")


# Read root
@router.get("/")
def read_root():
    return {"message": "Hello, World!"}


# Ingest the file into the database
@router.post("/ingest")
async def ingest_file(
    file: UploadFile,
    content_length: int = Header(None),
    user_email: EmailStr = Form(..., description="Valid email address"),
    api_key: str = Depends(verify_api_key),
):
    # Check rate limit
    if not check_rate_limit(
        user_email,
        "ingest",
        max_requests=RATE_LIMIT_MAX_REQUESTS_INGESTION_API,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS_INGESTION_API,
    ):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX_REQUESTS_INGESTION_API} file uploads allowed in last {RATE_LIMIT_WINDOW_SECONDS_INGESTION_API/3600} hours.",
        )

    temp_file_path = None

    try:
        # First layer validation
        await validate_file_headers(
            content_type=file.content_type,
            content_length=content_length,
            filename=file.filename,
        )

        # Create temporary file with proper prefix and suffix
        temp_file_path = tempfile.mktemp(
            prefix=TEMP_FILE_PREFIX,
            suffix=f"{TEMP_FILE_SUFFIX}{ALLOWED_FILE_TYPES[file.content_type]}",
        )

        # Second layer validation
        await validate_file_content(file, temp_file_path)

        # Process the file
        if file.content_type == "application/pdf":
            metadata = ingest_pdf(temp_file_path, user_email)

            # Log successful ingestion
            info_logger.info(
                f"File ingested successfully: {file.filename}, "
                f"size: {metadata['size']}, "
                f"pages: {metadata['pages']}, "
                f"chunks: {metadata['chunks']}"
            )

            return {
                "filename": file.filename,
                "message": "PDF file ingested successfully",
                "metadata": metadata,
            }

        return {"filename": file.filename, "error": "File type not supported"}

    except FileValidationError as e:
        # Log validation errors
        error_logger.error(f"File validation error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)

    except Exception as e:
        # Log unexpected errors
        error_logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


# Retrieve the answer from LLM based on the query
@router.post("/ask")
async def ask_question(request: QueryRequest, api_key: str = Depends(verify_api_key)):
    # Check rate limit
    if not check_rate_limit(
        request.user_email,
        "ask",
        max_requests=RATE_LIMIT_MAX_REQUESTS_ASK_API,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS_ASK_API,
    ):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX_REQUESTS_ASK_API} questions allowed in last {RATE_LIMIT_WINDOW_SECONDS_ASK_API/3600} hours.",
        )

    try:
        # Log the query
        info_logger.info(f"Processing query: {request.query}")

        # Get answer from LLM
        answer = retrieve_answer(request.query, request.user_email)

        return {"status": "success", "query": request.query, "answer": answer}

    except Exception as e:
        error_logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
