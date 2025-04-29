"""Pytest fixtures for the bathroom map application tests."""
import os
import pytest
import mongomock
from flask import Flask, g
from bson import ObjectId
from datetime import datetime, timedelta
import importlib
from pymongo import GEOSPHERE

# Import app but not create_app yet
import app as app_module
from schemas import init_app


# Mock the database initialization
class MockDB:
    def __init__(self):
        self.client = mongomock.MongoClient()
        self.db = self.client['test_bathroom_map']
        
        # Create indexes
        self.db.users.create_index("email", unique=True)
        self.db.bathrooms.create_index([("location", GEOSPHERE)])
        self.db.bathrooms.create_index("building")
        self.db.reviews.create_index("bathroom_id")
        self.db.reviews.create_index("user_id")
    
    def get_db(self):
        return self.db


# Replace the real get_db with our mock version
@pytest.fixture(autouse=True)
def mock_get_db(monkeypatch):
    """Replace the real get_db with our mock version."""
    mock_db = MockDB()
    
    def mock_get_db_func():
        return mock_db.db
    
    # Patch both the init_db function and get_db function
    import schemas.models
    monkeypatch.setattr('schemas.database.get_db', mock_get_db_func)
    monkeypatch.setattr('schemas.models.init_db', lambda app: None)  # Do nothing
    
    return mock_db.db


@pytest.fixture
def app():
    """Create a Flask app fixture for testing."""
    # Set test configuration
    os.environ["FLASK_ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key"
    os.environ["MONGO_URI"] = "mongodb://admin:secret@localhost:27017"
    os.environ["MONGO_DBNAME"] = "test_bathroom_map"
    
    # Reload app module to get fresh create_app with patched dependencies
    importlib.reload(app_module)
    
    # Create app
    flask_app = app_module.create_app()
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "JWT_SECRET_KEY": "test_jwt_secret_key",
        "MONGO_URI": "mongodb://admin:secret@localhost:27017",
        "MONGO_DBNAME": "test_bathroom_map"
    })
    
    return flask_app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def db(mock_get_db):
    """Get the mocked database."""
    # Clear all collections before each test
    for collection_name in mock_get_db.list_collection_names():
        mock_get_db[collection_name].delete_many({})
    return mock_get_db


@pytest.fixture
def mock_user_id():
    """Generate a mock user ID."""
    return str(ObjectId())


@pytest.fixture
def mock_user(db, mock_user_id):
    """Create a mock user in the database."""
    user = {
        "_id": ObjectId(mock_user_id),
        "email": "test@example.com",
        "password_hash": "pbkdf2:sha256:150000$MOCK_HASH",
        "name": "Test User",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    db.users.insert_one(user)
    return user


@pytest.fixture
def mock_bathroom(db):
    """Create a mock bathroom in the database."""
    bathroom = {
        "_id": ObjectId(),
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
    result = db.bathrooms.insert_one(bathroom)
    bathroom["_id"] = result.inserted_id
    return bathroom


@pytest.fixture
def mock_review(db, mock_bathroom, mock_user_id):
    """Create a mock review in the database."""
    review = {
        "_id": ObjectId(),
        "bathroom_id": str(mock_bathroom["_id"]),
        "user_id": mock_user_id,
        "ratings": {
            "cleanliness": 4,
            "privacy": 4,
            "accessibility": 4
        },
        "best_for": "number 1",
        "comment": "Test review comment",
        "created_at": datetime.utcnow()
    }
    result = db.reviews.insert_one(review)
    review["_id"] = result.inserted_id
    return review


@pytest.fixture
def auth_headers(app, mock_user_id):
    """Create auth headers with JWT token."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(
            identity=mock_user_id,
            expires_delta=timedelta(hours=1)
        )
        return {"Authorization": f"Bearer {access_token}"} 