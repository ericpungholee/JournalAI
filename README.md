# JournalAI 📝

An intelligent journaling application that combines personal reflection with AI-powered insights. Write, reflect, and gain a deeper understanding of your thoughts and emotions over time.
# Video Demo: https://youtu.be/79aJFVIAwaM
## Features ✨

- **Smart Journaling**: Write daily entries with automatic mood analysis.
- **AI Insights**: Get personalized analysis of your entries using OpenAI's GPT.
- **Time Machine**: Compare entries from one year ago with today.
- **Mood Tracking**: Visualize your emotional journey with interactive charts.
- **Weekly Analysis**: Receive AI-generated summaries of your week.
- **Relationship Insights**: Track mentions and interactions with people in your life.
- **Data Privacy**: All data stored locally in an SQLite database.

## Tech Stack 🛠️

### Frontend
- **HTML5/CSS3**: For structuring and styling the application.
- **Vanilla JavaScript**: For dynamic behaviors and interactivity.
- **Chart.js**: For data visualization.
- **Font Awesome**: For icons.
- **Responsive Design**: Optimized for desktop and mobile.

### Backend
- **Python 3.x**: Core programming language.
- **Flask**: Web framework for handling backend logic.
- **SQLAlchemy**: ORM for database interactions.
- **SQLite**: Lightweight database for storage.
- **OpenAI API**: For AI-driven insights.
- **spaCy**: For natural language processing.

## Getting Started 🚀

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/journal-ai.git
cd journal-ai
```

2. **Create and Activate a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. **Set Up Environment Variables**

Create a `.env` file in the root directory with the following content:

```env
OPENAI_API_KEY=your_openai_api_key
```

5. **Initialize the Database**

```bash
python create_db.py
```

6. **Run the Application**

```bash
python app.py
```

7. **Open Your Browser**

Navigate to `http://localhost:5000` to access the application.

## Usage 📖

1. **Writing Entries**
   - Click "New" to create a new entry.
   - Set the date and title.
   - Write your thoughts.
   - Save automatically or manually.

2. **Viewing Insights**
   - Navigate to "Insights" for mood analysis and trends.
   - View weekly summaries and AI-generated insights.
   - Track relationships and recurring themes.

3. **Time Machine**
   - Visit "One Year Ago" to compare past and present entries.
   - Get AI analysis of your growth and changes.
   - Reflect on your journey.



## Acknowledgments 🙏

- **OpenAI**: For providing the GPT API.
- **spaCy**: For natural language processing capabilities.
- **Chart.js**: For beautiful data visualization.
- **Flask**: For the amazing web framework.

## Screenshots 📸
![image](https://github.com/user-attachments/assets/6656d9f4-f210-4dcd-ac6e-e8d5d7c0d636)
![image](https://github.com/user-attachments/assets/fe08b0f7-7d7b-4afb-9225-a7f3680c5beb)

![image](https://github.com/user-attachments/assets/e6770650-e1da-4d3d-926e-5cd966ce04ce)
![image](https://github.com/user-attachments/assets/db744835-a415-4055-b5ed-31b5eaf67dc3)
![image](https://github.com/user-attachments/assets/c77f8a90-e06c-4481-af08-48a8a81fd026)


## Contact 📧

**Eric Lee**
https://www.linkedin.com/in/eric-lee99999/
eric.pungho.lee@gmail.com
http://www.ericsportfol.io/

