import os
from app import app, db

def reset_db():
    """Reset the database (for development only)"""
    db_path = os.path.join(os.path.dirname(__file__), 'notes.db')
    
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    with app.app_context():
        print("Creating fresh database...")
        db.create_all()
        print("Database reset complete!")

if __name__ == '__main__':
    response = input("This will delete all data! Are you sure? (y/N): ")
    if response.lower() == 'y':
        reset_db()
    else:
        print("Operation cancelled.") 