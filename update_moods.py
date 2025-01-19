from app import app, db, Note

def update_existing_notes_mood():
    with app.app_context():
        notes = Note.query.all()
        for note in notes:
            note.analyze_mood()
        db.session.commit()

if __name__ == '__main__':
    update_existing_notes_mood()
    print("Updated mood scores for all existing notes") 