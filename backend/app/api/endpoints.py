import logging
import os
import tempfile

from fastapi import APIRouter, Header, HTTPException, UploadFile

from app.core.config import (ALLOWED_FILE_TYPES, TEMP_FILE_PREFIX,
                             TEMP_FILE_SUFFIX)
from app.core.ingestion import ingest_pdf
from app.core.validation import (FileValidationError, validate_file_content,
                                 validate_file_headers)

error_logger = logging.getLogger("uvicorn.error")
info_logger = logging.getLogger("uvicorn.info")

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Hello, World!"}


@router.post("/ingest")
async def ingest_file(file: UploadFile, content_length: int = Header(None)):
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
            metadata = ingest_pdf(temp_file_path)

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
