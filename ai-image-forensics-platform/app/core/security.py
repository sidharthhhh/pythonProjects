from fastapi import HTTPException, UploadFile, Request
import magic
from app.core.config import settings

async def validate_file_size(request: Request):
    """Check if the content length exceeds the maximum allowed size."""
    if "content-length" not in request.headers:
        raise HTTPException(status_code=411, detail="Length Required")
    
    content_length = int(request.headers["content-length"])
    if content_length > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )

async def validate_image_file(file: UploadFile) -> bytes:
    """Read the file, check its magic number for basic type verification, and return bytes."""
    contents = await file.read()
    
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file provided")
        
    mime = magic.from_buffer(contents, mime=True)
    extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if extension not in settings.ALLOWED_IMAGE_FORMATS:
         raise HTTPException(status_code=415, detail=f"Unsupported file extension: {extension}")
         
    if not mime.startswith('image/'):
        raise HTTPException(status_code=415, detail="Invalid file type. Must be an image.")
        
    # Rewind for later use if needed, but we typically use the bytes
    await file.seek(0)
    
    return contents

async def verify_authentication(request: Request):
    """Stub for verifying API keys or JWT tokens."""
    # TODO: Implement actual secure API gateway authentication
    pass
