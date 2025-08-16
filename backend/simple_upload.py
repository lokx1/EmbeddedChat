#!/usr/bin/env python3
"""
Simple file upload endpoint for testing without database
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import uuid
from pathlib import Path
import json

app = FastAPI(title="Simple Upload Test")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    ai_provider: str = Form(None),
    api_key: str = Form(None)
):
    """Simple upload without database"""
    try:
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create mock response like database would
        result = {
            "id": 1,
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "mime_type": file.content_type,
            "status": "ready",
            "extracted_text": content.decode('utf-8', errors='ignore') if file.content_type.startswith('text/') else "Binary file",
            "summary": f"Uploaded file: {file.filename}",
            "created_at": "2025-08-16T12:00:00Z",
            "updated_at": "2025-08-16T12:00:00Z"
        }
        
        print(f"✅ Successfully uploaded: {file.filename} -> {unique_filename}")
        print(f"   Size: {len(content)} bytes")
        print(f"   Type: {file.content_type}")
        
        return result
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return {"error": str(e)}

@app.get("/api/v1/documents/")
async def list_documents():
    """List uploaded files"""
    files = []
    if UPLOAD_DIR.exists():
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "id": hash(file_path.name) % 1000,
                    "filename": file_path.name,
                    "original_filename": file_path.name,
                    "file_size": stat.st_size,
                    "status": "ready"
                })
    
    return {
        "documents": files,
        "total": len(files),
        "page": 1,
        "size": len(files)
    }

@app.get("/")
async def root():
    return {"message": "Simple Upload Test Server", "status": "running"}

if __name__ == "__main__":
    print("🚀 Starting simple upload server...")
    print("📁 Upload directory:", UPLOAD_DIR.absolute())
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
