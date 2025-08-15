# Application entry point
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import asyncio
import os

from src.core.config import settings
from src.api.middleware.cors import add_cors_middleware
from src.api.middleware.rate_limiting import add_rate_limit_middleware
from src.api.routes import health, chat, documents, auth, dashboard, workflow
from src.models.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Initialize database
    try:
        engine, _ = init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("🔄 Continuing without database...")
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")
    try:
        engine, _ = init_database()
        if engine:
            await engine.dispose()
            print("✅ Database connection closed")
    except Exception as e:
        print(f"⚠️ Error closing database: {e}")


def create_application() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # Add security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this properly in production
    )
    
    # Add custom middleware
    add_cors_middleware(app)
    add_rate_limit_middleware(app)
    
    # Include routers
    app.include_router(health.router, prefix=settings.API_V1_STR)
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(chat.router, prefix=settings.API_V1_STR)
    app.include_router(documents.router, prefix=settings.API_V1_STR)
    app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard")
    app.include_router(workflow.router, prefix=settings.API_V1_STR)
    
    # Include routers without prefix for backward compatibility
    app.include_router(health.router, tags=["health-v0"])
    app.include_router(auth.router, tags=["auth-v0"])
    app.include_router(chat.router, tags=["chat-v0"])
    app.include_router(documents.router, tags=["documents-v0"])
    app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard-v0"])
    
    return app


# Create FastAPI app
app = create_application()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get PORT from environment for Railway, with proper error handling
    try:
        port = int(os.environ.get("PORT", "8000"))
    except (ValueError, TypeError):
        port = 8000
    
    print(f"🚀 Starting server on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
