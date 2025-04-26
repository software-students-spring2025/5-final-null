"""Database connection module for the bathroom map application."""
from typing import Dict, Any
from flask import Flask, current_app, g
from pymongo import MongoClient
from pymongo.database import Database

def get_db() -> Database:
    """Get the MongoDB database connection.
    
    Returns:
        The MongoDB database instance
    """
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client[current_app.config['MONGO_DBNAME']]
    return g.db

def close_db(e=None) -> None:
    """Close the MongoDB connection when the application context ends.
    
    Args:
        e: Optional exception that caused the context to end
    """
    db_client = g.pop('db_client', None)
    if db_client is not None:
        db_client.close()

def init_app(app: Flask) -> None:
    """Initialize the database connection for the Flask application.
    
    Args:
        app: The Flask application instance
    """
    app.teardown_appcontext(close_db)
    
    # Create collection helpers
    @app.context_processor
    def utility_processor() -> Dict[str, Any]:
        """Add collection helper functions to template context."""
        return {
            'bathrooms': lambda: get_db().bathrooms,
            'reviews': lambda: get_db().reviews,
            'users': lambda: get_db().users
        } 