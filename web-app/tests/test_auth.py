"""Tests for authentication routes and functionality."""
import json
import pytest
from flask import Flask, session
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
    assert "user_id" in response.json
    
    # Verify user was created in DB
    created_user = db.users.find_one({"email": "new@example.com"})
    assert created_user is not None
    assert created_user["name"] == "New User"
    assert check_password_hash(created_user["password_hash"], "securepassword")
    
    # Verify login session was created
    with client.session_transaction() as sess:
        assert "_user_id" in sess


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


def test_login_success(client, mock_user):
    """Test successful login."""
    # Given
    login_data = {
        "email": "test@example.com",
        "password": "password"  # This matches the password set in the mock_user fixture
    }
    
    # When
    response = client.post(
        "/api/auth/login", 
        data=json.dumps(login_data),
        content_type="application/json"
    )
    
    # Then
    assert response.status_code == 200
    assert "user_id" in response.json
    
    # Verify login session was created
    with client.session_transaction() as sess:
        assert "_user_id" in sess


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


def test_logout(client, login_user):
    """Test logging out a user."""
    # login_user fixture has already logged in the user
    
    # Verify we're logged in
    with client.session_transaction() as sess:
        assert "_user_id" in sess
    
    # Now logout
    response = client.post("/api/auth/logout")
    
    # Verify we're logged out
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert "_user_id" not in sess


def test_get_current_user(client, login_user):
    """Test getting the current user profile."""
    # login_user fixture has already logged in the user
    
    # When
    response = client.get("/api/users/me")
    
    # Then
    assert response.status_code == 200
    response_data = json.loads(response.json["user"])
    assert response_data["email"] == "test@example.com"
    assert "password_hash" not in response_data


def test_get_current_user_not_logged_in(client):
    """Test getting user profile without being logged in fails."""
    # When
    response = client.get("/api/users/me")
    
    # Then
    assert response.status_code == 401 or response.status_code == 302  # 302 if redirected to login 