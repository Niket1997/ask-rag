# backend application for the ask-rag application
# this will expose following endpoints:
# 1. /ingest
# 2. /ask
# 3. /authenticate # optional

from fastapi import FastAPI, UploadFile, HTTPException, Header, Request
from ingestion import ingest_pdf
import os
import tempfile
import logging
from typing import Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Define allowed file types and their MIME types
ALLOWED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "application/json": ".json",
    "text/csv": ".csv"
}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def validate_file_headers(
    content_type: Optional[str],
    content_length: Optional[int],
    filename: Optional[str]
) -> None:
    """
    First layer validation - Quick header checks
    This would typically be done at the API Gateway/Load Balancer level
    """
    if not content_type:
        raise FileValidationError("Content-Type header is required", 400)
    
    if not content_length:
        raise FileValidationError("Content-Length header is required", 400)
    
    if not filename:
        raise FileValidationError("Filename is required", 400)
    
    if content_type not in ALLOWED_FILE_TYPES:
        raise FileValidationError(
            f"File type not allowed. Allowed types are: {', '.join(ALLOWED_FILE_TYPES.values())}",
            415
        )
    
    if content_length > MAX_FILE_SIZE:
        raise FileValidationError(
            f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB",
            413
        )

async def validate_file_content(
    file: UploadFile,
    temp_file_path: str
) -> int:
    """
    Second layer validation - Actual content validation
    This is done at the application level
    """
    total_size = 0
    chunk_size = 8192  # 8KB chunks
    
    try:
        while chunk := await file.read(chunk_size):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise FileValidationError(
                    f"Actual file size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB",
                    413
                )
            with open(temp_file_path, 'ab') as f:
                f.write(chunk)
        
        # Verify file extension matches content type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension != ALLOWED_FILE_TYPES[file.content_type]:
            raise FileValidationError(
                f"File extension {file_extension} does not match content type {file.content_type}",
                415
            )
        
        return total_size
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise e

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/ingest")
async def ingest_file(
    request: Request,
    file: UploadFile,
    content_length: int = Header(None)
):
    start_time = datetime.now()
    temp_file_path = None
    
    try:
        # First layer validation
        await validate_file_headers(
            content_type=file.content_type,
            content_length=content_length,
            filename=file.filename
        )
        
        # Create temporary file
        temp_file_path = tempfile.mktemp(suffix=ALLOWED_FILE_TYPES[file.content_type])
        
        # Second layer validation
        total_size = await validate_file_content(file, temp_file_path)
        
        # Process the file
        if file.content_type == "application/pdf":
            response = ingest_pdf(temp_file_path)
            
            # Log successful ingestion
            logger.info(
                f"File ingested successfully: {file.filename}, "
                f"size: {total_size}, "
                f"type: {file.content_type}, "
                f"processing_time: {(datetime.now() - start_time).total_seconds()}s"
            )
            
            return {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": total_size,
                "message": response
            }
        
        return {
            "filename": file.filename,
            "error": "File type not supported"
        }

    except FileValidationError as e:
        # Log validation errors
        logger.warning(
            f"File validation failed: {file.filename}, "
            f"error: {e.message}, "
            f"client_ip: {request.client.host}"
        )
        raise HTTPException(status_code=e.status_code, detail=e.message)
        
    except Exception as e:
        # Log unexpected errors
        logger.error(
            f"Unexpected error processing file: {file.filename}, "
            f"error: {str(e)}, "
            f"client_ip: {request.client.host}"
        )
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)