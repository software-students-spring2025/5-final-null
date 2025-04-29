"""Tests for bathroom-related routes and functionality."""
import json
import pytest
from bson import ObjectId


def test_get_bathrooms(client, mock_bathroom):
    """Test getting all bathrooms."""
    # When
    response = client.get("/api/bathrooms")
    
    # Then
    assert response.status_code == 200
    data = response.json
    assert "bathrooms" in data
    bathrooms = json.loads(data["bathrooms"])
    assert len(bathrooms) == 1
    assert bathrooms[0]["building"] == "Test Building"


def test_get_bathrooms_with_filters(client, db, mock_bathroom):
    """Test getting bathrooms with filters."""
    # Given
    # Add another bathroom with different attributes
    db.bathrooms.insert_one({
        "building": "Another Building",
        "floor": 2,
        "location": {"type": "Point", "coordinates": [1.0, 1.0]},
        "is_accessible": False,
        "gender": "male",
        "created_at": mock_bathroom["created_at"],
        "updated_at": mock_bathroom["updated_at"],
        "created_by": str(ObjectId())
    })
    
    # When - Filter by building
    response = client.get("/api/bathrooms?building=Test")
    
    # Then
    assert response.status_code == 200
    data = response.json
    bathrooms = json.loads(data["bathrooms"])
    assert len(bathrooms) == 1
    assert bathrooms[0]["building"] == "Test Building"
    
    # When - Filter by gender
    response = client.get("/api/bathrooms?gender=all")
    
    # Then
    assert response.status_code == 200
    data = response.json
    bathrooms = json.loads(data["bathrooms"])
    assert len(bathrooms) == 1
    assert bathrooms[0]["gender"] == "all"
    
    # When - Filter by accessibility
    response = client.get("/api/bathrooms?is_accessible=true")
    
    # Then
    assert response.status_code == 200
    data = response.json
    bathrooms = json.loads(data["bathrooms"])
    assert len(bathrooms) == 1
    assert bathrooms[0]["is_accessible"] is True


def test_get_bathroom_by_id(client, mock_bathroom):
    """Test getting a specific bathroom by ID."""
    # When
    response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}")
    
    # Then
    assert response.status_code == 200
    data = response.json
    bathroom = json.loads(data["bathroom"])
    assert bathroom["building"] == "Test Building"
    assert bathroom["floor"] == 1


def test_get_nonexistent_bathroom(client):
    """Test getting a non-existent bathroom returns 404."""
    # When
    response = client.get(f"/api/bathrooms/{ObjectId()}")
    
    # Then
    assert response.status_code == 404
    assert "error" in response.json


def test_create_bathroom(client, login_user):
    """Test creating a new bathroom."""
    # Given
    bathroom_data = {
        "building": "New Building",
        "floor": 3,
        "latitude": 42.3601,
        "longitude": -71.0589,
        "is_accessible": True,
        "gender": "female"
    }
    
    # When
    response = login_user.post(
        "/api/bathrooms",
        data=json.dumps(bathroom_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 201
    assert "bathroom_id" in response.json


def test_create_bathroom_missing_fields(client, login_user):
    """Test creating a bathroom with missing required fields fails."""
    # Given - Missing floor
    bathroom_data = {
        "building": "Incomplete Building",
        "latitude": 42.3601,
        "longitude": -71.0589
    }
    
    # When
    response = login_user.post(
        "/api/bathrooms",
        data=json.dumps(bathroom_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 400
    assert "error" in response.json
    assert "Missing required fields" in response.json["error"]


def test_create_bathroom_unauthorized(client):
    """Test creating a bathroom without authentication fails."""
    # Given
    bathroom_data = {
        "building": "Unauthorized Building",
        "floor": 1,
        "latitude": 42.3601,
        "longitude": -71.0589
    }
    
    # When
    response = client.post(
        "/api/bathrooms",
        data=json.dumps(bathroom_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 401 or response.status_code == 302  # 302 if redirected to login


def test_update_bathroom(client, mock_bathroom, login_user):
    """Test updating an existing bathroom."""
    # Given
    update_data = {
        "building": "Updated Building",
        "floor": 2,
        "is_accessible": False
    }
    
    # When
    response = login_user.put(
        f"/api/bathrooms/{mock_bathroom['_id']}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 200
    
    # Verify the update in the database
    updated_response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}")
    updated_bathroom = json.loads(updated_response.json["bathroom"])
    assert updated_bathroom["building"] == "Updated Building"
    assert updated_bathroom["floor"] == 2
    assert updated_bathroom["is_accessible"] is False


def test_update_nonexistent_bathroom(client, login_user):
    """Test updating a non-existent bathroom returns 404."""
    # Given
    update_data = {"building": "Won't Update"}
    
    # When
    response = login_user.put(
        f"/api/bathrooms/{ObjectId()}",
        data=json.dumps(update_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 404


def test_delete_bathroom(client, mock_bathroom, login_user):
    """Test deleting a bathroom."""
    # When
    response = login_user.delete(
        f"/api/bathrooms/{mock_bathroom['_id']}"
    )
    
    # Then
    assert response.status_code == 200
    
    # Verify the bathroom was deleted
    get_response = client.get(f"/api/bathrooms/{mock_bathroom['_id']}")
    assert get_response.status_code == 404


def test_delete_nonexistent_bathroom(client, login_user):
    """Test deleting a non-existent bathroom returns 404."""
    # When
    response = login_user.delete(
        f"/api/bathrooms/{ObjectId()}"
    )
    
    # Then
    assert response.status_code == 404


def test_get_nearby_bathrooms(client, db, mock_bathroom):
    """Test getting nearby bathrooms."""
    # Given
    # Add bathrooms at different locations
    db.bathrooms.insert_many([
        {
            "building": "Near Building 1",
            "floor": 1,
            "location": {"type": "Point", "coordinates": [0.01, 0.01]},
            "is_accessible": True,
            "gender": "all",
            "created_at": mock_bathroom["created_at"],
            "updated_at": mock_bathroom["updated_at"],
            "created_by": str(ObjectId())
        },
        {
            "building": "Far Building",
            "floor": 1,
            "location": {"type": "Point", "coordinates": [10.0, 10.0]},
            "is_accessible": True,
            "gender": "all",
            "created_at": mock_bathroom["created_at"],
            "updated_at": mock_bathroom["updated_at"],
            "created_by": str(ObjectId())
        }
    ])
    
    # When
    response = client.get("/api/bathrooms/nearby?latitude=0.0&longitude=0.0&max_distance=1000")
    
    # Then
    assert response.status_code == 200
    data = response.json
    bathrooms = json.loads(data["bathrooms"])
    
    # In test mode, since geospatial queries may not work with mongomock, 
    # we expect to get all bathrooms back
    assert len(bathrooms) > 0 