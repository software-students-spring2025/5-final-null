"""Tests for database models and schemas."""
import pytest
from datetime import datetime
from bson import ObjectId

from schemas.models import Bathroom, Review, User


def test_user_model_creation():
    """Test creating a User document."""
    # When
    user_doc = User.create_document(
        email="test@example.com",
        password_hash="hashed_password",
        name="Test User"
    )
    
    # Then
    assert user_doc["email"] == "test@example.com"
    assert user_doc["password_hash"] == "hashed_password"
    assert user_doc["name"] == "Test User"
    assert "created_at" in user_doc
    assert "updated_at" in user_doc
    assert isinstance(user_doc["created_at"], datetime)
    assert isinstance(user_doc["updated_at"], datetime)


def test_bathroom_model_creation():
    """Test creating a Bathroom document."""
    # When
    bathroom_doc = Bathroom.create_document(
        building="Test Building",
        floor=2,
        latitude=42.3601,
        longitude=-71.0589,
        is_accessible=True,
        gender="all"
    )
    
    # Then
    assert bathroom_doc["building"] == "Test Building"
    assert bathroom_doc["floor"] == 2
    assert bathroom_doc["location"]["type"] == "Point"
    assert bathroom_doc["location"]["coordinates"] == [-71.0589, 42.3601]
    assert bathroom_doc["is_accessible"] is True
    assert bathroom_doc["gender"] == "all"
    assert "created_at" in bathroom_doc
    assert "updated_at" in bathroom_doc


def test_bathroom_model_default_values():
    """Test that Bathroom model uses default values correctly."""
    # When - Only provide required fields
    bathroom_doc = Bathroom.create_document(
        building="Minimal Building",
        floor=3,
        latitude=42.0,
        longitude=-71.0
    )
    
    # Then - Default values should be used
    assert bathroom_doc["building"] == "Minimal Building"
    assert bathroom_doc["floor"] == 3
    assert bathroom_doc["is_accessible"] is False  # Default
    assert bathroom_doc["gender"] == "all"  # Default


def test_bathroom_model_invalid_gender():
    """Test that creating a Bathroom with invalid gender raises error."""
    # When/Then
    with pytest.raises(ValueError):
        Bathroom.create_document(
            building="Invalid Gender Building",
            floor=1,
            latitude=0,
            longitude=0,
            gender="invalid_value"  # Should be 'male', 'female', or 'all'
        )


def test_bathroom_model_invalid_floor():
    """Test that creating a Bathroom with invalid floor raises error."""
    # When/Then
    with pytest.raises(ValueError):
        Bathroom.create_document(
            building="Invalid Floor Building",
            floor=-1,  # Should be positive
            latitude=0,
            longitude=0
        )


def test_review_model_creation():
    """Test creating a Review document."""
    # Given
    bathroom_id = str(ObjectId())
    user_id = str(ObjectId())
    
    # When
    review_doc = Review.create_document(
        bathroom_id=bathroom_id,
        user_id=user_id,
        cleanliness=4,
        privacy=3,
        accessibility=5,
        best_for="Quick stop",
        comment="Great bathroom!"
    )
    
    # Then
    assert review_doc["bathroom_id"] == bathroom_id
    assert review_doc["user_id"] == user_id
    assert review_doc["ratings"]["cleanliness"] == 4
    assert review_doc["ratings"]["privacy"] == 3
    assert review_doc["ratings"]["accessibility"] == 5
    assert review_doc["best_for"] == "Quick stop"
    assert review_doc["comment"] == "Great bathroom!"
    assert "created_at" in review_doc


def test_review_model_invalid_rating():
    """Test that creating a Review with invalid rating raises error."""
    # When/Then
    with pytest.raises(ValueError):
        Review.create_document(
            bathroom_id=str(ObjectId()),
            user_id=str(ObjectId()),
            cleanliness=6,  # Should be 1-5
            privacy=3,
            accessibility=4,
            best_for="Invalid",
            comment="Invalid rating"
        )
    
    with pytest.raises(ValueError):
        Review.create_document(
            bathroom_id=str(ObjectId()),
            user_id=str(ObjectId()),
            cleanliness=3,
            privacy=0,  # Should be 1-5
            accessibility=4,
            best_for="Invalid",
            comment="Invalid rating"
        )
        
    with pytest.raises(ValueError):
        Review.create_document(
            bathroom_id=str(ObjectId()),
            user_id=str(ObjectId()),
            cleanliness=3,
            privacy=2,
            accessibility=-1,  # Should be 1-5
            best_for="Invalid",
            comment="Invalid rating"
        )


def test_review_model_empty_comment():
    """Test that creating a Review with empty comment works."""
    # When
    review_doc = Review.create_document(
        bathroom_id=str(ObjectId()),
        user_id=str(ObjectId()),
        cleanliness=4,
        privacy=3,
        accessibility=5,
        best_for="Test case",
        comment=""  # Empty comment should be allowed
    )
    
    # Then
    assert review_doc["comment"] == ""
    assert review_doc["ratings"]["cleanliness"] == 4 