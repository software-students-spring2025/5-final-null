"""Seed script to populate the database with initial NYU campus bathroom data."""
from schemas import Bathroom
from pymongo.errors import PyMongoError

def seed_bathrooms(db):
    """Seed the database with NYU campus bathrooms.
    
    Args:
        db: MongoDB database instance
    """
    # Check if bathrooms already exist
    if db.bathrooms.count_documents({}) > 0:
        print("Database already contains bathrooms. Skipping seed.")
        return
    
    # Define NYU campus bathroom data
    nyu_bathrooms = [
        {
            "building": "Kimmel Center",
            "floor": 2,
            "latitude": 40.7294,
            "longitude": -73.9972,
            "is_accessible": True,
            "gender": "all"
        },
        {
            "building": "Bobst Library",
            "floor": 1,
            "latitude": 40.7295,
            "longitude": -73.9975,
            "is_accessible": True,
            "gender": "all"
        },
        {
            "building": "Warren Weaver Hall",
            "floor": 3,
            "latitude": 40.7287,
            "longitude": -73.9958,
            "is_accessible": False,
            "gender": "male"
        },
        {
            "building": "Warren Weaver Hall",
            "floor": 3,
            "latitude": 40.7287,
            "longitude": -73.9958,
            "is_accessible": False,
            "gender": "female"
        },
        {
            "building": "Silver Center",
            "floor": 1,
            "latitude": 40.7308,
            "longitude": -73.9954,
            "is_accessible": True,
            "gender": "all"
        },
        {
            "building": "Tisch Hall",
            "floor": 2,
            "latitude": 40.7291,
            "longitude": -73.9954,
            "is_accessible": True,
            "gender": "all"
        },
        {
            "building": "Courant Institute",
            "floor": 4,
            "latitude": 40.7287,
            "longitude": -73.9958,
            "is_accessible": False,
            "gender": "male"
        },
        {
            "building": "Courant Institute",
            "floor": 4,
            "latitude": 40.7287,
            "longitude": -73.9958,
            "is_accessible": False,
            "gender": "female"
        },
        {
            "building": "Stern School of Business",
            "floor": 1,
            "latitude": 40.7291,
            "longitude": -73.9984,
            "is_accessible": True,
            "gender": "all"
        },
        {
            "building": "Palladium Hall",
            "floor": 2,
            "latitude": 40.7327,
            "longitude": -73.9921,
            "is_accessible": True,
            "gender": "all"
        }
    ]
    
    # Create bathroom documents and insert into database
    bathroom_documents = []
    for bathroom_data in nyu_bathrooms:
        try:
            bathroom_doc = Bathroom.create_document(
                building=bathroom_data["building"],
                floor=bathroom_data["floor"],
                latitude=bathroom_data["latitude"],
                longitude=bathroom_data["longitude"],
                is_accessible=bathroom_data["is_accessible"],
                gender=bathroom_data["gender"]
            )
            bathroom_documents.append(bathroom_doc)
        except Exception as e:
            print(f"Error creating bathroom document: {e}")
    
    # Insert bathrooms into the database
    if bathroom_documents:
        try:
            db.bathrooms.insert_many(bathroom_documents)
            print(f"Successfully seeded {len(bathroom_documents)} bathrooms into the database.")
        except PyMongoError as e:
            print(f"Error seeding bathrooms: {e}") 