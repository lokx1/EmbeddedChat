#!/usr/bin/env python3
"""
Railway startup script for EmbeddedChat backend
"""
import os
import sys
import uvicorn

def main():
    # Debug environment variables
    print("=== Environment Debug ===")
    print(f"PORT env var: {repr(os.environ.get('PORT'))}")
    print(f"All env vars: {dict(os.environ)}")
    
    # Get port with multiple fallbacks
    port = None
    
    # Try PORT environment variable
    if 'PORT' in os.environ:
        try:
            port = int(os.environ['PORT'])
            print(f"✅ Using PORT from environment: {port}")
        except (ValueError, TypeError) as e:
            print(f"❌ Invalid PORT value: {repr(os.environ['PORT'])}, error: {e}")
    
    # Fallback to default
    if port is None:
        port = 8000
        print(f"🔄 Using default port: {port}")
    
    # Import the app
    try:
        from main import app
        print("✅ Successfully imported FastAPI app")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        sys.exit(1)
    
    # Start server
    print(f"🚀 Starting uvicorn server on 0.0.0.0:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 