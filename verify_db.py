from database import verify_db_structure, DB_PATH
import os

def check_database():
    if not os.path.exists(DB_PATH):
        print(f"Database does not exist at {DB_PATH}")
        return False
    
    if verify_db_structure():
        print("Database structure is correct!")
        return True
    else:
        print("Database structure is incorrect!")
        return False

if __name__ == '__main__':
    check_database() 