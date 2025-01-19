from datetime import datetime, UTC
from textblob import TextBlob
from collections import Counter
import json
from extensions import db, nlp

class Note(db.Model):
    __tablename__ = 'note'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True, default='')
    content = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    mood_score = db.Column(db.Float, nullable=True)
    journal_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(UTC).date())
    names = db.Column(db.Text, nullable=True)
    relationships = db.Column(db.Text, nullable=True)

    def __init__(self, **kwargs):
        super(Note, self).__init__(**kwargs)
        if 'journal_date' not in kwargs:
            self.journal_date = datetime.now(UTC).date()
        if 'created_at' not in kwargs:
            self.created_at = datetime.now(UTC)
        if 'updated_at' not in kwargs:
            self.updated_at = datetime.now(UTC)

    # Copy all other methods from the original Note class 