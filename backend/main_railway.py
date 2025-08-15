import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="EmbeddedChat API",
    version="1.0.0",
    description="EmbeddedChat Backend API deployed on Railway"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://embedded-chat-psi.vercel.app",
        "https://*.vercel.app",
        "*"  # Allow all for now
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 EmbeddedChat API on Railway!",
        "version": "1.0.0",
        "status": "running",
        "platform": "Railway",
        "docs": "/docs"
    }

@app.get("/api/test")
async def test_api():
    """Test endpoint for frontend connectivity"""
    return {
        "status": "success",
        "message": "✅ Railway Backend API working!",
        "platform": "Railway",
        "cors": "enabled",
        "environment": "production"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "embedded-chat-backend",
        "platform": "Railway"
    }

@app.get("/api/v1/health")
async def health_v1():
    """Health check v1 endpoint"""
    return {
        "status": "healthy",
        "version": "v1",
        "platform": "Railway"
    }

# Add some sample API endpoints that your frontend might need
@app.get("/api/v1/chat")
async def chat_endpoint():
    """Sample chat endpoint"""
    return {
        "message": "Chat endpoint working",
        "status": "ready"
    }

@app.get("/api/v1/auth")
async def auth_endpoint():
    """Sample auth endpoint"""
    return {
        "message": "Auth endpoint working",
        "status": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main_railway:app", host="0.0.0.0", port=port, reload=False) 