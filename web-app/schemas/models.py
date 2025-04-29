"""Database models for the bathroom map application."""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pymongo import MongoClient, GEOSPHERE
from flask import current_app
import os

def init_db(app) -> None:
    """Initialize database with required indexes.
    
    Args:
        app: The Flask application instance
    """
    # Skip creating real indexes in test mode - check both config and environment
    if app.config.get('TESTING', False) or os.environ.get('TESTING') == 'true':
        return
        
    with app.app_context():
        client = MongoClient(current_app.config['MONGO_URI'])
        db = client[current_app.config['MONGO_DBNAME']]
        
        # Create geospatial index for bathroom locations
        db.bathrooms.create_index([("location", GEOSPHERE)])
        
        # Create indexes for other collections
        db.reviews.create_index("bathroom_id")
        db.users.create_index("email", unique=True)


# Typing aliases for clarity
BathroomDocument = Dict[str, Any]
ReviewDocument = Dict[str, Any]
UserDocument = Dict[str, Any]


class Bathroom:
    """Bathroom model representing a restroom location."""
    
    VALID_GENDERS = ["male", "female", "all"]
    
    @staticmethod
    def create_document(
        building: str, 
        floor: int, 
        latitude: float, 
        longitude: float,
        is_accessible: bool = False,
        gender: str = "all"
    ) -> BathroomDocument:
        """Create a new bathroom document.
        
        Args:
            building: Building name
            floor: Floor number
            latitude: Geographical latitude
            longitude: Geographical longitude
            is_accessible: Whether the bathroom is accessible
            gender: Gender designation (male, female, all)
            
        Returns:
            A bathroom document ready for database insertion
            
        Raises:
            ValueError: If floor is negative or gender is invalid
        """
        # Validate floor is positive
        if floor < 0:
            raise ValueError("Floor number must be a positive integer")
        
        # Validate gender is acceptable
        if gender not in Bathroom.VALID_GENDERS:
            raise ValueError(f"Gender must be one of: {', '.join(Bathroom.VALID_GENDERS)}")
            
        return {
            "building": building,
            "floor": floor,
            "location": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            },
            "is_accessible": is_accessible,
            "gender": gender,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }


class Review:
    """Review model for bathroom reviews."""
    
    VALID_RATING_RANGE = range(1, 6)  # 1-5 inclusive
    
    @staticmethod
    def create_document(
        bathroom_id: str,
        user_id: str,
        cleanliness: int,
        privacy: int,
        accessibility: int,
        best_for: str,
        comment: Optional[str] = None
    ) -> ReviewDocument:
        """Create a new review document.
        
        Args:
            bathroom_id: ID of the bathroom being reviewed
            user_id: ID of the user submitting the review
            cleanliness: Cleanliness rating (1-5)
            privacy: Privacy rating (1-5)
            accessibility: Accessibility rating (1-5)
            best_for: Purpose or best use case for the bathroom
            comment: Optional review comment
            
        Returns:
            A review document ready for database insertion
            
        Raises:
            ValueError: If any rating is not in the range 1-5
        """
        # Validate ratings are in the correct range
        for rating_name, rating_value in [
            ("Cleanliness", cleanliness),
            ("Privacy", privacy),
            ("Accessibility", accessibility)
        ]:
            if rating_value not in Review.VALID_RATING_RANGE:
                raise ValueError(f"{rating_name} rating must be a number between 1 and 5")
        
        return {
            "bathroom_id": bathroom_id,
            "user_id": user_id,
            "ratings": {
                "cleanliness": cleanliness,
                "privacy": privacy,
                "accessibility": accessibility
            },
            "best_for": best_for,
            "comment": comment,
            "created_at": datetime.utcnow()
        }


class User:
    """User model for application users."""
    
    @staticmethod
    def create_document(
        email: str,
        password_hash: str,
        name: str,
    ) -> UserDocument:
        """Create a new user document.
        
        Args:
            email: User's email address
            password_hash: Hashed password
            name: User's display name
            
        Returns:
            A user document ready for database insertion
        """
        return {
            "email": email,
            "password_hash": password_hash,
            "name": name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        } 
