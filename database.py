import os
from sqlalchemy import inspect
from datetime import datetime, UTC
from textblob import TextBlob
from collections import Counter
import json
from flask_sqlalchemy import SQLAlchemy
import spacy
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db = SQLAlchemy()
nlp = spacy.load('en_core_web_sm')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
    summary = db.Column(db.Text, nullable=True)

    def __init__(self, **kwargs):
        super(Note, self).__init__(**kwargs)
        if 'journal_date' not in kwargs:
            self.journal_date = datetime.now(UTC).date()
        if 'created_at' not in kwargs:
            self.created_at = datetime.now(UTC)
        if 'updated_at' not in kwargs:
            self.updated_at = datetime.now(UTC)

    def analyze_content(self):
        try:
            # Analyze mood
            blob = TextBlob(self.content)
            self.mood_score = blob.sentiment.polarity

            # Extract names using spaCy
            doc = nlp(self.content)
            names = [ent.text.strip().title() for ent in doc.ents if ent.label_ == 'PERSON' and len(ent.text.strip()) > 1]
            
            if names:
                # Use OpenAI to analyze relationships
                try:
                    prompt = f"""Analyze the relationships of people mentioned in this journal entry.

                    Journal entry:
                    {self.content}

                    People mentioned: {', '.join(names)}

                    For each person mentioned, determine their relationship category and explain why.
                    Categories: work, family, romantic, friends, other

                    Respond in this exact JSON format:
                    {{
                        "relationships": {{
                            "work": {{"person1": "count"}},
                            "family": {{"person2": "count"}},
                            "romantic": {{"person3": "count"}},
                            "friends": {{"person4": "count"}},
                            "other": {{"person5": "count"}}
                        }}
                    }}

                    Only include people where the relationship is clear from the context."""

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo-1106",  # Using the latest model
                        messages=[
                            {"role": "system", "content": "You are an expert at analyzing relationships in text. Be precise and only categorize relationships when there's clear contextual evidence."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"},  # Ensure JSON response
                        max_tokens=500,
                        temperature=0.3
                    )

                    relationships_data = json.loads(response.choices[0].message.content)
                    
                    # Convert the AI analysis to our Counter format
                    relationships = {
                        'work': Counter(),
                        'friends': Counter(),
                        'family': Counter(),
                        'romantic': Counter(),
                        'other': Counter()
                    }

                    for category, people in relationships_data['relationships'].items():
                        for name, count in people.items():
                            try:
                                count_num = int(count)
                                relationships[category][name] = count_num
                            except (ValueError, TypeError):
                                relationships[category][name] = 1

                    # Store the data
                    self.names = json.dumps(dict(Counter(names)))
                    self.relationships = json.dumps({cat: dict(counts) for cat, counts in relationships.items() if counts})

                except Exception as e:
                    print(f"OpenAI relationship analysis failed: {e}")
                    # Fall back to basic name counting if AI analysis fails
                    self.names = json.dumps(dict(Counter(names)))
                    self.relationships = json.dumps({'other': dict(Counter(names))})
            else:
                self.names = None
                self.relationships = None

        except Exception as e:
            print(f"Content analysis failed: {e}")
            self.mood_score = 0
            self.names = None
            self.relationships = None

    def generate_summary(self):
        """Generate summary using OpenAI after the note is saved"""
        try:
            # Create a more focused prompt for better summaries
            prompt = f"""Analyze this journal entry and provide a concise summary focusing on:
1. Main events or activities
2. Key emotions and feelings
3. Important interactions with people
4. Any decisions or realizations made

Journal entry:
{self.content}

Provide a natural, cohesive summary that captures these elements."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a thoughtful journal analyst who provides clear, insightful summaries of personal journal entries. Focus on emotional context and key events."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            self.summary = response.choices[0].message.content
            return True
        except Exception as e:
            print(f"OpenAI analysis failed: {e}")
            self.summary = None
            return False

    def get_mood_emoji(self):
        if self.mood_score is None:
            return "😐"
        if self.mood_score >= 0.5:
            return "😄"  # Very Positive
        if self.mood_score >= 0.1:
            return "🙂"  # Positive
        if self.mood_score >= -0.1:
            return "😐"  # Neutral
        if self.mood_score >= -0.5:
            return "🙁"  # Negative
        return "😢"      # Very Negative

    def to_dict(self):
        try:
            return {
                'id': self.id,
                'title': self.title or '',
                'content': self.content or '',
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'mood_score': self.mood_score if self.mood_score is not None else 0,
                'mood_emoji': self.get_mood_emoji(),
                'journal_date': self.journal_date.isoformat() if self.journal_date else None,
                'highlight': self.get_highlight() or '',
                'summary': self.summary or ''
            }
        except Exception as e:
            print(f"Error converting note to dict: {e}")
            return {
                'id': self.id,
                'title': '',
                'content': '',
                'created_at': None,
                'updated_at': None,
                'mood_score': 0,
                'mood_emoji': '😐',
                'journal_date': None,
                'highlight': '',
                'summary': ''
            }

    def get_highlight(self):
        sentences = [sent.text.strip() for sent in nlp(self.content).sents]
        if not sentences:
            return ""
        return max(sentences, key=len) if len(sentences) == 1 else sentences[1]

    @property
    def relationships_dict(self):
        """Return the relationships dictionary with proper error handling"""
        if not self.relationships:
            return {}
        try:
            return json.loads(self.relationships)
        except (json.JSONDecodeError, TypeError):
            return {}

def init_db(app):
    """Initialize the database"""
    db.init_app(app)
    
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('note'):
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
        else:
            print("Database tables already exist.") 