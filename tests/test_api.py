"""
Test cases for AI Reception System API
Run with: pytest -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

class TestHealth:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test API health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

class TestRoot:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test API root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

class TestOpenAPI:
    """Test OpenAPI schema"""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema availability"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "info" in schema

    def test_swagger_ui(self):
        """Test Swagger UI availability"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()

    def test_redoc_ui(self):
        """Test ReDoc UI availability"""
        response = client.get("/redoc")
        assert response.status_code == 200

# Example test for API endpoints (uncomment when database is configured)
# class TestCalls:
#     """Test call endpoints"""
#     
#     def test_create_call(self):
#         """Test creating a call log"""
#         response = client.post(
#             "/api/v1/calls",
#             json={
#                 "business_id": "550e8400-e29b-41d4-a716-446655440000",
#                 "caller_phone": "555-1234",
#                 "caller_name": "John Doe"
#             }
#         )
#         assert response.status_code in [200, 201, 422]  # 422 if validation fails

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
