from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="EmbeddedChat API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        "message": "🚀 EmbeddedChat Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/test")
async def test_api():
    """Test endpoint for frontend"""
    return {
        "status": "success",
        "message": "✅ Backend API working!",
        "cors": "enabled",
        "environment": "production"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def health_v1():
    """Health check v1"""
    return {"status": "healthy", "version": "v1"}

# This is the key for Vercel
def handler(event, context):
    """Vercel serverless handler"""
    return app(event, context)

# Also keep this for compatibility
app_handler = app 