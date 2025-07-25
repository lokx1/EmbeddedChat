# Application entry point
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import asyncio

from src.core.config import settings
from src.api.middleware.cors import add_cors_middleware
from src.api.middleware.rate_limiting import add_rate_limit_middleware
from src.api.routes import health, chat, documents, auth, dashboard
from src.models.database import engine
from src.models import user, conversation, message, document


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Skip table creation - tables already exist
    # async with engine.begin() as conn:
    #     # Import all models to ensure they are registered
    #     from src.models.database import Base
    #     await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")
    await engine.dispose()


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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
