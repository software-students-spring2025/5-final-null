"""Database models for the application."""
from typing import Dict, List, Any, Optional
from datetime import datetime

# Typing aliases for clarity
BathroomDocument = Dict[str, Any]
ReviewDocument = Dict[str, Any]
UserDocument = Dict[str, Any]

class Bathroom:
    """Bathroom model representing a restroom location."""
    
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
        """
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
            cleanliness: Rating for cleanliness (1-5)
            privacy: Rating for privacy (1-5)
            accessibility: Rating for accessibility (1-5)
            best_for: Tag (number 1, number 2, or both)
            comment: Optional review comment
            
        Returns:
            A review document ready for database insertion
        """
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