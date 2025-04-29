"""Pytest fixtures for the bathroom map application tests."""
import os
import pytest
import mongomock
from flask import Flask
from bson import ObjectId
from datetime import datetime, timedelta

from app import create_app
from schemas import init_app, init_db


@pytest.fixture
def app() -> Flask:
    """Create a Flask app fixture for testing.
    
    Returns:
        Flask: A Flask app configured for testing
    """
    # Set test configuration
    os.environ["FLASK_ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key"
    os.environ["MONGO_URI"] = "mongodb://localhost:27017"
    os.environ["MONGO_DBNAME"] = "test_bathroom_map"
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "JWT_SECRET_KEY": "test_jwt_secret_key",
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DBNAME": "test_bathroom_map"
    })
    
    # Use mongomock for testing
    app.config["MONGO_CLIENT"] = mongomock.MongoClient()
    
    # Initialize app with test configuration
    with app.app_context():
        init_db(app)
    
    yield app


@pytest.fixture
def client(app: Flask):
    """Create a test client for the app.
    
    Args:
        app: The Flask app
        
    Returns:
        Flask test client
    """
    return app.test_client()


@pytest.fixture
def db(app: Flask):
    """Create a test database connection.
    
    Args:
        app: The Flask app
        
    Returns:
        MongoDB test client
    """
    with app.app_context():
        from schemas import get_db
        # Clear all collections before each test
        for collection in get_db().list_collection_names():
            get_db()[collection].delete_many({})
        return get_db()


@pytest.fixture
def mock_user_id() -> str:
    """Generate a mock user ID.
    
    Returns:
        str: Mock user ID
    """
    return str(ObjectId())


@pytest.fixture
def mock_user(db, mock_user_id) -> dict:
    """Create a mock user in the database.
    
    Args:
        db: The test database
        mock_user_id: Mock user ID
        
    Returns:
        dict: User document
    """
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
def mock_bathroom(db) -> dict:
    """Create a mock bathroom in the database.
    
    Args:
        db: The test database
        
    Returns:
        dict: Bathroom document
    """
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
def mock_review(db, mock_bathroom, mock_user_id) -> dict:
    """Create a mock review in the database.
    
    Args:
        db: The test database
        mock_bathroom: Mock bathroom document
        mock_user_id: Mock user ID
        
    Returns:
        dict: Review document
    """
    review = {
        "_id": ObjectId(),
        "bathroom_id": str(mock_bathroom["_id"]),
        "user_id": mock_user_id,
        "rating": 4,
        "comment": "Test review comment",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = db.reviews.insert_one(review)
    review["_id"] = result.inserted_id
    return review


@pytest.fixture
def auth_headers(app, mock_user_id) -> dict:
    """Create auth headers with JWT token.
    
    Args:
        app: The Flask app
        mock_user_id: Mock user ID
        
    Returns:
        dict: Headers with JWT token
    """
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(
            identity=mock_user_id,
            expires_delta=timedelta(hours=1)
        )
        return {"Authorization": f"Bearer {access_token}"} 