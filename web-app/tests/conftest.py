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


@pytest.fixture(autouse=True)
def mock_get_db(monkeypatch):
    """Replace the real get_db with our mock version."""
    # Create a fresh mock DB for each test
    mock_db = MockDB()
    db = mock_db.db
    
    # Clear any existing data
    for collection_name in db.list_collection_names():
        db[collection_name].delete_many({})
    
    # Define our mocked get_db function
    def mock_get_db_func():
        return db
    
    # Import database module
    import schemas.database
    
    # Patch the database connection function
    monkeypatch.setattr('schemas.database.get_db', mock_get_db_func)
    
    # Skip database initialization in tests
    import schemas.models
    monkeypatch.setattr('schemas.models.init_db', lambda app: None)
    
    # Ensure Flask g object is clean
    if hasattr(g, 'db'):
        delattr(g, 'db')
    
    return db


@pytest.fixture
def app():
    """Create a Flask app fixture for testing."""
    # Set test configuration
    os.environ["FLASK_ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key"
    os.environ["MONGO_URI"] = "mongodb://localhost:27017"
    os.environ["MONGO_DBNAME"] = "test_bathroom_map"
    
    # Reload the app module to get a fresh application instance each test
    importlib.reload(app_module)
    
    # Create app with test config
    flask_app = app_module.create_app()
    flask_app.config.update({
        "TESTING": True,
        "DEBUG": False,
        "SECRET_KEY": "test_secret_key",
        "JWT_SECRET_KEY": "test_jwt_secret_key",
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DBNAME": "test_bathroom_map"
    })
    
    # Return the app - the client fixture will handle context
    return flask_app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    # Set up app context for each test
    with app.app_context():
        # Create test client
        with app.test_client() as test_client:
            yield test_client


@pytest.fixture
def db(mock_get_db):
    """Get the mocked database."""
    # The database is already cleared in mock_get_db
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
    db.bathrooms.insert_one(bathroom)  # Insert directly
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
    db.reviews.insert_one(review)
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