import os
from datetime import datetime
from typing import Optional

from app.core.config import ALLOWED_FILE_TYPES, CHUNK_SIZE, MAX_FILE_SIZE
from app.core.constants import redis_client
from fastapi import UploadFile


# Custom exception for file validation errors
class FileValidationError(Exception):
    """Custom exception for file validation errors"""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Validate the file headers
async def validate_file_headers(
    content_type: Optional[str], content_length: Optional[int], filename: Optional[str]
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
            415,
        )

    if content_length > MAX_FILE_SIZE:
        raise FileValidationError(
            f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB", 413
        )


# Validate the file content
async def validate_file_content(file: UploadFile, temp_file_path: str) -> int:
    """
    Second layer validation - Actual content validation
    This is done at the application level
    """
    total_size = 0

    try:
        while chunk := await file.read(CHUNK_SIZE):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise FileValidationError(
                    f"Actual file size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB",
                    413,
                )
            with open(temp_file_path, "ab") as f:
                f.write(chunk)

        # Verify file extension matches content type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension != ALLOWED_FILE_TYPES[file.content_type]:
            raise FileValidationError(
                f"File extension {file_extension} does not match content type {file.content_type}",
                415,
            )

        return total_size
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise e


# Check if the user has exceeded the rate limit for the given endpoint using a sliding window
def check_rate_limit(
    user_email: str, endpoint: str, max_requests: int = 20, window_seconds: int = 86400
) -> bool:
    """
    Check if the user has exceeded the rate limit for the given endpoint using a sliding window
    """
    # Create Redis key for the sliding window
    redis_key = f"rate_limit:{endpoint}:{user_email}"

    # Get current count
    current_count = redis_client.get(redis_key)

    if current_count is None:
        # First request in the window
        redis_client.setex(redis_key, window_seconds, 1)
        return True

    current_count = int(current_count)
    if current_count >= max_requests:
        return False

    # Increment counter
    redis_client.incr(redis_key)
    return True
