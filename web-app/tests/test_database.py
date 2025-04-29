"""Tests for database connection functionality."""
import pytest
from flask import Flask, g
from pymongo.database import Database
from pymongo.collection import Collection

from schemas.database import init_app, get_db, close_db


def test_get_db_outside_context():
    """Test that get_db raises an exception outside app context."""
    # When/Then
    with pytest.raises(RuntimeError):
        get_db()


def test_get_db(app):
    """Test that get_db returns a database connection."""
    # When
    with app.app_context():
        db = get_db()
        
        # Then
        assert db is not None
        assert isinstance(db, Database)
        
        # Check that collections exist
        assert isinstance(db.users, Collection)
        assert isinstance(db.bathrooms, Collection)
        assert isinstance(db.reviews, Collection)


def test_get_db_same_connection(app):
    """Test that get_db returns the same connection within context."""
    # When
    with app.app_context():
        db1 = get_db()
        db2 = get_db()
        
        # Then
        assert db1 is db2


def test_close_db(app):
    """Test that close_db removes the db connection from g."""
    # When
    with app.app_context():
        db = get_db()
        assert hasattr(g, "mongo_db")
        
        close_db(None)
        
        # Then
        assert not hasattr(g, "mongo_db")


def test_init_app(app):
    """Test that init_app properly initializes the app."""
    # Given
    test_app = Flask(__name__)
    
    # When
    init_app(test_app)
    
    # Then
    assert "teardown_appcontext" in test_app.teardown_funcs[None]
    
    # Test that get_db works with the initialized app
    with test_app.app_context():
        db = get_db()
        assert db is not None 