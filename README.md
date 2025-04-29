# Bathroom Map

[![Web-App CI/CD](https://github.com/software-students-spring2025/5-final-null/actions/workflows/web-app-ci.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-null/actions/workflows/web-app-ci.yml)
[![Linting](https://github.com/software-students-spring2025/5-final-null/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/software-students-spring2025/5-final-null/actions/workflows/lint.yml)

## Description

Bathroom Map is a web application that helps users find and review bathrooms in various buildings on NYU's campus. It provides information about bathroom locations, accessibility features, cleanliness ratings, and more.

## Container Images

- Web App: [DockerHub - bathroom-map-webapp](https://hub.docker.com/r/np2446/bathroom-map-webapp)
- Database: [MongoDB Official Image](https://hub.docker.com/_/mongo)

## Contributors

- [Noah Perelmuter](https://github.com/np2446)
- [Siyu Lei](https://github.com/em815)
- [Lina Sanchez](https://github.com/linahsan)
- [pinkmaggs](https://github.com/pinkmaggs)

## System Architecture

The Bathroom Map project consists of two main subsystems:

1. **Web Application (Flask)**: A Python-based web application built with Flask that provides the API endpoints and web interfaces for users to interact with the bathroom map.
2. **Database (MongoDB)**: A MongoDB database that stores information about bathrooms, user reviews, and user accounts.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Git

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/software-students-spring2025/5-final-null
   cd 5-final-null
   ```

2. Create environment variables file:
   ```bash
   cp web-app/.env.example web-app/.env
   ```

3. Edit the `.env` file with your specific configuration if needed.

4. Start the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. The application will be running at http://localhost:5001

### Environment Configuration

The application requires the following environment variables, which can be set in the `.env` file:

- `FLASK_APP`: Name of the Flask application file (default: app.py)
- `FLASK_ENV`: Environment mode (development/production)
- `MONGO_DBNAME`: Name of the MongoDB database (default: bathroom_map)
- `MONGO_URI`: MongoDB connection URI (default: mongodb://admin:secret@mongo:27017)
- `SECRET_KEY`: Secret key for Flask session encryption
- `JWT_SECRET_KEY`: Secret key for JWT token generation

Example `.env` file:
```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_PORT=5000
MONGO_DBNAME=bathroom_map
MONGO_URI=mongodb://admin:secret@mongo:27017
SECRET_KEY=development_key_change_in_production
```

### Database Initialization

The application automatically initializes the required database collections and indexes on startup. No manual steps are required.

## API Documentation

The application provides the following main API endpoints:

### Authentication

- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login a user
- `POST /api/auth/logout`: Logout a user

### Bathrooms

- `GET /api/bathrooms`: Get all bathrooms with optional filtering
- `GET /api/bathrooms/<bathroom_id>`: Get details of a specific bathroom
- `POST /api/bathrooms`: Create a new bathroom (requires authentication)
- `PUT /api/bathrooms/<bathroom_id>`: Update a bathroom (requires authentication)
- `DELETE /api/bathrooms/<bathroom_id>`: Delete a bathroom (requires authentication)
- `GET /api/bathrooms/nearby`: Find bathrooms near a specific location

### Reviews

- `GET /api/bathrooms/<bathroom_id>/reviews`: Get all reviews for a bathroom
- `POST /api/bathrooms/<bathroom_id>/reviews`: Create a new review (requires authentication)
- `GET /api/reviews/<review_id>`: Get a specific review
- `PUT /api/reviews/<review_id>`: Update a review (requires authentication)
- `DELETE /api/reviews/<review_id>`: Delete a review (requires authentication)

## Development Setup

### Local Development with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/software-students-spring2025/5-final-null
   cd 5-final-null
   ```

2. Create environment variables file:
   ```bash
   cp web-app/.env.example web-app/.env
   ```

3. Edit the `.env` file with your development configuration.

4. Build and start the containers using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```

5. The application will be running at http://localhost:5001

6. View application logs:
   ```bash
   docker-compose logs -f web-app
   ```

7. To stop the containers:
   ```bash
   docker-compose down
   ```

### Development with Local Changes

If you're actively making changes to the code and want to see changes without rebuilding:

1. Start the MongoDB container only:
   ```bash
   docker-compose up -d mongo
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   cd web-app
   pip install -r requirements.txt
   ```

4. Run the Flask application with hot reloading:
   ```bash
   FLASK_ENV=development FLASK_APP=app.py MONGO_URI=mongodb://admin:secret@localhost:27017 flask run --host=0.0.0.0 --port=5001
   ```

### Running Tests

```bash
cd web-app
pytest
```

To get coverage report:
```bash
pytest --cov=.
```

## Deployment

The application is automatically deployed to Digital Ocean when changes are pushed to the main branch. The deployment process includes:

1. Running tests
2. Building a Docker image
3. Pushing the image to Docker Hub
4. Deploying to Digital Ocean

To manually deploy:

1. Ensure you have proper access to the Digital Ocean droplet
2. SSH into the droplet
3. Pull the latest changes and restart the containers:
   ```bash
   cd ~/bathroom-map
   docker-compose pull
   docker-compose up -d
   ```

## License

[GNU General Public License v3.0](LICENSE)
