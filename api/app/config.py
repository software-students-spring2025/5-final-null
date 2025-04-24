"""Configuration settings for the Flask application."""
import os
from typing import Dict, Any

class Config:
    """Base configuration class."""
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev_key_please_change_in_production")
    MONGO_URI: str = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DBNAME: str = os.environ.get("MONGO_DBNAME", "bathroom_map")
    DEBUG: bool = False
    TESTING: bool = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_DBNAME = "test_bathroom_map"


class ProductionConfig(Config):
    """Production configuration."""
    # Production-specific settings
    pass


# Configuration dictionary
config: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
} 