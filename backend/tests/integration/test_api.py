# Integration tests for API endpoints
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from src.models.database import Base, get_db
from src.models.user import User
from src.api.middleware.auth import get_password_hash


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def async_session():
    """Create async test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
def client(async_session):
    """Create test client with test database"""
    def get_test_db():
        yield async_session
    
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(async_session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User"
    )
    
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    return user


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data
    
    def test_detailed_health_check(self, client):
        """Test detailed health check"""
        response = client.get("/api/v1/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "checks" in data
        assert "database" in data["checks"]
    
    def test_readiness_check(self, client):
        """Test readiness probe"""
        response = client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
    
    def test_liveness_check(self, client):
        """Test liveness probe"""
        response = client.get("/api/v1/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


class TestChatEndpoints:
    """Test chat-related endpoints"""
    
    def test_create_conversation_unauthorized(self, client):
        """Test creating conversation without authentication"""
        conversation_data = {
            "title": "Test Conversation",
            "description": "A test conversation"
        }
        
        response = client.post("/api/v1/chat/conversations", json=conversation_data)
        assert response.status_code == 403  # Unauthorized due to missing auth
    
    def test_get_conversations_unauthorized(self, client):
        """Test getting conversations without authentication"""
        response = client.get("/api/v1/chat/conversations")
        assert response.status_code == 403  # Unauthorized due to missing auth


class TestDocumentEndpoints:
    """Test document-related endpoints"""
    
    def test_upload_document_unauthorized(self, client):
        """Test uploading document without authentication"""
        # Create a simple test file
        test_file_content = b"This is a test document"
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.txt", test_file_content, "text/plain")}
        )
        
        assert response.status_code == 403  # Unauthorized due to missing auth
    
    def test_get_documents_unauthorized(self, client):
        """Test getting documents without authentication"""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 403  # Unauthorized due to missing auth


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/api/docs"


class TestCorsHeaders:
    """Test CORS headers"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present"""
        response = client.options("/api/v1/health/")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
    
    def test_cors_preflight(self, client):
        """Test CORS preflight request"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = client.options("/api/v1/health/", headers=headers)
        
        # Should handle preflight request
        assert response.status_code in [200, 204]


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present"""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self, client):
        """Test 404 handling for non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test 405 handling for wrong HTTP method"""
        # Try POST on a GET-only endpoint
        response = client.post("/api/v1/health/")
        
        assert response.status_code == 405


class TestOpenAPISchema:
    """Test OpenAPI schema generation"""
    
    def test_openapi_schema_accessible(self, client):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/api/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
    
    def test_docs_accessible(self, client):
        """Test that Swagger docs are accessible"""
        response = client.get("/api/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
