import os
from app import app, db

def setup_db():
    """Setup the database with all tables"""
    db_path = os.path.join(os.path.dirname(__file__), 'notes.db')
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    # Create fresh database with all tables
    with app.app_context():
        print("Creating fresh database...")
        db.create_all()
        print("Database setup complete!")

if __name__ == '__main__':
    setup_db() 