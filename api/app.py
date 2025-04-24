from flask import Flask
from app.config import DevelopmentConfig
from app.routes import register_routes

def create_app(config_class=DevelopmentConfig):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register routes
    register_routes(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000) 