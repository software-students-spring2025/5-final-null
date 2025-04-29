"""Tests for authentication routes and functionality."""
import json
import pytest
from flask import Flask
from werkzeug.security import check_password_hash
from bson import ObjectId


def test_register_success(client, db):
    """Test successful user registration."""
    # Given
    user_data = {
        "email": "new@example.com",
        "password": "securepassword",
        "name": "New User"
    }
    
    # When
    response = client.post(
        "/api/auth/register", 
        data=json.dumps(user_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 201
    assert "access_token" in response.json
    
    # Verify user was created in DB
    created_user = db.users.find_one({"email": "new@example.com"})
    assert created_user is not None
    assert created_user["name"] == "New User"
    assert check_password_hash(created_user["password_hash"], "securepassword")


def test_register_existing_user(client, mock_user):
    """Test registration with existing email fails."""
    # Given
    user_data = {
        "email": "test@example.com",  # Same as mock_user
        "password": "password123",
        "name": "Duplicate User"
    }
    
    # When
    response = client.post(
        "/api/auth/register", 
        data=json.dumps(user_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 400
    assert "error" in response.json
    assert "User already exists" in response.json["error"]


def test_register_missing_fields(client):
    """Test registration with missing fields fails."""
    # Given - Missing password
    user_data = {
        "email": "incomplete@example.com",
        "name": "Incomplete User"
    }
    
    # When
    response = client.post(
        "/api/auth/register", 
        data=json.dumps(user_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 400
    assert "error" in response.json
    assert "Missing required fields" in response.json["error"]


def test_login_success(client, mock_user, db):
    """Test successful login."""
    # Given
    # Update the mock user's password hash to a known value
    from werkzeug.security import generate_password_hash
    password = "correctpassword"
    db.users.update_one(
        {"_id": mock_user["_id"]},
        {"$set": {"password_hash": generate_password_hash(password)}}
    )
    
    login_data = {
        "email": "test@example.com",
        "password": password
    }
    
    # When
    response = client.post(
        "/api/auth/login", 
        data=json.dumps(login_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 200
    assert "access_token" in response.json


def test_login_invalid_credentials(client, mock_user):
    """Test login with invalid credentials fails."""
    # Given
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    # When
    response = client.post(
        "/api/auth/login", 
        data=json.dumps(login_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 401
    assert "error" in response.json
    assert "Invalid email or password" in response.json["error"]


def test_login_nonexistent_user(client):
    """Test login with non-existent user fails."""
    # Given
    login_data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    
    # When
    response = client.post(
        "/api/auth/login", 
        data=json.dumps(login_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 401
    assert "error" in response.json
    assert "Invalid email or password" in response.json["error"]


def test_get_current_user(client, mock_user, auth_headers):
    """Test getting the current user profile with valid token."""
    # When
    response = client.get(
        "/api/users/me",
        headers=auth_headers
    )
    
    # Then
    assert response.status_code == 200
    response_data = json.loads(response.json["user"])
    assert response_data["email"] == "test@example.com"
    assert "password_hash" not in response_data


def test_get_current_user_no_token(client):
    """Test getting user profile without token fails."""
    # When
    response = client.get("/api/users/me")
    
    # Then
    assert response.status_code == 401 