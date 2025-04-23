"""Basic tests for the Flask application."""
import pytest
from app import create_app
from app.config import TestingConfig


def test_health_endpoint():
    """Test the health check endpoint."""
    app = create_app(TestingConfig)
    with app.test_client() as client:
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json == {"status": "healthy"} 