from app import db, app

def init_db():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 