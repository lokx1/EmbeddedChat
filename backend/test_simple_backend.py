#!/usr/bin/env python3
"""
Quick test to start simple backend without database
"""
import uvicorn
from simple_upload import app

if __name__ == "__main__":
    print("🚀 Starting simple backend for testing...")
    print("📁 Upload files to: http://localhost:8000/api/v1/documents/upload")
    print("📋 List files at: http://localhost:8000/api/v1/documents/")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
