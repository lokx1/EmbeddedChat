# Unit tests for services
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.api.middleware.auth import (
    verify_password, get_password_hash, create_access_token
)
from src.schemas.user import UserCreate
from src.core.config import settings


class TestAuthService:
    """Test authentication service functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        
        # Hash password
        hashed = get_password_hash(password)
        
        # Verify correct password
        assert verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        
        token = create_access_token(data, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0


class TestSchemaValidation:
    """Test Pydantic schema validation"""
    
    def test_user_create_valid(self):
        """Test valid user creation schema"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        user = UserCreate(**user_data)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "testpassword123"
        assert user.full_name == "Test User"
    
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        with pytest.raises(ValueError):
            UserCreate(**user_data)
    
    def test_user_create_short_password(self):
        """Test user creation with short password"""
        user_data = {
            "username": "testuser", 
            "email": "test@example.com",
            "password": "short"
        }
        
        with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
            UserCreate(**user_data)


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @patch('time.time')
    def test_rate_limit_tracking(self, mock_time):
        """Test rate limit request tracking"""
        from src.api.middleware.rate_limiting import RateLimitMiddleware
        
        # Mock current time
        mock_time.return_value = 1000.0
        
        app = Mock()
        middleware = RateLimitMiddleware(app, calls=5, period=60)
        
        # Simulate client making requests
        client_ip = "127.0.0.1"
        middleware.clients[client_ip] = {
            "requests": [990.0, 995.0, 998.0],  # 3 recent requests
            "blocked_until": 0
        }
        
        # Should allow 2 more requests (5 total limit)
        assert len(middleware.clients[client_ip]["requests"]) == 3
    
    def test_rate_limit_cleanup(self):
        """Test cleanup of old requests"""
        from src.api.middleware.rate_limiting import RateLimitMiddleware
        
        app = Mock()
        middleware = RateLimitMiddleware(app, calls=5, period=60)
        
        current_time = 1000.0
        client_ip = "127.0.0.1"
        
        # Add old and recent requests
        middleware.clients[client_ip] = {
            "requests": [900.0, 930.0, 995.0, 998.0],  # Mix of old/new
            "blocked_until": 0
        }
        
        # Clean old requests (older than 60 seconds)
        middleware.clients[client_ip]["requests"] = [
            req_time for req_time in middleware.clients[client_ip]["requests"]
            if current_time - req_time < middleware.period
        ]
        
        # Should only have 2 recent requests left
        assert len(middleware.clients[client_ip]["requests"]) == 2
        assert 995.0 in middleware.clients[client_ip]["requests"]
        assert 998.0 in middleware.clients[client_ip]["requests"]


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_cors_origins_string(self):
        """Test CORS origins parsing from string"""
        from src.core.config import Settings
        
        # Test string input
        test_origins = "http://localhost:3000,http://localhost:8080"
        settings_instance = Settings(BACKEND_CORS_ORIGINS=test_origins)
        
        assert isinstance(settings_instance.BACKEND_CORS_ORIGINS, list)
        assert len(settings_instance.BACKEND_CORS_ORIGINS) == 2
        assert "http://localhost:3000" in settings_instance.BACKEND_CORS_ORIGINS
    
    def test_cors_origins_list(self):
        """Test CORS origins as list"""
        from src.core.config import Settings
        
        test_origins = ["http://localhost:3000", "http://localhost:8080"]
        settings_instance = Settings(BACKEND_CORS_ORIGINS=test_origins)
        
        assert isinstance(settings_instance.BACKEND_CORS_ORIGINS, list)
        assert len(settings_instance.BACKEND_CORS_ORIGINS) == 2


class TestExceptionHandlers:
    """Test custom exception handlers"""
    
    def test_http_404_exception(self):
        """Test 404 exception creation"""
        from src.core.exceptions import http_404_not_found
        
        exception = http_404_not_found("Resource not found")
        
        assert exception.status_code == 404
        assert exception.detail == "Resource not found"
    
    def test_http_401_exception(self):
        """Test 401 exception creation"""
        from src.core.exceptions import http_401_unauthorized
        
        exception = http_401_unauthorized("Invalid credentials")
        
        assert exception.status_code == 401
        assert exception.detail == "Invalid credentials"
        assert exception.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_http_429_exception(self):
        """Test 429 rate limit exception"""
        from src.core.exceptions import http_429_rate_limit
        
        exception = http_429_rate_limit("Too many requests")
        
        assert exception.status_code == 429
        assert exception.detail == "Too many requests"
