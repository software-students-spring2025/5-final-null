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


def test_get_reviews_nonexistent_bathroom(client):
    """Test getting reviews for a non-existent bathroom returns 404."""
    # When
    response = client.get(f"/api/bathrooms/{ObjectId()}/reviews")
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_create_review(client, mock_bathroom, auth_headers):
    """Test creating a new review."""
    # Given
    review_data = {
        "cleanliness": 5,
        "privacy": 4,
        "accessibility": 3,
        "best_for": "number 2",
        "comment": "Great bathroom!"
    }
    
    # When
    response = client.post(
        f"/api/bathrooms/{mock_bathroom['_id']}/reviews",
        data=json.dumps(review_data),
        content_type="application/json",
        headers=auth_headers
    )
    
    # Then
    assert response.status_code == 201
    assert "review_id" in response.json
    
    # Check review was created
    bathroom_response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}/reviews")
    reviews = json.loads(bathroom_response.json["reviews"])
    new_review = [r for r in reviews if r["comment"] == "Great bathroom!"]
    assert len(new_review) == 1
    assert new_review[0]["ratings"]["cleanliness"] == 5


def test_create_review_nonexistent_bathroom(client, auth_headers):
    """Test creating a review for a non-existent bathroom fails."""
    # Given
    review_data = {
        "cleanliness": 5,
        "privacy": 4,
        "accessibility": 3,
        "best_for": "number 2",
        "comment": "Won't be created"
    }
    
    # When
    response = client.post(
        f"/api/bathrooms/{ObjectId()}/reviews",
        data=json.dumps(review_data),
        content_type="application/json",
        headers=auth_headers
    )
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_create_review_invalid_rating(client, mock_bathroom, auth_headers):
    """Test creating a review with invalid rating fails."""
    # Given - Rating out of range
    review_data = {
        "cleanliness": 6,  # Should be 1-5
        "privacy": 4,
        "accessibility": 3,
        "best_for": "number 2",
        "comment": "Invalid rating"
    }
    
    # When
    response = client.post(
        f"/api/bathrooms/{mock_bathroom['_id']}/reviews",
        data=json.dumps(review_data),
        content_type="application/json",
        headers=auth_headers
    )
    
    # Then
    assert response.status_code == 400
    assert "error" in response.json
    assert "rating" in response.json["error"]


def test_create_review_unauthorized(client, mock_bathroom):
    """Test creating a review without authentication fails."""
    # Given
    review_data = {
        "cleanliness": 5,
        "privacy": 4,
        "accessibility": 3,
        "best_for": "number 2",
        "comment": "Unauthorized review"
    }
    
    # When
    response = client.post(
        f"/api/bathrooms/{mock_bathroom['_id']}/reviews",
        data=json.dumps(review_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 401


def test_update_review(client, mock_review, auth_headers):
    """Test updating an existing review."""
    # Given
    update_data = {
        "cleanliness": 2,
        "privacy": 3,
        "accessibility": 4,
        "best_for": "both",
        "comment": "Updated review comment"
    }
    
    # When
    response = client.put(
        f"/api/reviews/{mock_review['_id']}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=auth_headers
    )
    
    # Then
    assert response.status_code == 200
    
    # Verify the update
    bathroom_response = client.get(f"/api/bathrooms/{mock_review['bathroom_id']}/reviews")
    reviews = json.loads(bathroom_response.json["reviews"])
    updated_review = reviews[0]
    assert updated_review["comment"] == "Updated review comment"
    assert updated_review["ratings"]["cleanliness"] == 2


def test_update_nonexistent_review(client, auth_headers):
    """Test updating a non-existent review returns 404."""
    # Given
    update_data = {
        "cleanliness": 3,
        "privacy": 3,
        "accessibility": 3,
        "best_for": "number 1",
        "comment": "Won't update"
    }
    
    # When
    response = client.put(
        f"/api/reviews/{ObjectId()}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=auth_headers
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
        "best_for": "number 1",
        "comment": "Unauthorized update"
    }
    
    # When
    response = client.put(
        f"/api/reviews/{mock_review['_id']}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 401


def test_delete_review(client, mock_review, auth_headers, mock_bathroom):
    """Test deleting a review."""
    # When
    response = client.delete(
        f"/api/reviews/{mock_review['_id']}",
        headers=auth_headers
    )
    
    # Then
    assert response.status_code == 200
    
    # Verify the review was deleted
    bathroom_response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}/reviews")
    reviews = json.loads(bathroom_response.json["reviews"])
    assert len(reviews) == 0


def test_delete_nonexistent_review(client, auth_headers):
    """Test deleting a non-existent review returns 404."""
    # When
    response = client.delete(
        f"/api/reviews/{ObjectId()}",
        headers=auth_headers
    )
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_delete_review_unauthorized(client, mock_review):
    """Test deleting a review without authentication fails."""
    # When
    response = client.delete(
        f"/api/reviews/{mock_review['_id']}"
    )
    
    # Then
    assert response.status_code == 401 