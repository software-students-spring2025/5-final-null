"""Tests for review-related routes and functionality."""
import json
import pytest
from bson import ObjectId


def test_get_reviews(client, mock_bathroom, mock_review):
    """Test getting all reviews for a bathroom."""
    # When
    response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}/reviews")
    
    # Then
    assert response.status_code == 200
    data = response.json
    assert "reviews" in data
    reviews = json.loads(data["reviews"])
    assert len(reviews) == 1
    assert reviews[0]["comment"] == "Test review comment"
    assert reviews[0]["ratings"]["cleanliness"] == 4
    assert reviews[0]["ratings"]["privacy"] == 3
    assert reviews[0]["ratings"]["accessibility"] == 4
    assert reviews[0]["best_for"] == "Quick stop"


def test_get_reviews_nonexistent_bathroom(client):
    """Test getting reviews for a non-existent bathroom returns 404."""
    # When
    response = client.get(f"/api/bathrooms/{ObjectId()}/reviews")
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_get_review(client, mock_review):
    """Test getting a specific review by ID."""
    # When
    response = client.get(f"/api/reviews/{mock_review['_id']}")
    
    # Then
    assert response.status_code == 200
    data = response.json
    assert "review" in data
    review = json.loads(data["review"])
    assert review["comment"] == "Test review comment"
    assert review["ratings"]["cleanliness"] == 4
    assert review["ratings"]["privacy"] == 3
    assert review["ratings"]["accessibility"] == 4
    assert review["best_for"] == "Quick stop"


def test_get_nonexistent_review(client):
    """Test getting a non-existent review returns 404."""
    # When
    response = client.get(f"/api/reviews/{ObjectId()}")
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_create_review(client, mock_bathroom, login_user):
    """Test creating a new review."""
    # Given
    review_data = {
        "cleanliness": 5,
        "privacy": 4,
        "accessibility": 3,
        "best_for": "Emergency",
        "comment": "Great bathroom!"
    }
    
    # When
    response = login_user.post(
        f"/api/bathrooms/{mock_bathroom['_id']}/reviews",
        data=json.dumps(review_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 201
    assert "review" in response.json
    
    # Check review was created
    bathroom_response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}/reviews")
    reviews = json.loads(bathroom_response.json["reviews"])
    new_review = [r for r in reviews if r["comment"] == "Great bathroom!"]
    assert len(new_review) == 1
    assert new_review[0]["ratings"]["cleanliness"] == 5
    assert new_review[0]["ratings"]["privacy"] == 4
    assert new_review[0]["ratings"]["accessibility"] == 3
    assert new_review[0]["best_for"] == "Emergency"


def test_create_review_nonexistent_bathroom(client, login_user):
    """Test creating a review for a non-existent bathroom fails."""
    # Given
    review_data = {
        "cleanliness": 5,
        "privacy": 4,
        "accessibility": 3,
        "best_for": "Emergency",
        "comment": "Won't be created"
    }
    
    # When
    response = login_user.post(
        f"/api/bathrooms/{ObjectId()}/reviews",
        data=json.dumps(review_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_create_review_invalid_rating(client, mock_bathroom, login_user):
    """Test creating a review with invalid rating fails."""
    # Given - Rating out of range
    review_data = {
        "cleanliness": 6,  # Should be 1-5
        "privacy": 4,
        "accessibility": 3,
        "best_for": "Emergency",
        "comment": "Invalid rating"
    }
    
    # When
    response = login_user.post(
        f"/api/bathrooms/{mock_bathroom['_id']}/reviews",
        data=json.dumps(review_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 400
    assert "error" in response.json
    assert "Cleanliness" in response.json["error"]


def test_create_review_unauthorized(client, mock_bathroom):
    """Test creating a review without authentication fails."""
    # Given
    review_data = {
        "cleanliness": 5,
        "privacy": 4,
        "accessibility": 3,
        "best_for": "Emergency",
        "comment": "Unauthorized review"
    }
    
    # When
    response = client.post(
        f"/api/bathrooms/{mock_bathroom['_id']}/reviews",
        data=json.dumps(review_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 401 or response.status_code == 302  # 302 if redirected to login


def test_update_review(client, mock_review, login_user, mock_user, setup_db):
    """Test updating an existing review."""
    # Given - Update mock_review to set user_id to the logged in user
    setup_db.reviews.update_one(
        {"_id": mock_review["_id"]},
        {"$set": {"user_id": str(mock_user["_id"])}}
    )
    
    update_data = {
        "cleanliness": 2,
        "privacy": 3,
        "accessibility": 1,
        "best_for": "Not recommended",
        "comment": "Updated review comment"
    }
    
    # When
    response = login_user.put(
        f"/api/reviews/{mock_review['_id']}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 200
    
    # Verify the update
    bathroom_response = client.get(f"/api/bathrooms/{mock_review['bathroom_id']}/reviews")
    reviews = json.loads(bathroom_response.json["reviews"])
    updated_review = reviews[0]
    assert updated_review["comment"] == "Updated review comment"
    assert updated_review["ratings"]["cleanliness"] == 2
    assert updated_review["ratings"]["privacy"] == 3
    assert updated_review["ratings"]["accessibility"] == 1
    assert updated_review["best_for"] == "Not recommended"


def test_update_nonexistent_review(client, login_user):
    """Test updating a non-existent review returns 404."""
    # Given
    update_data = {
        "cleanliness": 3,
        "privacy": 3,
        "accessibility": 3,
        "best_for": "Average",
        "comment": "Won't update"
    }
    
    # When
    response = login_user.put(
        f"/api/reviews/{ObjectId()}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_update_review_unauthorized(client, mock_review):
    """Test updating a review without authentication fails."""
    # Given
    update_data = {
        "cleanliness": 3,
        "privacy": 3,
        "accessibility": 3,
        "best_for": "Average",
        "comment": "Unauthorized update"
    }
    
    # When
    response = client.put(
        f"/api/reviews/{mock_review['_id']}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 401 or response.status_code == 302  # 302 if redirected to login


def test_update_review_wrong_user(client, mock_review, login_user, setup_db):
    """Test updating a review belonging to another user fails."""
    # Given - Ensure the review belongs to a different user
    setup_db.reviews.update_one(
        {"_id": mock_review["_id"]},
        {"$set": {"user_id": str(ObjectId())}}  # Random user ID
    )
    
    update_data = {
        "cleanliness": 3,
        "privacy": 3,
        "accessibility": 3,
        "best_for": "Average",
        "comment": "Can't update another user's review"
    }
    
    # When
    response = login_user.put(
        f"/api/reviews/{mock_review['_id']}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 403
    assert "error" in response.json


def test_delete_review(client, mock_review, login_user, mock_bathroom, mock_user, setup_db):
    """Test deleting a review."""
    # Given - Update mock_review to set user_id to the logged in user
    setup_db.reviews.update_one(
        {"_id": mock_review["_id"]},
        {"$set": {"user_id": str(mock_user["_id"])}}
    )
    
    # When
    response = login_user.delete(f"/api/reviews/{mock_review['_id']}")
    
    # Then
    assert response.status_code == 200
    
    # Verify the review was deleted
    bathroom_response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}/reviews")
    reviews = json.loads(bathroom_response.json["reviews"])
    assert len(reviews) == 0


def test_delete_nonexistent_review(client, login_user):
    """Test deleting a non-existent review returns 404."""
    # When
    response = login_user.delete(f"/api/reviews/{ObjectId()}")
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_delete_review_unauthorized(client, mock_review):
    """Test deleting a review without authentication fails."""
    # When
    response = client.delete(f"/api/reviews/{mock_review['_id']}")
    
    # Then
    assert response.status_code == 401 or response.status_code == 302  # 302 if redirected to login


def test_delete_review_wrong_user(client, mock_review, login_user, setup_db):
    """Test deleting a review belonging to another user fails."""
    # Given - Ensure the review belongs to a different user
    setup_db.reviews.update_one(
        {"_id": mock_review["_id"]},
        {"$set": {"user_id": str(ObjectId())}}  # Random user ID
    )
    
    # When
    response = login_user.delete(f"/api/reviews/{mock_review['_id']}")
    
    # Then
    assert response.status_code == 403
    assert "error" in response.json 