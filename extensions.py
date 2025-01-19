from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
import spacy
import os
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

# Initialize other services
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
nlp = spacy.load('en_core_web_sm') 