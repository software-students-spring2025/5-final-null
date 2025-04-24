"""Route definitions for the Flask application."""
from typing import Dict, Any
from flask import Flask, jsonify, request

def register_routes(app: Flask) -> None:
    """Register all routes with the Flask application.
    
    Args:
        app: The Flask application instance
    """
    
    @app.route('/api/health', methods=['GET'])
    def health_check() -> Dict[str, str]:
        """Health check endpoint.
        
        Returns:
            A JSON response indicating the service is healthy
        """
        return jsonify({"status": "healthy"})
    
    @app.route('/api/bathrooms', methods=['GET'])
    def get_bathrooms() -> Dict[str, Any]:
        """Get all bathrooms.
        
        Returns:
            A JSON response with all bathrooms
        """
        # Placeholder - would actually query MongoDB
        bathrooms = [
            {"id": "1", "building": "Kimmel", "floor": 2, "lat": 40.729553, "lng": -73.997330},
            {"id": "2", "building": "Bobst", "floor": 4, "lat": 40.729879, "lng": -73.997101}
        ]
        return jsonify({"bathrooms": bathrooms}) 