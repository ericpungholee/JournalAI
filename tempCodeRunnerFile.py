from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, UTC
from textblob import TextBlob
import os
import spacy
from collections import Counter
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
nlp = spacy.load('en_core_web_sm')

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

    # ... rest of your Note class methods ...

# Create tables
with app.app_context():
    db.create_all()

# ... rest of your routes ...

if __name__ == '__main__':
    app.run(debug=True) 