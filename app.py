from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta, UTC
import os
import spacy
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from database import db, Note, init_db
from collections import Counter
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
init_db(app)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
nlp = spacy.load('en_core_web_sm')

# Routes start here
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/insights')
def insights():
    try:
        # Get some basic stats about notes
        notes = Note.query.all()
        total_notes = len(notes)
        latest_note = Note.query.order_by(Note.updated_at.desc()).first()
        total_characters = sum(len(note.content) for note in notes)
        
        # Handle case when there are no notes
        if total_notes == 0:
            return render_template('insights.html', stats={
                'total_notes': 0,
                'latest_update': None,
                'total_characters': 0,
                'weekly_summary': {
                    'total_entries': 0,
                    'message': 'Start writing your first journal entry!'
                },
                'relationships': {}
            })

        # Get notes from the last 7 days, but limit to 7 most recent entries
        today = datetime.now(UTC).date()
        week_ago = today - timedelta(days=7)
        this_week_notes = Note.query.filter(
            Note.journal_date >= week_ago,
            Note.journal_date <= today
        ).order_by(Note.journal_date.desc()).limit(7).all()  # Limit to 7 entries

        # Calculate weekly stats
        if this_week_notes:
            if len(this_week_notes) > 7:
                this_week_notes = this_week_notes[:7]  # Extra safety check
                
            # Prepare all weekly content for OpenAI analysis
            weekly_content = "\n\n---\n\n".join([
                f"Date: {note.journal_date.strftime('%A, %B %d')}\n"
                f"Title: {note.title}\n"
                f"Content: {note.content}"
                for note in this_week_notes
            ])

            try:
                # Get comprehensive weekly analysis from OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "system", "content": """You are an insightful journal analyst who provides 
                        comprehensive analysis of journal entries. Focus on patterns, emotional trends, 
                        key events, and personal growth."""},
                        {"role": "user", "content": f"""Analyze these journal entries from the past week and provide a detailed analysis.
                        Focus on:
                        1. Overall mood and emotional trends
                        2. Key achievements and successes (both big and small)
                        3. Main challenges faced
                        4. Important people mentioned and their roles
                        5. Recurring themes or patterns
                        6. Notable activities or events
                        7. Personal growth or insights gained
                        8. Recommendations for next week based on patterns and challenges

                        Journal entries:
                        {weekly_content}

                        Respond in this exact JSON format:
                        {{
                            "mood_analysis": {{
                                "overall_trend": "improved/declined/stable",
                                "description": "Brief description of emotional state"
                            }},
                            "achievements": [
                                "achievement1",
                                "achievement2",
                                "achievement3"
                            ],
                            "challenges": [
                                "challenge1",
                                "challenge2",
                                "challenge3"
                            ],
                            "key_people": [
                                {{"name": "Name1", "role": "Role/Relationship", "impact": "Their impact"}},
                                {{"name": "Name2", "role": "Role/Relationship", "impact": "Their impact"}}
                            ],
                            "themes": [
                                "theme1",
                                "theme2"
                            ],
                            "activities": [
                                "activity1",
                                "activity2"
                            ],
                            "insights": [
                                "insight1",
                                "insight2"
                            ],
                            "recommendations": [
                                "Specific action or focus area for next week based on the analysis",
                                "Another recommendation that could help with observed challenges",
                                "Suggestion to build on positive patterns or achievements"
                            ],
                            "summary": "A cohesive summary paragraph of the week"
                        }}"""}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=1000,
                    temperature=0.7
                )
                
                analysis = json.loads(response.choices[0].message.content)
                
                # Calculate basic stats
                start_date = min(note.journal_date for note in this_week_notes)
                end_date = max(note.journal_date for note in this_week_notes)
                date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
                
                # Calculate mood stats
                mood_scores = [note.mood_score for note in this_week_notes if note.mood_score is not None]
                avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
                
                # Get best and worst days
                valid_mood_notes = [note for note in this_week_notes if note.mood_score is not None]
                if valid_mood_notes:
                    best_day = max(valid_mood_notes, key=lambda x: x.mood_score)
                    worst_day = min(valid_mood_notes, key=lambda x: x.mood_score)
                else:
                    best_day = worst_day = this_week_notes[0]
                
                weekly_summary = {
                    'date_range': date_range,
                    'total_entries': len(this_week_notes),
                    'avg_mood': avg_mood,
                    'mood_trend': analysis['mood_analysis']['overall_trend'],
                    'best_day': {
                        'date': best_day.journal_date.strftime('%A, %B %d'),
                        'mood': best_day.mood_score or 0,
                        'title': best_day.title or 'Untitled'
                    },
                    'worst_day': {
                        'date': worst_day.journal_date.strftime('%A, %B %d'),
                        'mood': worst_day.mood_score or 0,
                        'title': worst_day.title or 'Untitled'
                    },
                    'mood_analysis': analysis['mood_analysis'],
                    'top_achievements': analysis['achievements'],
                    'top_challenges': analysis['challenges'],
                    'key_people': analysis['key_people'],
                    'themes': analysis['themes'],
                    'activities': analysis['activities'],
                    'insights': analysis['insights'],
                    'recommendations': analysis['recommendations'],
                    'summary': analysis['summary']
                }
            except Exception as e:
                print(f"Error in OpenAI analysis: {e}")
                weekly_summary = {
                    'total_entries': len(this_week_notes),
                    'message': "Error generating weekly analysis"
                }
        else:
            weekly_summary = {
                'total_entries': 0,
                'message': "No entries this week",
                'avg_mood': 0,
                'mood_trend': 'stable',
                'best_day': None,
                'worst_day': None
            }

        # Get relationship stats (keep existing relationship analysis)
        all_relationships = {
            'work': Counter(),
            'friends': Counter(),
            'family': Counter(),
            'romantic': Counter(),
            'other': Counter()
        }
        
        for note in notes:
            rel_dict = note.relationships_dict
            for category, names in rel_dict.items():
                for name, count in names.items():
                    if name.strip():
                        all_relationships[category][name] += count

        relationship_stats = {
            category: {
                'names': dict(counter.most_common(3)),
                'total': sum(counter.values()),
                'color': {
                    'work': '#3498db',
                    'friends': '#2ecc71',
                    'family': '#e74c3c',
                    'romantic': '#e84393',
                    'other': '#95a5a6'
                }[category]
            }
            for category, counter in all_relationships.items()
            if counter
        }

        stats = {
            'total_notes': total_notes,
            'latest_update': latest_note.updated_at if latest_note else None,
            'total_characters': total_characters,
            'weekly_summary': weekly_summary,
            'relationships': relationship_stats
        }
        
        return render_template('insights.html', stats=stats)
    except Exception as e:
        print(f"Error in insights route: {e}")
        return render_template('insights.html', stats={
            'total_notes': 0,
            'latest_update': None,
            'total_characters': 0,
            'weekly_summary': {
                'total_entries': 0,
                'message': 'Error loading insights',
                'top_achievements': ["Error loading achievements"],
                'top_challenges': ["Error loading challenges"]
            },
            'relationships': {}
        })

@app.route('/insights/mood-data')
def get_mood_data():
    # Get only the last 7 entries for mood data
    notes = Note.query.order_by(Note.journal_date.desc()).limit(7).all()
    notes = sorted(notes, key=lambda x: x.journal_date)  # Sort by date ascending for the graph
    return jsonify([{
        'id': note.id,
        'date': note.journal_date.isoformat(),
        'mood': note.mood_score,
        'mood_emoji': note.get_mood_emoji(),
        'title': note.title,
        'highlight': note.get_highlight()
    } for note in notes])

@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        notes = Note.query.order_by(Note.updated_at.desc()).all()
        return jsonify([note.to_dict() for note in notes])
    except Exception as e:
        print(f"Error loading notes: {e}")
        return jsonify({'message': 'Failed to load notes'}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        return jsonify(note.to_dict())
    except Exception as e:
        print(f"Error loading note {note_id}: {e}")
        return jsonify({'message': 'Failed to load note'}), 500

@app.route('/api/notes', methods=['POST'])
def create_note():
    try:
        if not request.is_json:
            return jsonify({'message': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        content = data.get('content', '').strip()
        if not content:
            return jsonify({'message': 'Content cannot be empty'}), 400

        try:
            journal_date = datetime.strptime(data.get('journal_date', ''), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            journal_date = datetime.now(UTC).date()
            
        note = Note(
            title=data.get('title', '').strip(),
            content=content,
            journal_date=journal_date
        )
        
        # First do basic analysis
        try:
            note.analyze_content()
        except Exception as e:
            print(f"Error analyzing content: {e}")
            note.mood_score = 0
            note.names = None
            note.relationships = None
        
        # Save the note first
        db.session.add(note)
        db.session.commit()
        
        # Then generate and save the summary
        try:
            if note.generate_summary():
                db.session.commit()  # Save the summary if generated successfully
                print("Summary generated successfully")
            else:
                print("Failed to generate summary")
        except Exception as e:
            print(f"Error generating summary: {e}")
            # Continue even if summary generation fails
        
        return jsonify(note.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating note: {e}")
        return jsonify({'message': 'An error occurred while saving the note'}), 500

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']
            note.analyze_content()
            # Generate new summary if content changed
            try:
                note.generate_summary()
            except Exception as e:
                print(f"Error generating summary during update: {e}")
        if 'journal_date' in data:
            try:
                note.journal_date = datetime.strptime(data['journal_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Invalid date format'}), 400
        
        db.session.commit()
        return jsonify(note.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/one-year-ago')
def one_year_ago():
    try:
        # Get today's date and calculate the date 1 year ago
        today = datetime.now(UTC).date()
        one_year_ago = today.replace(year=today.year - 1)
        
        # Find both entries
        old_note = Note.query.filter_by(journal_date=one_year_ago).first()
        today_note = Note.query.filter_by(journal_date=today).first()
        
        if not old_note:
            return render_template('one_year_ago.html', data={
                'has_entry': False,
                'message': f'No journal entry found for {one_year_ago.strftime("%B %d, %Y")}'
            })

        # Generate comparison if we have both entries
        comparison = None
        if today_note:
            try:
                comparison_prompt = f"""Compare these two journal entries from the same day, one year apart.
                Focus on:
                1. Changes in emotional state and perspective
                2. Life changes and developments
                3. Common themes or differences
                4. Personal growth indicators
                5. Changes in relationships or priorities

                Entry from {one_year_ago.strftime('%B %d, %Y')}:
                {old_note.content}

                Entry from today ({today.strftime('%B %d, %Y')}):
                {today_note.content}

                Important: Always reference the specific year (2023 or 2024) when mentioning events, feelings, or situations from either entry.

                Respond in this exact JSON format:
                {{
                    "emotional_comparison": {{
                        "then": "Description of emotional state in [year]",
                        "now": "Description of current emotional state in [year]",
                        "change": "Analysis of emotional growth from [year] to [year]"
                    }},
                    "life_changes": [
                        "From [year]: Key change or development",
                        "In [year]: Current development"
                    ],
                    "common_themes": [
                        "Theme present in both [year] and [year]"
                    ],
                    "differences": [
                        "In [year]: Notable aspect",
                        "While in [year]: Different aspect"
                    ],
                    "growth_indicators": [
                        "From [year] to [year]: Sign of personal growth"
                    ],
                    "relationship_changes": [
                        "How relationships shifted from [year] to [year]"
                    ]
                }}"""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "system", "content": "You are an insightful journal analyst. Always reference specific years when discussing past events or feelings."},
                        {"role": "user", "content": comparison_prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=800,
                    temperature=0.7
                )
                
                comparison = json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Error generating comparison: {e}")
                comparison = None

        # Generate AI insights for this entry
        try:
            analysis_prompt = f"""Analyze this journal entry from exactly one year ago and provide insights.
            Focus on:
            1. The emotional state and mood
            2. Key events and activities
            3. Important people mentioned and their roles
            4. Main themes or topics
            5. Notable reflections or thoughts

            Journal entry from {one_year_ago.strftime('%B %d, %Y')}:
            Title: {old_note.title}
            Content: {old_note.content}

            Important: Always include the year ({one_year_ago.year}) when mentioning events, feelings, or situations.

            Respond in this exact JSON format:
            {{
                "mood_analysis": {{
                    "mood_state": "Description of emotional state in {one_year_ago.year}",
                    "key_emotions": ["emotion in {one_year_ago.year}", "another emotion"]
                }},
                "key_events": [
                    "In {one_year_ago.year}: Important event or activity",
                    "During {one_year_ago.year}: Another important event"
                ],
                "people": [
                    {{"name": "Name1", "role": "Role/Relationship in {one_year_ago.year}", "context": "How they were mentioned in {one_year_ago.year}"}}
                ],
                "themes": [
                    "Main theme in {one_year_ago.year}",
                    "Another theme from {one_year_ago.year}"
                ],
                "reflections": [
                    "Notable thought from {one_year_ago.year}",
                    "Another reflection from {one_year_ago.year}"
                ]
            }}"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {"role": "system", "content": "You are an insightful journal analyst. Always reference specific years when discussing past events or feelings."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=800,
                temperature=0.7
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            data = {
                'has_entry': True,
                'date': one_year_ago.strftime('%B %d, %Y'),
                'today_date': today.strftime('%B %d, %Y'),
                'note': {
                    'title': old_note.title,
                    'content': old_note.content,
                    'mood_score': old_note.mood_score,
                    'mood_emoji': old_note.get_mood_emoji()
                },
                'today_note': today_note.to_dict() if today_note else None,
                'analysis': analysis,
                'comparison': comparison
            }
            
            return render_template('one_year_ago.html', data=data)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return render_template('one_year_ago.html', data={
                'has_entry': True,
                'date': one_year_ago.strftime('%B %d, %Y'),
                'note': {
                    'title': old_note.title,
                    'content': old_note.content,
                    'mood_score': old_note.mood_score,
                    'mood_emoji': old_note.get_mood_emoji()
                },
                'error': 'Error generating insights'
            })
            
    except Exception as e:
        print(f"Error in one year ago route: {e}")
        return render_template('one_year_ago.html', data={
            'has_entry': False,
            'error': 'Error loading journal entry'
        })

if __name__ == '__main__':
    app.run(debug=True) 