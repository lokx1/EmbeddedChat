from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app - SIMPLE VERSION
app = FastAPI(
    title="EmbeddedChat Backend API",
    version="1.0.0",
    description="Simple API for EmbeddedChat"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "https://embedded-chat-psi.vercel.app",
        "https://*.vercel.app",
        "*"  # Allow all for testing
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 EmbeddedChat Backend API is running!",
        "version": "1.0.0",
        "status": "success",
        "platform": "Vercel Serverless",
        "docs": "/docs"
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for frontend connectivity"""
    return {
        "status": "success", 
        "message": "✅ Backend API is working perfectly!",
        "timestamp": "2025-01-16",
        "environment": "production",
        "cors_enabled": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "embedded-chat-backend",
        "uptime": "ok"
    }

@app.get("/api/v1/health")
async def health_v1():
    """Health check v1 endpoint"""
    return {
        "status": "healthy",
        "version": "v1"
    }

# Vercel handler
handler = app 