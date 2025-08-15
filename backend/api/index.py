from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="EmbeddedChat Backend API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "https://embedded-chat-psi.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to EmbeddedChat Backend API",
        "version": "1.0.0",
        "status": "Backend is running on Vercel!",
        "docs": "/docs"
    }

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint for debugging connectivity"""
    return {
        "status": "success",
        "message": "Backend API is working on Vercel!",
        "environment": "production"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "embedded-chat-backend"
    }

# This is required for Vercel
handler = app 