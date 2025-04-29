"""Pytest fixtures for the bathroom map application tests."""
import os
import pytest
import mongomock
from flask import Flask
from bson import ObjectId
from datetime import datetime, timedelta
import importlib
import json
from werkzeug.security import generate_password_hash

# Set test environment variables before importing anything
os.environ["FLASK_ENV"] = "testing"
os.environ["TESTING"] = "true"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["MONGO_DBNAME"] = "test_bathroom_map"

# Now import app module
import app as app_module
from schemas import init_app

@pytest.fixture(scope="session")
def app():
    """Create a Flask app fixture for testing."""
    # Create app
    flask_app = app_module.create_app()
    flask_app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "SECRET_KEY": "test_secret_key",
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DBNAME": "test_bathroom_map",
        "SERVER_NAME": "localhost.localdomain",  # Needed for url_for in tests
        "WTF_CSRF_ENABLED": False  # Disable CSRF for testing
    })
    
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client."""
    with app.test_client() as client:
        # Enable session in the test client
        client.application = app
        with app.app_context():
            yield client

@pytest.fixture(scope="function", autouse=True)
def setup_db(app, monkeypatch):
    """Set up the test database for each test."""
    # Create a mock MongoDB client
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["test_bathroom_map"]
    
    # Define mock get_db function to return our mock_db
    def mock_get_db():
        return mock_db
    
    # Patch the real get_db with our mock and skip real db initialization BEFORE any test runs
    import schemas.database
    monkeypatch.setattr("schemas.database.get_db", mock_get_db)
    monkeypatch.setattr("schemas.models.init_db", lambda app: None)
    
    # Set up all required indexes in mock db
    mock_db.users.create_index("email", unique=True)
    
    # Create indexes for test collections (mongomock doesn't fully support geospatial)
    try:
        mock_db.bathrooms.create_index("building")
        mock_db.reviews.create_index("bathroom_id")
        mock_db.reviews.create_index("user_id")
    except Exception as e:
        print(f"Warning: Could not create some indexes in test DB: {e}")
    
    # Clear collections before each test
    for collection in mock_db.list_collection_names():
        mock_db[collection].delete_many({})
    
    # Make the mock_db accessible from app
    app.mock_db = mock_db
    
    # Run test with app context
    with app.app_context():
        yield mock_db

@pytest.fixture
def mock_user_id():
    """Generate a mock user ID."""
    return str(ObjectId())

@pytest.fixture
def mock_user(setup_db, mock_user_id):
    """Create a mock user in the database."""
    user = {
        "_id": ObjectId(mock_user_id),
        "email": "test@example.com",
        "password_hash": generate_password_hash("password"),
        "name": "Test User",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    setup_db.users.insert_one(user)
    return user

@pytest.fixture
def mock_bathroom(setup_db):
    """Create a mock bathroom in the database."""
    bathroom_id = ObjectId()
    bathroom = {
        "_id": bathroom_id,
        "building": "Test Building",
        "floor": 1,
        "location": {
            "type": "Point",
            "coordinates": [0.0, 0.0]
        },
        "is_accessible": True,
        "gender": "all",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": str(ObjectId())
    }
    setup_db.bathrooms.insert_one(bathroom)
    return bathroom

@pytest.fixture
def mock_review(setup_db, mock_bathroom, mock_user_id):
    """Create a mock review in the database."""
    review = {
        "_id": ObjectId(),
        "bathroom_id": str(mock_bathroom["_id"]),
        "user_id": mock_user_id,
        "ratings": {
            "cleanliness": 4,
            "privacy": 3,
            "accessibility": 4
        },
        "best_for": "Quick stop",
        "comment": "Test review comment",
        "created_at": datetime.utcnow()
    }
    setup_db.reviews.insert_one(review)
    return review

@pytest.fixture
def login_user(client, mock_user, setup_db, app):
    """Log in the mock user."""
    # Create a token directly instead of relying on the login endpoint
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=str(mock_user["_id"]))
    
    # Create a client with token in headers (more reliable than cookies for testing)
    class AuthClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token
            
        def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {})
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.get(*args, **kwargs)
            
        def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {})
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.post(*args, **kwargs)
            
        def put(self, *args, **kwargs):
            kwargs.setdefault('headers', {})
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.put(*args, **kwargs)
            
        def delete(self, *args, **kwargs):
            kwargs.setdefault('headers', {})
            kwargs['headers']['Authorization'] = f'Bearer {self.token}'
            return self.client.delete(*args, **kwargs)
    
    # Return the wrapped client
    return AuthClient(client, access_token)

@pytest.fixture
def db(setup_db):
    """Alias for setup_db to maintain backward compatibility with tests."""
    return setup_db 