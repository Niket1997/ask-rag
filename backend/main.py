# backend application for the ask-rag application
# this will expose following endpoints:
# 1. /ingest
# 2. /ask
# 3. /authenticate # optional

from fastapi import FastAPI, UploadFile, HTTPException
from ingestion import ingest_pdf
import os
import tempfile

app = FastAPI()

# Define allowed file types and their MIME types
ALLOWED_FILE_TYPES = {
    "application/pdf": ".pdf",
    "application/json": ".json",
    "text/csv": ".csv"
}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/ingest")
async def ingest_file(file: UploadFile):
    # Check file size
    file_size = 0
    chunk_size = 1024  # 1KB chunks
    
    # Read file in chunks to check size
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE/1024/1024}MB"
            )
    
    # Reset file pointer
    await file.seek(0)
    
    # Check file type
    content_type = file.content_type
    if content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed types are: {', '.join(ALLOWED_FILE_TYPES.values())}"
        )
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ALLOWED_FILE_TYPES[content_type]) as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        if content_type == "application/pdf":
            # Pass the temporary file path to ingest_pdf
            response = ingest_pdf(temp_file_path)
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            return {
                "filename": file.filename,
                "content_type": content_type,
                "size": file_size,
                "message": response
            }
        
        # Clean up the temporary file for other file types
        os.unlink(temp_file_path)
        return {
            "filename": file.filename,
            "error": "File type not supported"
        }

    except Exception as e:
        # Clean up the temporary file in case of error
        if 'temp_file_path' in locals():
            os.unlink(temp_file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )