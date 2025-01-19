from app import app, db
import os

def migrate_db():
    # Delete the existing database file
    db_path = os.path.join(os.path.dirname(__file__), 'notes.db')
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    with app.app_context():
        print("Creating new database with updated schema...")
        db.create_all()
        print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate_db() 